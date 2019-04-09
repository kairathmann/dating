#  -*- coding: UTF8 -*-

# To test hermes integration navigate to root directory and run `python test_integration.py`

import time
from sys_util.text.pprint import *

from plant_hermes.adapter import QtumAdapter
from hermes import CONTRACT_FUNCTIONS, DEFAULT_GAS_LIMIT, \
    DEFAULT_GAS_PRICE, CONTRACT_ADDRESS, CONTRACT_OWNER_ADDRESS, NODE_URL

TRANSFER_FROM_ADDRESS = CONTRACT_OWNER_ADDRESS


class HermesIntegrationTest(object):
    """
        Integration test class used to test transferring tokens.
        In order to move tokens, We need to use an address who already have tokens.
        In order for that to happen we need to move them from an address with tokens
        and QTUM (For the gas)
        Follow hermes.md and Import the test wallet as this has the CONTRACT_OWNER_ADDRESS private key
        And have actual tokens for the deployed test contract hermes is using

        1.If more QTUM is needed. Then navigate to the test faucet to get tokens http://testnet-faucet.qtum.info
        make sure you use qNh2o4R8DpvmhnL45QWqegzHRyKeNgWT13
        2.If the script wont run because of missing uxto - Please run
        cd /srv/luna/qtum/bin/
        ./qcli sendtoaddress qNh2o4R8DpvmhnL45QWqegzHRyKeNgWT13 5
    """

    def __init__(self):
        self.adapter_instance = QtumAdapter(

            node_url=NODE_URL,
            contract_address=CONTRACT_ADDRESS,
            contract_owner_address=CONTRACT_OWNER_ADDRESS,
            contract_functions=CONTRACT_FUNCTIONS,
            default_gas_limit=DEFAULT_GAS_LIMIT,
            default_gas_price=DEFAULT_GAS_PRICE
        )

    def main(self):
        target_address = self.adapter_instance.get_new_address()
        print_success('Created {}'.format(target_address))
        result = self.adapter_instance.transfer(target_address, 1, TRANSFER_FROM_ADDRESS)
        print_info(result)
        print_success('You can check the transaction above here')
        print_success('https://testnet.qtum.org/tx/{}'.format(result.get('txid')))
        print_success(
            'You can also wait 2 minutes and then check if this returns 1 - python hermes.py getbalanceof {}'.format(
                target_address))
