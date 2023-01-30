from defi_protocols.functions import get_symbol, balance_of, get_node, get_data, get_decimals
from defi_protocols.constants import USDC_ETH, USDT_ETH, DAI_ETH, WETH_ETH, WBTC_ETH, ZERO_ADDRESS, ETHEREUM
from txn_uniswapv3_helpers import COMP, AAVE, RETH2, SWISE, SETH2, bcolors, get_best_rate, swap_selected_token, json_file_download, restart_end, add_txn_with_role
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOKENS = [SETH2, COMP, AAVE, RETH2, SWISE, WETH_ETH, USDC_ETH, USDT_ETH, DAI_ETH, WBTC_ETH]

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
    },
    SETH2: {
        WETH_ETH: [SETH2, WETH_ETH]
    },
    WETH_ETH: {
        SETH2: [WETH_ETH, SETH2],
        USDC_ETH: [WETH_ETH, USDC_ETH],
        USDT_ETH: [WETH_ETH, USDT_ETH],
        DAI_ETH: [WETH_ETH, DAI_ETH],
        WBTC_ETH: [WETH_ETH, WBTC_ETH]
    },
    USDC_ETH: {
        WETH_ETH: [USDC_ETH, WETH_ETH],
        USDT_ETH: [[USDC_ETH, USDT_ETH], [USDC_ETH, WETH_ETH, USDT_ETH]],
        DAI_ETH: [[USDC_ETH, DAI_ETH], [USDC_ETH, WETH_ETH, DAI_ETH]]
    },
    USDT_ETH: {
        WETH_ETH: [USDT_ETH, WETH_ETH],
        USDC_ETH: [[USDT_ETH, USDC_ETH], [USDT_ETH, WETH_ETH, USDC_ETH]],
        DAI_ETH: [[USDT_ETH, DAI_ETH], [USDT_ETH, WETH_ETH, DAI_ETH]]
    },
    DAI_ETH: {
        WETH_ETH: [DAI_ETH, WETH_ETH],
        USDC_ETH: [[DAI_ETH, USDC_ETH], [DAI_ETH, WETH_ETH, USDC_ETH]],
        USDT_ETH: [[DAI_ETH, USDT_ETH], [DAI_ETH, WETH_ETH, USDT_ETH]]
    },
    WBTC_ETH: {
        WETH_ETH: [WBTC_ETH, WETH_ETH]
    },
}



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Token Swapper ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
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
    print(f"{bcolors.WARNING}{bcolors.BOLD}If you choose sETH2, it will automatically be swapped by WETH{bcolors.ENDC}")
    print('Select the action to execute: ')

    valid_token_options = []
    for i in range(len(TOKENS)):
        
        print('%d- Swap %s' % (i+1, get_symbol(TOKENS[i], ETHEREUM, web3=web3)))
        
        valid_token_options.append(str(i+1))
    
    i += 2
    print('%d- Wrap %s' % (i, 'ETH'))
    valid_token_options.append(str(i))

    i += 1
    print('%d- Unwrap %s' % (i, 'WETH'))
    valid_token_options.append(str(i))

    print()
    token_option = input('Enter the token: ')
    while token_option not in valid_token_options:
        message = 'Enter a valid option (' + ','.join(option for option in valid_token_options) + '): '
        token_option = input(message)

    if int(token_option) <= i-2:
        selected_token = TOKENS[int(token_option)-1]
        token_symbol = get_symbol(selected_token, ETHEREUM, web3=web3)
        token_balance = balance_of(avatar_address, selected_token, 'latest', ETHEREUM, web3=web3, decimals=False)
        selected_token_decimals = get_decimals(selected_token, ETHEREUM, web3=web3)

        if token_balance > 0:
            print()
            message = str('The amount of %s in the Avatar Safe is: %.18f' % (token_symbol, token_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
            print()
            message = 'If you want to select the MAX amount of %s enter \"max\"' % token_symbol
            print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
            amount = input('Enter the amount of %s to swap: ' % token_symbol)
            while True:
                try:
                    if amount == 'max':
                        amount = token_balance / (10**selected_token_decimals)
                    else:
                        amount = float(amount)
                        if amount > token_balance / (10**selected_token_decimals):
                            print()
                            message = str('Insufficient balance of %s in Avatar Safe: %.18f' % (token_symbol, token_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
                            message += (' %s\n') % token_symbol
                            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                            raise Exception
                    break
                except:
                    amount = input('Enter a valid amount: ')

            if len(list(PATHS[selected_token])) == 1:
                swap_token_option = 1
            else:
                print()
                print('Select the token to swap the %s amount for: ' % token_symbol)
                j = 0
                valid_swap_token_options = []
                for swap_token in PATHS[selected_token]:
                    print('%d- %s' % (j+1, get_symbol(swap_token, ETHEREUM, web3=web3)))
                    valid_swap_token_options.append(str(j+1))
                    j += 1
                
                print()
                swap_token_option = input('Enter the token: ')
                while swap_token_option not in valid_swap_token_options:
                    message = 'Enter a valid option (' + ','.join(option for option in valid_swap_token_options) + '): '
                    swap_token_option = input(message)

                print()
            
            selected_swap_token = list(PATHS[selected_token])[int(swap_token_option) - 1]
            selected_swap_token_symbol = get_symbol(selected_swap_token, ETHEREUM, web3=web3)

            # rate = get_best_rate(PATHS[selected_token][selected_swap_token], web3=web3)
            path, amount_out_min = get_best_rate(PATHS[selected_token][selected_swap_token], web3=web3)
            
            # swap_selected_token(avatar_address, roles_mod_address, rate, selected_token, token_balance, token_symbol, selected_swap_token, selected_swap_token_symbol, json_file, web3=web3)
            swap_selected_token(avatar_address, roles_mod_address, path, amount_out_min, selected_token, amount, selected_swap_token, json_file, web3=web3)
            
        else:
            print()
            message = 'Avatar Safe has no remaining balance of %s' % (token_symbol)
            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")

    else:
        print()
        if token_option == str(i-1):
            selected_token = ZERO_ADDRESS
            symbol = 'ETH'
            action = 'wrap'
        else:
            selected_token = WETH_ETH
            symbol = 'WETH'
            action = 'unwrap'

        balance = balance_of(avatar_address, selected_token, 'latest', ETHEREUM, decimals=False, web3=web3)
        if balance > 0:
            message = str('The amount of %s in the Avatar Safe is: %.18f' % (symbol, balance / (10**18))).rstrip('0').rstrip('.')
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
            print()
            message = 'If you want to select the MAX amount of %s enter \"max\"' % symbol
            print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")

            amount = input('Enter the amount of %s to %s: ' % (symbol, action))

            while True:
                try:
                    if amount == 'max':
                        amount = balance / (10**18)
                    else:
                        amount = float(amount)
                        if amount > balance / (10**18):
                            print()
                            message = str('Insufficient balance of %s in Avatar Safe: %.18f' % (symbol, (balance / (10**18)))).rstrip('0').rstrip('.')
                            message += (' %s\n') % symbol
                            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                            raise Exception
                    break
                except:
                    amount = input('Enter a valid amount: ')

            eth_value = 0
            amount = amount * (10**18)
            if selected_token == ZERO_ADDRESS:
                tx_data = get_data(WETH_ETH, 'deposit', [], ETHEREUM, web3=web3)
                eth_value = amount
            else:
                tx_data = get_data(WETH_ETH, 'withdraw', [int(amount)], ETHEREUM, web3=web3)

            if tx_data is not None:
                add_txn_with_role(roles_mod_address, WETH_ETH, tx_data, eth_value, json_file, web3=web3)
        
        else:
            message = 'Avatar Safe has no remaining balance of %s' % (symbol)
            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
        
    print()

    if json_file['transactions'] != []:
        json_file_download(json_file)
        break
    else:
        restart_end()

