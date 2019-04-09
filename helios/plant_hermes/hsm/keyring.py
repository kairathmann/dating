#  -*- coding: UTF8 -*-

import os
from Crypto.Cipher import AES


class HSMkeyring(object):
    """
        Simulates a Hardware Security Module Keyring

        ### IN PRODUCTION, ALL FUNCTIONS BELOW WILL RUN INSIDE THE HSM'S CRYPTOGRAPHIC PROCESSOR ###
    """

    # Random strings for keys are generated using "print base64.b64encode(Random.new().read(64))"
    # where "64" is the number of BYTES in the key. 64 bytes = 512 bits

    KEYRING = {

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

        # Deployed contract address on the QTUM network
        'CONTRACT_ADDRESS': 'TBD',

        # Address which money will be transferred from
        'CONTRACT_OWNER_ADDRESS': 'TBD',

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

        'SENDGRID_API_SEND_KEY': os.environ.get('LUNA_SENDGRID_API_SEND_KEY'),

        'DATABASES': {

            'default': {

                'ENGINE': os.environ.get('LUNA_DB_ENGINE'),
                'NAME': os.environ.get('POSTGRES_DB'),
                'USER': os.environ.get('POSTGRES_USER'),
                'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
                'HOST': os.environ.get('POSTGRES_HOST'),
                'PORT': os.environ.get('POSTGRES_PORT'),
                'CONN_MAX_AGE': 600
            },

            'worker_pool': {

                'ENGINE': os.environ.get('LUNA_DB_ENGINE'),
                'NAME': os.environ.get('POSTGRES_DB'),
                'USER': os.environ.get('POSTGRES_USER'),
                'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
                'HOST': os.environ.get('POSTGRES_HOST'),
                'PORT': os.environ.get('POSTGRES_PORT'),
                'CONN_MAX_AGE': 600
            }
        }
    }

    # ===================================================================================================

    def __init__(self, master_key):
        """
            Creates a new adapter instance
        """

        self.master_key = master_key

    def get_key(self, keyname):
        """
            Creates a new adapter instance
        """

        return self.KEYRING[keyname]
