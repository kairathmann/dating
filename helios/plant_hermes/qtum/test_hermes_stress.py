#  -*- coding: UTF8 -*-

import time
from sys_util.text.pprint import *

from plant_hermes.adapter import QtumAdapter

from hermes import CONTRACT_FUNCTIONS, DEFAULT_GAS_LIMIT, DEFAULT_GAS_PRICE
from hermes import CONTRACT_ADDRESS, CONTRACT_OWNER_ADDRESS, NODE_URL


class HermesStressTest(object):
    """
        NOTE: To test hermes stress navigate to root directory and run `python test_integration.py`

        Stress test hermes by:
        1.Calls get_new_address
        2.Use the test faucet to get tokens to that address testnet-faucet.qtum.info
        3.Replace this variable with the address you have
        4.Replace the following with your address -
        cd /srv/luna/qtum/bin/
        ./qcli sendtoaddress qJtBAKSm1Ew7ViWSNauGoqb6Ka2T1yZc8j 1
    """

    TRANSFER_FROM_ADDRESS = 'qJtBAKSm1Ew7ViWSNauGoqb6Ka2T1yZc8j'

    def __init__(self):
        self.adapter_instance = QtumAdapter(

            node_url=NODE_URL,
            contract_address=CONTRACT_ADDRESS,
            contract_owner_address=CONTRACT_OWNER_ADDRESS,
            contract_functions=CONTRACT_FUNCTIONS,
            default_gas_limit=DEFAULT_GAS_LIMIT,
            default_gas_price=DEFAULT_GAS_PRICE
        )

        # Increase this number to check performance settings
        self.stress_test_addresses = 3

    def main(self):
        """

        """
        addresses = self.stresstest_new_address()
        results = self.stresstest_transfer(addresses)

        print_info(results)

        results = self.stresstest_get_transactions(addresses)

        print_info(results)

    def stresstest_new_address(self):
        """
            :return:
        """

        num_of_addresses = self.stress_test_addresses

        start = time.time()

        print_info('About to create {} addresses...'.format(num_of_addresses))

        result = [str(self.adapter_instance.get_new_address()) for i in range(num_of_addresses)]

        total = time.time() - start

        print_info('Finished in {} seconds'.format(total))
        print_success(result)

        return result

    def stresstest_transfer(self, addresses):
        """

            :param addresses:
            :return:
        """

        start = time.time()
        print_info('About to transfer {} transactions...'.format(len(addresses)))

        result = [self.adapter_instance.transfer(address, 1, self.TRANSFER_FROM_ADDRESS) for address in addresses]

        total = time.time() - start

        print_info('Finished in {} seconds'.format(total))
        print_success(result)

        return result

    def stresstest_get_transactions(self, addresses):
        """

            :param addresses:
            :return:
        """

        start = time.time()
        print_info('About to get {} transactions...'.format(len(addresses)))

        result = [self.adapter_instance.get_transactions(address) for address in addresses]

        total = time.time() - start

        print_info('Finished in {} seconds'.format(total))
        print_success(result)

        return result
