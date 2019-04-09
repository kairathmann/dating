#  -*- coding: UTF8 -*-

import sys, logging, os

import settings
from plant_hermes.qtum.adapter import QtumAdapter
from sys_util.text.pprint import print_error, print_info, print_spaceship, print_success, print_warn

logging.basicConfig(

    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Change to 'logging.DEBUG' to get debug information
)

CONTRACT_FUNCTIONS = {

    # Function signatures for the deployed ERC20 token; a hex calculated from the function name + argument types
    # See: https://digixglobal.github.io/etc-redemption/docs/ERC20/

    'balance_of': 'TBD',
    'transfer': 'TBD'
}

DEFAULT_GAS_LIMIT = 250000
DEFAULT_GAS_PRICE = 0.0000004

NODE_URL = settings.QTUM_RPC

# This can be overwritten by the --mainnet flag
RUNNING_ON_PROD = settings.RUNNING_ON_PROD

# This can be overwritten by the --mainnet flag
CONTRACT_ADDRESS = settings.QTUM_CONTRACT_ADDRESS
# This can be overwritten by the --mainnet flag
CONTRACT_OWNER_ADDRESS = settings.QTUM_CONTRACT_OWNER_ADDRESS


def run_command(adapter, cli_args):
    command = cli_args[1]

    if command == 'ping':

        print_success('Ping successful. Block count is {}'.format(adapter.get_block_count()))

    elif command == 'newaddress':

        print_success(adapter.get_new_address())

    elif command == 'gettransactions':

        if len(cli_args) < 3:
            print_error('Please supply a wallet address')

        else:
            print_success(adapter.get_transactions(cli_args[2]))

    elif command == 'getbalanceof':

        if len(cli_args) < 3:
            print_error('Please supply a wallet address')

        else:
            print_success(adapter.get_balance(cli_args[2]))

    elif command == 'transfer':

        if len(cli_args) < 5:
            return print_error('Please supply a target wallet address, amount and source wallet address')

        else:
            result = adapter.transfer(cli_args[2], None, cli_args[3], cli_args[4])
            print_success(result)
            if RUNNING_ON_PROD:
                print_success('You can check the tx id at https://explorer.qtum.org/tx/{}'.format(result['txid']))
                print_success('Or you can check here https://qtumexplorer.io/tx/{}'.format(result['txid']))
                return
            else:
                return print_success('You can check the tx id at https://testnet.qtum.org/tx/{}'.format(result['txid']))


    elif command == 'sendtoaddress':

        if len(cli_args) < 4:
            return print_error('Please supply a target wallet address and amount')

        else:
            print_success(adapter.send_to_address(cli_args[2], cli_args[3]))

    elif command == 'listunspent':

        if len(cli_args) < 5:
            return print_error('Please supply a target wallet address, minimum confirmation, max confirmation')

        else:
            print_success(adapter.list_unspent(cli_args[2], cli_args[3], cli_args[4]))

    else:

        print_error('Invalid command\n')
        print_help()


def print_help():
    print_spaceship()

    print_info('Hermes can run with the following args:')
    print_info('python hermes.py COMMAND')
    print_warn('ping - Returns the amount of blocks in the node')
    print_warn('newaddress - Creates a new address')
    # TODO: disabled till we get the bitcore node fork for QTUM binary
    # print_warn('gettransactions walletAddress - Get transactions for a given wallet address')
    print_warn('getbalanceof walletAddress - Get the balance of a specific hex wallet address'
               '[Calling ERC-20 contract transfer function]')
    print_warn(
        'transfer fromWalletAddress toWalletAddress amount - Transfer given amount of tokens (Not QTUM) to a wallet'
        '[Calling ERC-20 contract transfer function]')
    print_warn('sendtoaddress toWalletAddress amount - Sends a given amount of QTUM to a wallet.')
    print_warn(
        'listunspent toWalletAddress minConfirmation maxConfirmation - Returns array of unspent transaction outputs - UXTO')


# ==========================================================================================


if __name__ == '__main__':

    if len(sys.argv) < 2 or \
        ((sys.argv[1].startswith('-') and len(sys.argv) < 3)):

        print_help()

    else:

        if not NODE_URL:
            print_error('Please set QTUM_RPC settings variable as user:pass@host:port')
            raise Exception('Please set QTUM_RPC settings variable')

        if sys.argv[1] == '--mainnet' or sys.argv[1] == '-m':
            RUNNING_ON_PROD = True
            sys.argv.pop(0)
            CONTRACT_ADDRESS = settings.QTUM_MAINNET_CONTRACT_ADDRESS
            CONTRACT_OWNER_ADDRESS = settings.QTUM_MAINNET_CONTRACT_OWNER_ADDRESS

        if RUNNING_ON_PROD:
            print_warn('Running on production - Mainnet!')
        else:
            print_warn('Running on development - Testnet!')

        adapter_instance = QtumAdapter(

            node_url=NODE_URL,
            contract_address=CONTRACT_ADDRESS,
            contract_owner_address=CONTRACT_OWNER_ADDRESS,
            contract_functions=CONTRACT_FUNCTIONS,
            default_gas_limit=DEFAULT_GAS_LIMIT,
            default_gas_price=DEFAULT_GAS_PRICE
        )

        run_command(adapter_instance, sys.argv)
