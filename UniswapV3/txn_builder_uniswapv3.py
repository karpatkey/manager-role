from defi_protocols.functions import *
from defi_protocols.constants import *
from txn_uniswapv3 import *

MAX_TOKEN_AMOUNT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

ABI_ALLOWANCE = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Transaction Builder ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
print()

while proceed:
    eth = False
    print(f"{bcolors.OKBLUE}--------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--- Tokens ---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--------------{bcolors.ENDC}")
    print()
    print(f"{bcolors.WARNING}If one of the tokens is ETH press Enter{bcolors.ENDC}")
    print()
    token0 = input('Enter Token0 address: ').lower()
    while not web3.isAddress(token0) and token0 != '':
        token0 = input('Enter a valid address: ').lower()
    
    if token0 == '':
        token0 = WETH_ETH
        eth = True

    print()
    token1 = input('Enter Token1 address: ').lower()
    while not web3.isAddress(token1) and token1 != '':
        token1 = input('Enter a valid address: ').lower()
    
    if token1 == '':
        token1 = WETH_ETH
        eth = True

    print()

    if token0 == token1:
        print(f"{bcolors.FAIL}{bcolors.BOLD}ERROR: Tokens can't have the same address{bcolors.ENDC}")
        break

    print(f"{bcolors.OKBLUE}------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--- Fees ---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}------------{bcolors.ENDC}")

    print()
    print('1- 0.01%')
    print('2- 0.05%')
    print('3- 0.3%')
    print('4- 1%')
    print()
    
    fee = input('Enter the Fee: ')
    while fee not in ['1','2','3','4']:
        fee = input('Enter a valid option (1, 2, 3 or 4): ')
    
    if fee == '1':
        fee = 100
    elif fee == '2':
        fee = 500
    elif fee == '3':
        fee = 3000
    elif fee == '4':
        fee = 10000
    
    print()
    
    pool = subgraph_query_pool(token0, token1, fee)
    if pool == None:
        token0 = web3.toChecksumAddress(token0)
        token1 = web3.toChecksumAddress(token1)
        if token0 > token1:
            token0, token1 = token1, token0
        token0_symbol = get_symbol(token0, ETHEREUM, web3=web3)
        token1_symbol = get_symbol(token1, ETHEREUM, web3=web3)
        message = 'Warning: No pool in Uniswap V3 for tokens: %s and %s, with Fee: %.2f%%' % (token0_symbol, token1_symbol, fee/10000)
        print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()
    else:
        token0 = web3.toChecksumAddress(pool[0]['token0']['id'])
        token1 = web3.toChecksumAddress(pool[0]['token1']['id'])
        token0_symbol = get_symbol(token0, ETHEREUM, web3=web3)
        token1_symbol = get_symbol(token1, ETHEREUM, web3=web3)
    
    if token0 == WETH_ETH and eth == True:
        token0_symbol = 'ETH' 

    if token1 == WETH_ETH and eth == True:
        token1_symbol = 'ETH'       

    token0_decimals = get_decimals(token0, ETHEREUM, web3=web3)
    token1_decimals = get_decimals(token1, ETHEREUM, web3=web3)
    message = 'UniswapV3 %s/%s %.2f%%:' % (token0_symbol, token1_symbol, fee/10000)
    print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")
    #print(f"{bcolors.OKGREEN}{pool}{bcolors.ENDC}")

    print()
    print(f"{bcolors.OKBLUE}------------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--- Operations ---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}------------------{bcolors.ENDC}")
    print()
    print('1- Add Liquidity (New Position)')
    print('2- Increase Liquidity')
    print('3- Remove Liquidity')
    print('4- Collect Fees')
    print()
    operation = input('Enter the operation you want to execute: ') 
    while operation not in ['1','2','3','4']:
        operation = input('Enter a valid option (1, 2, 3 or 4): ')
    
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
    
    if operation == '1':
        print(f"{bcolors.OKBLUE}---------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Add Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}---------------------{bcolors.ENDC}")
        print()
    
        avatar_address = input('Enter the Avatar Safe address: ')
        while not web3.isAddress(avatar_address):
            avatar_address = input('Enter a valid address: ')
        
        web3.toChecksumAddress(avatar_address)

        print()

        roles_mod_address = input('Enter the Roles Module address: ')
        while not web3.isAddress(roles_mod_address):
            roles_mod_address = input('Enter a valid address: ')
        
        web3.toChecksumAddress(roles_mod_address)

        print()

        print('Select the token to enter the amount: ')
        print('1- %s' % token0_symbol)
        print('2- %s' % token1_symbol)
        print()

        token_option = input('Enter the Token: ')
        while token_option not in ['1','2']:
            token_option = input('Enter a valid option (1 or 2): ')

        print()
        amount0_desired = 0
        amount1_desired = 0
        if token_option == '1':
            amount0_desired = input('Enter the Amount of %s: ' % token0_symbol)
        elif token_option == '2':
            amount1_desired = input('Enter the Amount of %s: ' % token1_symbol)

        while True:
            try:
                if token_option == '1':
                    amount0_desired = float(amount0_desired)
                    amount1_desired = 2 * amount0_desired * 10**token1_decimals
                    amount0_desired = amount0_desired * 10**token0_decimals
                elif token_option == '2':
                    amount1_desired = float(amount1_desired)
                    amount0_desired = amount1_desired / 2 * 10**token0_decimals
                    amount1_desired = amount1_desired * 10**token1_decimals
                break
            except:
                if token_option == '1':
                    amount0_desired = input('Enter a valid amount: ' )
                elif token_option == '2':
                    amount1_desired = input('Enter a valid amount: ' )
        
        # approve Token0
        if token0_symbol != 'ETH':
            token0_contract = get_contract(token0, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
            if token0_contract.functions.allowance(avatar_address, UniswapV3.POSITIONS_NFT).call() == 0:
                tx_data = get_data(token0, 'approve', [UniswapV3.POSITIONS_NFT, MAX_TOKEN_AMOUNT], ETHEREUM, web3=web3)
                if tx_data is not None:
                    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [token0, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
                    if exec_data is not None:
                        json_file['transactions'].append(
                            {
                                'to': roles_mod_address,
                                'data': exec_data,
                                'value': 0
                            }
                        )

        # approve Token1
        if token1_symbol != 'ETH':
            token1_contract = get_contract(token0, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
            if token1_contract.functions.allowance(avatar_address, UniswapV3.POSITIONS_NFT).call() == 0:
                tx_data = get_data(token1, 'approve', [UniswapV3.POSITIONS_NFT, MAX_TOKEN_AMOUNT], ETHEREUM, web3=web3)
                if tx_data is not None:
                    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [token1, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
                    if exec_data is not None:
                        json_file['transactions'].append(
                            {
                                'to': roles_mod_address,
                                'data': exec_data,
                                'value': 0
                            }
                        )
        
        # createAndInitializePoolIfNecessary
        if pool == None:
            sqrt_price_x96 = 1
            tx_data = get_data(UniswapV3.POSITIONS_NFT, 'createAndInitializePoolIfNecessary', [token0, token1, fee, sqrt_price_x96], ETHEREUM, web3=web3)
            
            value = 0
            if tx_data is not None:
                exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [UniswapV3.POSITIONS_NFT, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
                if exec_data is not None:
                    if eth == True:
                        if token0_symbol == 'ETH':
                            value = amount0_desired
                        else:
                            value = amount1_desired
                    
                    json_file['transactions'].append(
                        {
                            'to': roles_mod_address,
                            'data': exec_data,
                            'value': int(value)
                        }
                    )
        
        # mint
        tick_lower = fee / 2
        tick_upper = fee * 2
        amount0_min = 0.1 * amount0_desired
        amount1_min = 0.1 * amount1_desired
        deadline = math.floor(datetime.now().timestamp()+1800)
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'mint', [[token0, token1, int(fee), int(tick_lower), int(tick_upper), int(amount0_desired), int(amount1_desired), int(amount0_min), int(amount1_min), avatar_address, int(deadline)]], ETHEREUM, web3=web3)

        value = 0
        if tx_data is not None:
            exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [UniswapV3.POSITIONS_NFT, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
            if exec_data is not None:
                if eth == True:
                    if token0_symbol == 'ETH':
                        value = amount0_desired
                    else:
                        value = amount1_desired
                
                json_file['transactions'].append(
                    {
                        'to': roles_mod_address,
                        'data': exec_data,
                        'value': int(value)
                    }
                )
        
        # If one of the two tokens is ETH add the refundETH() function call
        if value > 0:
            tx_data = get_data(UniswapV3.POSITIONS_NFT, 'refundETH', [], ETHEREUM, web3=web3)
            if tx_data is not None:
                exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [UniswapV3.POSITIONS_NFT, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')

                if exec_data is not None:
                    json_file['transactions'].append(
                        {
                            'to': roles_mod_address,
                            'data': exec_data,
                            'value': int(value)
                        }
                    )
                    
    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_txn_builder.json', 'w') as uniswapv3_txn_builder:
        json.dump(json_file, uniswapv3_txn_builder)
    
    break
    

    

    

    
