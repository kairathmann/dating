#  -*- coding: UTF8 -*-

from datetime import datetime
from decimal import Decimal

from sys_base.exceptions import HeliosException

from sys_util.math import base58, hash160
from sys_util.math.eth import d8, to_decimal, from_decimal
from sys_util.website.authproxy import AuthServiceProxy


class QtumAdapter(object):
    """
        An adapter class that bridges our Python environment to the QTUM node RPC
    """

    def __init__(self, node_url, contract_address, contract_owner_address, contract_functions,
                 default_gas_limit, default_gas_price):
        """
            Creates a new adapter instance

            :param node_url: url for QTUM node RPC listener
            :param contract_address: deployed contract address on the QTUM network
            :param contract_owner_address: address which tokens will be transferred from
            :param contract_functions: A hash of function name and the hex signature of a function
            :param default_gas_limit: ??
            :param default_gas_price: ??
        """

        self.node = AuthServiceProxy(node_url)

        self.contract_address = contract_address
        self.contract_functions = contract_functions
        self.contract_owner_address = contract_owner_address
        self.default_gas_limit = default_gas_limit
        self.default_gas_price = default_gas_price

    def get_block_count(self):
        """
            Returns the block count for the QTUM node

            :return: (int) the current block count of the QTUM node
        """

        return self.node.getblockcount()

    def current_block_time(self):
        """
            Returns a datetime() object for the most recent block reported by the API
        """

        block_count = self.node.getblockcount()
        block_hash = self.node.getblockhash(block_count)
        time_str = self.node.getblock(block_hash)['time']

        return datetime.fromtimestamp(int(time_str))

    def get_new_address(self):
        """
            Generates a new QTUM address and returns all crypto data necessary to control it

            :return: addr: (string) public QTUM address
            :return: private_key: (string) private key for QTUM address
        """

        addr = self.node.getnewaddress()
        private_key = self.node.dumpprivkey(addr)

        return addr, private_key

    # def parse_transaction(self, tx_id):
    #     """
    #         Fetches and parses a QTUM transaction with id tx_id
    #
    #         :param tx_id: transaction id
    #
    #         :return: dict
    #         {
    #             'txid': u'483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3',
    #             'amount': 3,
    #             'time': 1515070304,
    #             'confirmations': 154,
    #             'address': u'qcagFaZpYNdL5KDPmJPfyyeqWgarQueanA'
    #         }
    #     """
    #
    #     transaction = self.node.getrawtransaction(tx_id, True)
    #
    #     for vout in transaction['vout']:
    #
    #         contract_instructions = vout['scriptPubKey']['asm'].split(' ')
    #
    #         # The 4th element is the actual contract function name
    #         if len(contract_instructions) >= 4:
    #
    #             contract_parameters = contract_instructions[3]
    #
    #             # Check if the transaction has the ERC20 transfer() method
    #             if contract_parameters.startswith(self.contract_functions['transfer']):
    #
    #                 return {
    #
    #                     'address': transaction['vin'][0]['address'],
    #
    #                     # Amount is the last parameter (padding to 64 chars); convert from hex (16) to decimal
    #                     'amount': int(contract_parameters[-64:], 16),
    #
    #                     'time': transaction['time'],
    #                     'confirmations': transaction['confirmations'],
    #                     'txid': transaction['txid']
    #                 }
    #
    #     raise Exception('Invalid Transaction')

    # def get_transactions(self, address):
    #     """
    #         Returns a list of transactions for a given address
    #
    #         :param address: The wallet address
    #         :return: list of transaction dicts
    #     """
    #
    #     transaction_ids = self.node.getaddresstxids({'addresses': [address]})
    #
    #     return [self.parse_transaction(tx_id) for tx_id in transaction_ids]

    def get_balance(self, address):
        """
            Returns the balance for a given QTUM address
            This calls an ERC-20 compliant smart contract get_balance() method

            :param address: wallet address
            :return: (int) current balance
        """

        # QTUM switches between uppercase and lowercase 'q' depending on whether the address is on the testnet
        # or mainnet (which is a stupid thing to do as it makes tests done in the testnet INVALID)

        if address[0] not in ['Q', 'q']:
            raise HeliosException(desc='Invalid QTUM address', code='invalid_address')

        # The Ethereum spec requires us to pad the address to 64 bytes
        address_to = hash160.hash160(base58.b58decode(bytes(address))).rjust(64, '0')

        function_params = self.contract_functions['balance_of'] + address_to
        result = self.node.callcontract(self.contract_address, function_params)

        # Convert the returned amount from hex (16) to decimal
        confirmed_bal_long = Decimal(int(result['executionResult']['output'], 16))

        confirmed_bal = to_decimal(confirmed_bal_long)

        # Placeholder data until RPC code is updated
        unconfirmed_bal = d8(17.0380000012840004124)

        return confirmed_bal, unconfirmed_bal

    def send_to_address(self, address, amount):
        """
            Sends an amount of QTUM (which is DIFFERENT than our token) to a given address. This method
            is used to provide 'gas' to an address to facilitate moving tokens.

            :param address: QTUM address to send the QTUM to
            :param amount: number of QTUM to send
            :return: (object) including the txid
        """

        # QTUM switches between uppercase and lowercase 'q' depending on whether the address is on the testnet
        # or mainnet (which is a stupid thing to do as it makes tests done in the testnet INVALID)

        if address[0] not in ['Q', 'q']:
            raise HeliosException(desc='Invalid QTUM address', code='invalid_address')

        return self.node.sendtoaddress(address, amount)

    def list_unspent(self, address, min_confirmations=1, max_confirmations=9999999):
        """
            Returns array of unspent transaction outputs
            with between min_confirmations and max_confirmations (inclusive) confirmations.
            Filter only specified address.

            We use this function to know if a user has any Gas / QTUM / UTXO associated with this address

            :param address: (string) QTUM addresses to filter
            :param min_confirmations: (numeric, optional, default=1) The minimum confirmations to filter
            :param max_confirmations: (numeric, optional, default=9999999) The maximum confirmations to filter
            :return: (array of json object)
            {
                "txid" : "txid",          (string) the transaction id
                "vout" : n,               (numeric) the vout value
                "address" : "address",    (string) the qtum address
                "account" : "account",    (string) DEPRECATED. The associated account, or "" for the default account
                "scriptPubKey" : "key",   (string) the script key
                "amount" : x.xxx,         (numeric) the transaction output amount in QTUM
                "confirmations" : n,      (numeric) The number of confirmations
                "redeemScript" : n        (string) The redeemScript if scriptPubKey is P2SH
                "spendable" : xxx,        (bool) Whether we have the private keys to spend this output
                "solvable" : xxx          (bool) Whether we know how to spend this output, ignoring the lack of keys
              }
        """

        # QTUM switches between uppercase and lowercase 'q' depending on whether the address is on the testnet
        # or mainnet (which is a stupid thing to do as it makes tests done in the testnet INVALID)

        if address[0] not in ['Q', 'q']:
            raise HeliosException(desc='Invalid QTUM address', code='invalid_address')

        return self.node.listunspent(int(min_confirmations), int(max_confirmations), [address])

    def transfer(self, source_addr, source_private_key, dest_addr, amount):
        """
            Transfers tokens from source_addr to dest_addr
            This calls an ERC-20 compliant smart contract transfer() method

            :param source_addr: QTUM address within source wallet to use
            :param source_private_key: private key for source wallet
            :param dest_addr: QTUM address to transfer the tokens to
            :param amount: number of tokens to transfer.
        """

        # QTUM switches between uppercase and lowercase 'q' depending on whether the address is on the testnet
        # or mainnet (which is a stupid thing to do as it makes tests done in the testnet INVALID)

        if source_addr[0] not in ['Q', 'q']:
            raise HeliosException(desc='Invalid source QTUM address', code='invalid_source_address')

        if dest_addr[0] not in ['Q', 'q']:
            raise HeliosException(desc='Invalid dest QTUM address', code='invalid_dest_address')

        # Ethereum spec require us to 64 pad the address to
        address_to = hash160.hash160(base58.b58decode(bytes(dest_addr))).rjust(64, '0')

        # Convert amount to smart contract decimal system
        decimal_amount = from_decimal(amount)
        return self.node.sendtocontract(

            self.contract_address,

            # Convert amount from decimal to hex without the '0x'
            self.contract_functions['transfer'] + address_to + hex(decimal_amount)[2:].rjust(64, '0'),

            0,
            self.default_gas_limit,
            self.default_gas_price,
            source_addr
        )
