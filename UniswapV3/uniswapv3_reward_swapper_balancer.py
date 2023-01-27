from defi_protocols.functions import get_symbol, balance_of, get_node
from defi_protocols.constants import USDC_ETH, DAI_ETH, WETH_ETH, ETHEREUM
from txn_uniswapv3_helpers import COMP, AAVE, RETH2, SWISE, SETH2, bcolors, get_best_rate, swap_selected_token, json_file_download, restart_end
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
        WETH_ETH: [RETH2, SETH2, WETH_ETH]
    },
    SWISE: {
        USDC_ETH: [SWISE, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [SWISE, SETH2, WETH_ETH, DAI_ETH],
        WETH_ETH: [SWISE, SETH2, WETH_ETH]
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

avatar_address = '0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89'
roles_mod_address = '0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9'

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
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}---------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}--- Rewards ---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}---------------{bcolors.ENDC}")
    print()

    for reward_token in REWARDS_TOKENS:
        token_symbol = get_symbol(reward_token, ETHEREUM, web3=web3)
        token_balance = balance_of(avatar_address, reward_token, 'latest', ETHEREUM, web3=web3)
        message = ('Reward Token: %s\nBalance: %.18f' % (token_symbol, token_balance)).rstrip('0').rstrip('.')
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()

        if token_balance == 0:
            continue
        
        print('Select the action to execute with the balance of %s: ' % token_symbol)

        j = 0
        valid_swap_token_options = []
        for swap_token in PATHS[reward_token]:
            print('%d- %s' % (j+1, get_symbol(swap_token, ETHEREUM, web3=web3)))
            valid_swap_token_options.append(str(j+1))
            j += 1
        
        j += 1
        print('%d- None' % j)
        valid_swap_token_options.append(str(j))
        
        print()
        swap_token_option = input('Enter the token: ')
        while swap_token_option not in valid_swap_token_options:
            message = 'Enter a valid option (' + ','.join(option for option in valid_swap_token_options) + '): '
            swap_token_option = input(message)
        
        if int(swap_token_option) != j:
            # print()
            selected_swap_token = list(PATHS[reward_token])[int(swap_token_option) - 1]
            selected_swap_token_symbol = get_symbol(selected_swap_token, ETHEREUM, web3=web3)

            # path, rate = get_best_rate(PATHS[reward_token][selected_swap_token], web3=web3)
            path, amount_out_min = get_best_rate(PATHS[reward_token][selected_swap_token], web3=web3)
            
             # swap_selected_token(avatar_address, roles_mod_address, path, rate, reward_token, token_balance, token_symbol, selected_swap_token, selected_swap_token_symbol, json_file, web3=web3)
            swap_selected_token(avatar_address, roles_mod_address, path, amount_out_min, reward_token, token_balance, swap_token, json_file, web3=web3)

            print()
        
        else:
            print()
            continue
        
    if json_file['transactions'] != []:
        json_file_download(json_file)
        break
    else:
        restart_end()

