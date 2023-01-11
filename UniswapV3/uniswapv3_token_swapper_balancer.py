from defi_protocols.functions import get_symbol, balance_of, get_node, get_data
from defi_protocols.constants import USDC_ETH, DAI_ETH, WETH_ETH, ZERO_ADDRESS, ETHEREUM
from txn_uniswapv3_helpers import COMP, AAVE, RETH2, SWISE, SETH2, bcolors, swap_selected_token, json_file_download, restart_end, add_txn_with_role
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOKENS = [SETH2, COMP, AAVE, RETH2, SWISE, WETH_ETH]

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
    },
    SETH2: {
        WETH_ETH: [SETH2, WETH_ETH]
    },
    WETH_ETH: {
        USDC_ETH: [WETH_ETH, USDC_ETH],
        DAI_ETH: [WETH_ETH, DAI_ETH],
    }
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

avatar_address = '0xA2372f3C9a26F45b5D69BD513BE0d553Ff9CC617'
roles_mod_address = '0xeF14e0f66a2e22Bbe85bFA53b3F956354Ce51e62'

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

    if token_option <= str(i-2):
        selected_token = TOKENS[int(token_option)-1]
        if selected_token in [SETH2, COMP, AAVE, RETH2, SWISE, WETH_ETH]:
            token_symbol = get_symbol(selected_token, ETHEREUM, web3=web3)
            token_balance = balance_of(avatar_address, selected_token, 'latest', ETHEREUM, web3=web3)
            if token_balance > 0:
                print()
                message = ('Selected Token: %s\nBalance: %.18f' % (token_symbol, token_balance)).rstrip('0').rstrip('.')
                print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
                print()

                if selected_token == SETH2:
                    swap_token = WETH_ETH
                    swap_token_symbol = 'WETH'
                
                elif selected_token == WETH_ETH:
                    print('Select the token to swap the %s balance for: ' % token_symbol)
                    print('1- USDC')
                    print('2- DAI')
                    print()
                    swap_option = input('Enter the option: ')
                    while swap_option not in ['1','2']:
                        swap_option = input('Enter a valid option (1, 2): ')
                    
                else:
                    print('Select the token to swap the %s balance for: ' % token_symbol)
                    print('1- USDC')
                    print('2- DAI')
                    print('3- WETH')
                    print()
                    swap_option = input('Enter the option: ')
                    while swap_option not in ['1','2', '3']:
                        swap_option = input('Enter a valid option (1, 2, 3): ')
                    
                if swap_option == '1':
                    swap_token = USDC_ETH
                    swap_token_symbol = 'USDC'
                elif swap_option == '2':
                    swap_token = DAI_ETH
                    swap_token_symbol = 'DAI'
                elif swap_option == '3':
                    swap_token = WETH_ETH
                    swap_token_symbol = 'WETH'       
            
                path = PATHS[selected_token][swap_token]

                if token_balance > 0:
                    print()
                    swap_selected_token(avatar_address, roles_mod_address, path, selected_token, token_balance, token_symbol, swap_token, swap_token_symbol, json_file, web3=web3)
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
            message = 'If you want to select the MAX amount of %s enter \"max\"' % symbol
            print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")

            if selected_token == ZERO_ADDRESS:
                amount = input('Enter the Amount of %s to %s: ' % (symbol, action))

            while True:
                try:
                    if amount == 'max':
                        amount = balance
                    else:
                        amount = float(amount)
                        if amount > balance / (10**18):
                            print()
                            message = str('Insufficient balance of ETH in Avatar Safe: %.18f' % (balance / (10**18))).rstrip('0').rstrip('.')
                            message += (' %s\n') % symbol
                            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                            raise Exception
                    break
                except:
                    amount = input('Enter a valid amount: ')

            eth_value = 0
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

