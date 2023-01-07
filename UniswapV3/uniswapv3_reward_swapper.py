from defi_protocols.functions import get_symbol, balance_of, get_node
from defi_protocols.constants import USDC_ETH, DAI_ETH, WETH_ETH, ETHEREUM
from txn_uniswapv3_helpers import COMP, AAVE, RETH2, SWISE, SETH2, bcolors, swap_selected_token, json_file_download, restart_end
from datetime import datetime
import math


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
REWARDS_TOKENS = [COMP, AAVE, RETH2, SWISE]

PATHS = {
    COMP: {
        USDC_ETH: [COMP, WETH_ETH, USDC_ETH],
        DAI_ETH: [COMP, WETH_ETH, DAI_ETH],
        WETH_ETH: [COMP, WETH_ETH]
    },
    AAVE: {
        USDC_ETH: [AAVE, WETH_ETH, USDC_ETH],
        DAI_ETH: [AAVE, WETH_ETH, DAI_ETH],
        WETH_ETH: [AAVE, WETH_ETH]
    },
    RETH2: {
        USDC_ETH: [RETH2, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [RETH2, SETH2, WETH_ETH, DAI_ETH],
        WETH_ETH: [RETH2, WETH_ETH]
    },
    SWISE: {
        USDC_ETH: [SWISE, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [SWISE, SETH2, WETH_ETH, DAI_ETH],
        WETH_ETH: [SWISE, WETH_ETH]
    }
}



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Reward Swapper ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------------{bcolors.ENDC}")
print()

avatar_address = input('Enter the Avatar Safe address: ')
while not web3.isAddress(avatar_address):
    avatar_address = input('Enter a valid address: ')

avatar_address = web3.toChecksumAddress(avatar_address)
print()

roles_mod_address = input('Enter the Roles Module address: ')
while not web3.isAddress(roles_mod_address):
    roles_mod_address = input('Enter a valid address: ')

roles_mod_address = web3.toChecksumAddress(roles_mod_address)
print()

json_file = {
    'version': '1.0',
    'chainId': '1',
    'meta': {
        'name': None,
        'description': '',
        'txBuilderVersion': '1.8.0'
    },
    'createdAt': math.floor(datetime.now().timestamp()*1000),
    'transactions': []
}

while True:
    for reward_token in REWARDS_TOKENS:
        token_symbol = get_symbol(reward_token, ETHEREUM, web3=web3)
        token_balance = balance_of(avatar_address, reward_token, 'latest', ETHEREUM, web3=web3)
        message = 'Reward Token: %s\nBalance: %f' % (token_symbol, token_balance)
        print(f"{bcolors.OKBLUE}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()

        if token_balance == 0:
            continue
        
        print('Select the action to execute with the balance of %s: ' % token_symbol)
        print('1- Swap it for USDC')
        print('2- Swap it for DAI')
        print('3- Swap it for WETH')
        print('4- None')
        print()

        swap_option = input('Enter the option: ')
        while swap_option not in ['1','2','3', '4']:
            swap_option = input('Enter a valid option (1, 2, 3, 4): ')
        
        if swap_option != '4':

            if swap_option == '1':
                swap_token = USDC_ETH
                swap_token_symbol = 'USDC'
            elif swap_option == '2':
                swap_token = DAI_ETH
                swap_token_symbol = 'DAI'
            elif swap_option == '3':
                swap_token = WETH_ETH
                swap_token_symbol = 'WETH'

            path = PATHS[reward_token][swap_token]

            if token_balance > 0:
                print()
                swap_selected_token(avatar_address, roles_mod_address, path, reward_token, token_balance, token_symbol, swap_token, swap_token_symbol, json_file, web3=web3)
        else:
            continue
        
    if json_file['transactions'] != []:
        json_file_download(json_file)
        break
    else:
        restart_end()

