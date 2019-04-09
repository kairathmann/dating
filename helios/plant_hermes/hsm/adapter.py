#  -*- coding: UTF8 -*-

import os
import base64, hashlib, json

from Crypto import Random
from Crypto.Cipher import AES

from datetime import datetime, timedelta

from django.conf import settings

from plant_hermes.qtum.adapter import QtumAdapter

from sys_base.exceptions import HeliosException

from sys_util.math.eth import d8


class HSMadapter(object):
    """
        Simulates a Hardware Security Module

        ### IN PRODUCTION, ALL FUNCTIONS BELOW WILL RUN INSIDE THE HSM'S CRYPTOGRAPHIC PROCESSOR ###
    """

    # These secrets are stored inside the Hardware Security Module's protected memory. For the MVP,
    # we'll store this as a JSON blob encrypted with a symmetric key, and decrypt it into memory
    # when launching the Luna app
    # ===================================================================================================

    HSM_CONFIG = {

        'MIN_CONFIRMATIONS': 10,

        # Maximum lag allowed between system time and next expected block time before the HSM
        # refuses to sign QTUM transactions

        'MAX_BLOCK_LAG': 30
    }

    # Random strings for keys are generated using "print base64.b64encode(Random.new().read(64))"
    # where "64" is the number of BYTES in the key. 64 bytes = 512 bits

    HSM_SECRETS = {

        'CONTRACT_FUNCTIONS': {

            # Function signatures for the deployed ERC20 token; a hex calculated from the function name + argument types
            # See: https://digixglobal.github.io/etc-redemption/docs/ERC20/

            'balance_of': 'TBD',
            'transfer': 'TBD'
        },

        'DEFAULT_GAS_LIMIT': 250000,
        'DEFAULT_GAS_PRICE': 0.0000004,

        # Initial gas we load each new receiving address with - around 12 cents (for QTUM @ 40$)
        'PRELOAD_GAS': 0.003,  # TODO - check if can optimize for lower

        # ------------------------------------------------------------------------

        # Cold wallet address that we send tokens into
        'COLD_ADDRESS': 'TBD',

        # ------------------------------------------------------------------------

        # Master key that our hot wallet QTUM keys are derived from
        'HOT_MASTER_KEY': 'TBD',

        # Hot wallet address that we send tokens from
        'HOT_ADDRESS': 'TBD',

        # Private key hot wallet address that we send tokens from
        'HOT_PRIVATE_KEY': 'TBD',

        # ------------------------------------------------------------------------

        # [BASE64] Master key that user QTUM wallet keys are derived from
        'ENCLAVE_MASTER_KEY': 'TBD',

        # [BASE64] Symmetric AES key used to encrypt/decrypt the enclave dicts used to store user wallet crypto secrets
        'ENCLAVE_AES_KEY': 'TBD',

        # [BASE64] 256-bit symmetric AES key used to encrypt/decrypt record data blobs
        'POLICY_AES_KEY': 'TBD',

        # [BASE64] 512-bit salt value used to calculate record signature hashes
        'RECORD_SIG_SALT': os.environ.get('RECORD_SIG_SALT'),

        # ------------------------------------------------------------------------

        'SENDGRID_API_SEND_KEY': os.environ.get('LUNA_SENDGRID_API_SEND_KEY')
    }

    # ===================================================================================================

    def __init__(self):
        """
            Creates a new adapter instance
        """

        self.qtum_node = QtumAdapter(

            node_url=settings.QTUM_RPC,
            contract_address=settings.QTUM_CONTRACT_ADDRESS,
            contract_owner_address=settings.QTUM_CONTRACT_OWNER_ADDRESS,
            contract_functions=self.HSM_SECRETS['CONTRACT_FUNCTIONS'],
            default_gas_limit=self.HSM_SECRETS['DEFAULT_GAS_LIMIT'],
            default_gas_price=self.HSM_SECRETS['DEFAULT_GAS_PRICE']
        )

    def node_is_synced(self):
        """
            Checks if the local QTUM node is in sync with the blockchain

            :return: True if synced to the blockchain, otherwise False
        """

        max_block_lag = timedelta(seconds=int(self.HSM_CONFIG['MAX_BLOCK_LAG']))
        qtum_block_time = timedelta(seconds=180)

        if datetime.now() > (self.qtum_node.current_block_time() + max_block_lag + qtum_block_time):

            return False

        else:
            return True

    def generate_enclave_address(self):
        """
            Generates a new QTUM address

            :return: new_addr: public qtum address that a user can send tokens to
            :return: data_iv: base64 encoded AES iv used to encrypt enclave_data and policy_data
            :return: enclave_data: AES encrypted dict of secrets used to control this enclave address
            :return: initial_policy_data: empty AES encrypted dict of policy data for this enclave address
        """

        # NOTE: generating keypairs doesn't require the node to be in sync with the blockchain
        # ------------------------------------------------------------------------------------

        # Generate a new QTUM address and private key
        new_addr, private_key = self.qtum_node.get_new_address()

        # In order for AES to be secure, we have to generate a new IV for EVERY record. We ALWAYS
        # handle iv's and keys in base64 encoded form, as the byte form isn't viewable in normal
        # editors and the hex form takes up too much space

        data_iv = Random.new().read(AES.block_size)

        # Serialize and encrypt the address data dict

        aes = AESCipher()

        enclave_data = aes.encrypt(

            key=base64.b64decode(self.HSM_SECRETS['ENCLAVE_AES_KEY']),
            iv=data_iv,

            plaintext=json.dumps({

                # We duplicate 'enclave_addr' in the addr_data blob as an additional security measure
                'enclave_addr': str(new_addr),
                'private_key': str(private_key)
            })
        )

        # Create an empty policy_data blob for future entries to be added to

        initial_policy_data = aes.encrypt(

            key=base64.b64decode(self.HSM_SECRETS['POLICY_AES_KEY']),
            iv=data_iv,
            plaintext=json.dumps([])
        )

        return new_addr, data_iv, enclave_data, initial_policy_data

    def sweep_enclave_address(self, data_iv, enclave_data):
        """
            Transfers the entire balance of an enclave address into our cold storage address. This HAS to
            be implemented inside the HSM to prevent an attacker from tampering with our code and changing
            the receiving QTUM address to an address which they control

            :param data_iv: iv used to encrypt enclave_data and policy_data
            :param enclave_data: AES encrypted dict of secrets used to control this enclave address

            :return: tokens_swept: value of tokens transferred from enclave address
            :return: unconfirmed_bal: value of unconfirmed tokens remaining in enclave address
            :return: txid: base64 txid of transaction that transferred the tokens
        """

        if not self.node_is_synced():
            raise HeliosException(desc='Node not synced', code='node_not_synced')

        # Decrypt the QTUM address data and loft it back into a dict

        aes = AESCipher()

        enclave = json.loads(aes.decrypt(

            key=base64.b64decode(self.HSM_SECRETS['ENCLAVE_AES_KEY']),
            iv=data_iv,
            ciphertext=enclave_data
        ))

        # Get the total balance of the address so we can completely empty it
        confirmed_bal, unconfirmed_bal = self.qtum_node.get_balance(enclave['enclave_addr'])

        if confirmed_bal <= d8(0.0):

            return d8(0.0), unconfirmed_bal, None

        else:

            # Before transferring from an address, we need to check that there is sufficient UTXO (Gas/QTUM)
            # in that address to fund the transaction.
            #
            # It's important we limit how often we transfer-in gas, otherwise an attacker could create an
            # amplification attack whereby they make millions of tiny deposits to the address while
            # we keep adding 12 cents worth of QTUM for each deposit. They wouldn't be able to get the
            # gas out of the address, but it could burn significant resources on our end.

            if len(self.qtum_node.list_unspent(enclave['enclave_addr'])) <= 0:
                self.qtum_node.send_to_address(enclave['enclave_addr'], self.HSM_SECRETS['PRELOAD_GAS'])

                # TODO: it might be necessary to wait a block between transferring the gas into the
                # TODO: address and running the sweep transaction

            transfer_response = self.qtum_node.transfer(

                source_addr=enclave['enclave_addr'],
                source_private_key=enclave['private_key'],
                dest_addr=settings.QTUM_CONTRACT_OWNER_ADDRESS,

                # Transfer the entire wallet balance
                amount=confirmed_bal
            )

            txid = transfer_response.get('txid')

            return confirmed_bal, unconfirmed_bal, txid

    def transfer_to_sovereign_address(self, data_iv, policy_data, dest_addr, amount):
        """
            Transfers tokens from our hot wallet to the specified sovereign address. Sovereign addresses are
            QTUM addresses outside of our platform that we don't control

            :param data_iv: initialization vector for AES block cipher
            :param policy_data: encrypted policy data blob
            :param dest_addr: qtum address to transfer the tokens to
            :param amount: amount of tokens to transfer

            :return: txid: qtum network txid
            :return: updated_policy_data: updated policy data to store to the user's TokenAccount record
        """

        if not self.node_is_synced():
            raise HeliosException(desc='Node not synced', code='node_not_synced')

        # Decrypt the machine learning algorithm data for this user's record

        aes = AESCipher()

        cleartext_policy_data_unparsed = aes.decrypt(

            key=base64.b64decode(self.HSM_SECRETS['ENCLAVE_AES_KEY']),
            iv=data_iv,
            ciphertext=policy_data
        )

        if cleartext_policy_data_unparsed:
            cleartext_policy_data = json.loads(cleartext_policy_data_unparsed)
        else:
            cleartext_policy_data = []

        # TODO: ENFORCE ACTUAL POLICY USING MACHINE LEARNING ALGORITHM HERE

        if len(self.qtum_node.list_unspent(self.HSM_SECRETS['HOT_ADDRESS'])) <= 0:
            self.qtum_node.send_to_address(self.HSM_SECRETS['HOT_ADDRESS'], self.HSM_SECRETS['PRELOAD_GAS'])

            # TODO: it might be necessary to wait a block between transfering the gas into the
            # TODO: address and running the sweep transaction

        transfer_response = self.qtum_node.transfer(

            source_addr=self.HSM_SECRETS['HOT_ADDRESS'],
            source_private_key=self.HSM_SECRETS['HOT_PRIVATE_KEY'],
            dest_addr=dest_addr,
            amount=amount
        )

        txid = transfer_response.get('txid')

        updated_policy_data = aes.encrypt(

            key=base64.b64decode(self.HSM_SECRETS['POLICY_AES_KEY']),
            iv=data_iv,
            plaintext=json.dumps(cleartext_policy_data.append({

                'timestamp': datetime.now(),
                'txid': str(txid),
                'dest_addr': str(dest_addr),
                'amount': str(d8(amount))
            }))
        )

        return txid, updated_policy_data

    @classmethod
    def sign_record(cls, plaintext):
        """
            Generates the 'hsm_sig' value for a HSM-protected Luna platform record

            :param plaintext: contents of all HSM-protected record fields, concatenated into a string
            :return: base64 encoded sha512 hash value (calculated using secret salt stored in HSM)
        """

        salted = hashlib.sha512(plaintext).digest() + base64.b64decode(cls.HSM_SECRETS['RECORD_SIG_SALT'])

        return hashlib.sha512(salted).digest()

    @classmethod
    def verify_record_sig(cls, hsm_sig, plaintext):
        """
            Verifies a HSM-protected Luna platform record

            :param plaintext: contents of all HSM-protected record fields, concatenated into a string
            :param hsm_sig: value of hsm_sig field

            :return: True if hsm_sig is valid, otherwise False
        """

        salted = hashlib.sha512(plaintext).digest() + base64.b64decode(cls.HSM_SECRETS['RECORD_SIG_SALT'])
        calc_sig = hashlib.sha512(salted).digest()

        return bool(str(hsm_sig) == str(calc_sig))


class AESCipher(object):
    """
        A wraper class for Python's built-in AES cypher library. Note that 'key' and 'iv' args are in base64
        encoded form NOT binary to make them easier to work with as strings in IDE's
    """

    def encrypt(self, key, iv, plaintext):
        cipher = AES.new(key, AES.MODE_CBC, iv)

        return cipher.encrypt(self.pad(plaintext))

    def decrypt(self, key, iv, ciphertext):
        cipher = AES.new(key, AES.MODE_CBC, iv)

        return self.unpad(cipher.decrypt(ciphertext)).decode('utf-8')

    def pad(self, s):
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    def unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]
