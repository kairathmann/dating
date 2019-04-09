import unittest
import json
from plant_hermes.adapter import QtumAdapter
from hermes import CONTRACT_FUNCTIONS, DEFAULT_GAS_LIMIT, \
    DEFAULT_GAS_PRICE, CONTRACT_ADDRESS, CONTRACT_OWNER_ADDRESS, NODE_URL
from mock import MagicMock
from sys_util.website.authproxy import AuthServiceProxy

mock_results = {
    'getaddresstxids':
        ['483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3'],

    'getrawtransaction':
        json.loads(
            '{"blockhash": "94eab436bce8d075ab1d64688a83b343b90e258d7e2d3acd8df69d5bbb16e037", "vout": [{"valueSat": 0, "scriptPubKey": {"reqSigs": 1, "hex": "01040390d003012844a9059cbb000000000000000000000000384af5a9d74d3c9d40c9e554ef5b937c3af6dbbd00000000000000000000000000000000000000000000000000000000000000031490a17d8a35309c644f41076dd8f6acff97f0d136c2", "addresses": ["qWk7vCnBpG3VM6ccLgf9PEvdKbcdvaEcND"], "asm": "4 250000 40 a9059cbb000000000000000000000000384af5a9d74d3c9d40c9e554ef5b937c3af6dbbd0000000000000000000000000000000000000000000000000000000000000003 90a17d8a35309c644f41076dd8f6acff97f0d136 OP_CALL", "type": "call"}, "value": "0E-8", "n": 0}, {"spentIndex": 20, "spentHeight": 62266, "value": "0.89880000", "n": 1, "valueSat": 89880000, "spentTxId": "a5c97bef9cd6525547356b55fbe91185e92ae329ae787385a2fad800466e30c2", "scriptPubKey": {"reqSigs": 1, "hex": "76a914d0a9139b7a42a2731088c29c6d7fb90cc099a1cd88ac", "addresses": ["qcagFaZpYNdL5KDPmJPfyyeqWgarQueanA"], "asm": "OP_DUP OP_HASH160 d0a9139b7a42a2731088c29c6d7fb90cc099a1cd OP_EQUALVERIFY OP_CHECKSIG", "type": "pubkeyhash"}}], "hex": "0200000001f9a549e83644b2ad40bacd7853dde3ff6a31a9794a3efbfca4c783b307a311b5000000006a47304402200696edb2c58ba3226438ab558aa6a56d3f7a9188b4b925a3019822a94304a49102200ca055af593357e337f2bbbbff2fdb0ec2826f639cf5ff28d1ca5cd45357a8ae012103ab323076a4869deb1ce54a5e298b75a8e95457e2744d7ba555cceca6df37054afeffffff0200000000000000006301040390d003012844a9059cbb000000000000000000000000384af5a9d74d3c9d40c9e554ef5b937c3af6dbbd00000000000000000000000000000000000000000000000000000000000000031490a17d8a35309c644f41076dd8f6acff97f0d136c2c0755b05000000001976a914d0a9139b7a42a2731088c29c6d7fb90cc099a1cd88ac38f30000", "vin": [{"scriptSig": {"hex": "47304402200696edb2c58ba3226438ab558aa6a56d3f7a9188b4b925a3019822a94304a49102200ca055af593357e337f2bbbbff2fdb0ec2826f639cf5ff28d1ca5cd45357a8ae012103ab323076a4869deb1ce54a5e298b75a8e95457e2744d7ba555cceca6df37054a", "asm": "304402200696edb2c58ba3226438ab558aa6a56d3f7a9188b4b925a3019822a94304a49102200ca055af593357e337f2bbbbff2fdb0ec2826f639cf5ff28d1ca5cd45357a8ae[ALL] 03ab323076a4869deb1ce54a5e298b75a8e95457e2744d7ba555cceca6df37054a"}, "vout": 0, "sequence": 4294967294, "value": "1.00000000", "txid": "b511a307b383c7a4fcfb3e4a79a9316affe3dd5378cdba40adb24436e849a5f9", "address": "qcagFaZpYNdL5KDPmJPfyyeqWgarQueanA", "valueSat": 100000000}], "txid": "483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3", "blocktime": 1515070304, "version": 2, "confirmations": 154, "time": 1515070304, "locktime": 62264, "height": 62265, "size": 299}')
}

mocked_address = 'qcagFaZpYNdL5KDPmJPfyyeqWgarQueanA'
real_result = "[{'txid': u'483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3', 'amount': 3, 'time': 1515070304, 'confirmations': 154, 'address': u'qcagFaZpYNdL5KDPmJPfyyeqWgarQueanA'}]"


class GetTransactionsTest(unittest.TestCase):
    def init(self):
        self.adapter_instance = QtumAdapter(

            node_url=NODE_URL,
            contract_address=CONTRACT_ADDRESS,
            contract_owner_address=CONTRACT_OWNER_ADDRESS,
            contract_functions=CONTRACT_FUNCTIONS,
            default_gas_limit=DEFAULT_GAS_LIMIT,
            default_gas_price=DEFAULT_GAS_PRICE
        )

    def test_get_transactions(self):
        self.init()
        self.adapter_instance.node = AuthServiceProxy('http://test:test@localhost:1337'),
        self.adapter_instance.node.getaddresstxids = MagicMock(return_value=mock_results.get('getaddresstxids'))
        self.adapter_instance.node.getrawtransaction = MagicMock(return_value=mock_results.get('getrawtransaction'))

        result = self.adapter_instance.get_transactions(mocked_address)
        self.assertEqual(str(result), real_result)
