from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols.UniswapV3 import *
from txn_uniswapv3 import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MAX_TOKEN_AMOUNT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

MAX_COLLECT_AMOUNT = 340282366920938463463374607431768211455

MIN = 'MIN'

MAX = 'MAX'

TICK_SPACING = {
    FEES[0]: 1,
    FEES[1]: 10,
    FEES[2]: 60,
    FEES[3]: 200
}

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

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ABI_ALLOWANCE = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# approve_tokens
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def approve_tokens():

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
        token1_contract = get_contract(token1, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
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


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# tokens_amounts
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def tokens_amounts():

    global token0_symbol
    global token1_symbol
    global eth

    print('Select the token to enter the amount: ')
    print('1- %s' % token0_symbol)
    print('2- %s' % token1_symbol)
    print()

    token_option = input('Enter the Token: ')
    while token_option not in ['1','2']:
        token_option = input('Enter a valid option (1 or 2): ')
    
    if (token_option == '1' and token0_symbol == 'WETH') or (token_option == '2' and token1_symbol == 'WETH'):
        print()
        print('Select the token to enter the amount: ')
        print('1- ETH')
        print('2- WETH')
        print()
        token_option_eth = input('Enter the Token: ')
        while token_option_eth not in ['1','2']:
            token_option_eth = input('Enter a valid option (1 or 2): ')
        
        if token_option_eth == '1':
            eth = True
            if token_option == '1':
                token0_symbol = 'ETH'
            else:
                token1_symbol = 'ETH'

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
                amount1_desired = 496554138828729 # CHANGE
                amount0_desired = amount0_desired * 10**token0_decimals
            elif token_option == '2':
                amount1_desired = float(amount1_desired)
                amount0_desired = 3598 # CHANGE
                amount1_desired = amount1_desired * 10**token1_decimals
            break
        except:
            if token_option == '1':
                amount0_desired = input('Enter a valid amount: ')
            elif token_option == '2':
                amount1_desired = input('Enter a valid amount: ')
    
    return amount0_desired, amount1_desired

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# set_price
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def set_price(price_range_option, min_max):

    if price_range_option == '1':
        price = input('Enter the %s Price of %s per %s desired: ' % (min_max, token1_symbol, token0_symbol))
    else:
        price = input('Enter the %s Price of %s per %s desired: ' % (min_max, token0_symbol, token1_symbol))
    
    while True:
        try:
            price = float(price)
            break
        except:
            price = input('Enter a valid price: ')
    
    print()
    
    if price_range_option == '2':
        price = 1 / price

    tick_index = (math.log10(price) + (token1_decimals - token0_decimals)) / math.log10(1.0001) / TICK_SPACING[fee]
    tick1_index = math.floor(tick_index)
    tick2_index = math.ceil(tick_index)
    price1 = 1.0001**(tick1_index * TICK_SPACING[fee]) / 10**(token1_decimals - token0_decimals)
    price2 = 1.0001**(tick2_index * TICK_SPACING[fee]) / 10**(token1_decimals - token0_decimals)
    
    if price_range_option == '2':
        price1 = 1 / price1
        price2 = 1 / price2
    
    if price_range_option == '1':
        print('Enter the %s Price of %s per %s: ' % (min_max, token1_symbol, token0_symbol))
    else:
        print('Enter the %s Price of %s per %s: ' % (min_max, token0_symbol, token1_symbol))
    
    print('1- %.8f' % price1)
    print('2- %.8f' % price2)
    print()
    
    price_option = input('Enter the option: ')
    while price_option not in ['1','2']:
        price_option = input('Enter a valid option (1 or 2): ')
    
    if price_option == '1':
        price = price1
        tick = tick1_index * TICK_SPACING[fee]
    else:
        price = price2
        tick = tick2_index * TICK_SPACING[fee]
    
    return price, tick


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# tokens_prices
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def tokens_prices():

    print('Set Price Range: ')
    print('1- %s per %s' % (token1_symbol, token0_symbol))
    print('2- %s per %s' % (token0_symbol, token1_symbol))
    print()

    price_range_option = input('Enter the option: ')
    while price_range_option not in ['1','2']:
        price_range_option = input('Enter a valid option (1 or 2): ')

    print()
    min_price = 0
    max_price = 0
    current_price = get_rate_uniswap_v3(token0, token1, 'latest', ETHEREUM, fee=fee)
    
    if price_range_option == '1':
        message = 'The current price of %s per %s is %.8f' % (token1_symbol, token0_symbol, current_price)
    else:
        message = 'The current price of %s per %s is %.8f' % (token0_symbol, token1_symbol, 1 / current_price)
    
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

    print()
    min_price, tick1 = set_price(price_range_option, MIN)
    print()
    max_price, tick2 = set_price(price_range_option, MAX)

    if tick1 <= tick2:
        tick_lower = tick1
        tick_upper = tick2
    else:
        tick_lower = tick2
        tick_upper = tick1

    return min_price, max_price, tick_lower, tick_upper, current_price, price_range_option, 


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_eth_value
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_eth_value():

    eth_value = 0
    if eth == True:
        if token0_symbol == 'ETH':
            eth_value = amount0_desired
        else:
            eth_value = amount1_desired
    
    return eth_value


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_txn_with_role
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_txn_with_role(tx_data, eth_value):

    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [UniswapV3.POSITIONS_NFT, eth_value, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
    if exec_data is not None:   
        json_file['transactions'].append(
            {
                'to': roles_mod_address,
                'data': exec_data,
                'value': str(0)
            }
        )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# input_nft_position
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def input_nft_position():

    positions_nft_contract = get_contract(UniswapV3.POSITIONS_NFT, ETHEREUM, web3=web3, abi=UniswapV3.ABI_POSITIONS_NFT)
    nft_indexes = positions_nft_contract.functions.balanceOf(avatar_address).call()
    
    if nft_indexes == 0:
        message = 'ERROR: No NFT Position IDs found in Safe: %s' % avatar_address
        print(f"{bcolors.FAIL}{message}{bcolors.ENDC}")
        return None
    else:
        safe_positions = []
        valid_options = []
        print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- NFT Positions IDs ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
        print()
        for i in range(nft_indexes):
            nft_position_id = positions_nft_contract.functions.tokenOfOwnerByIndex(avatar_address, i).call()
            position = positions_nft_contract.functions.positions(nft_position_id).call()
            token0 = position[2]
            token0_symbol = get_symbol(token0, ETHEREUM, web3=web3)
            token1 = position[3]
            token1_symbol = get_symbol(token1, ETHEREUM, web3=web3)
            fee = position[4]

            safe_positions.append([nft_position_id, token0, token0_symbol, token1, token1_symbol, fee])
            valid_options.append(str(i+1))

            print('%d- %d: %s/%s, %.2f%%' % (i+1, nft_position_id, token0_symbol, token1_symbol, fee/10000))

        print()
        option = input('Enter the NFT Position ID: ')
        while option not in valid_options:
            message = 'Enter a valid option (' + ','.join(option for option in valid_options) + '): '
            option = input(message)
        
        print()

        return safe_positions[int(option)-1]


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_liquidity():

    # tokens approvals
    approve_tokens()

    eth_value = get_eth_value()
    
    # createAndInitializePoolIfNecessary
    if pool == None:
        sqrt_price_x96 = math.sqrt(current_price * 10**(token1_decimals - token0_decimals)) * (2**96)
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'createAndInitializePoolIfNecessary', [token0, token1, fee, int(sqrt_price_x96)], ETHEREUM, web3=web3)
        
        if tx_data is not None:
            add_txn_with_role(tx_data, eth_value)
    
    # mint
    amount0_min = 3568 # CHANGE
    amount1_min = 492307833644865 # CHANGE
    deadline = math.floor(datetime.now().timestamp()+1800)
    tx_data = get_data(UniswapV3.POSITIONS_NFT, 'mint', [[token0, token1, int(fee), int(tick_lower), int(tick_upper), int(round(amount0_desired)), int(round(amount1_desired)), int(round(amount0_min)), int(round(amount1_min)), avatar_address, int(deadline)]], ETHEREUM, web3=web3)

    if tx_data is not None:
        add_txn_with_role(tx_data, eth_value)
    
    # If one of the two tokens is ETH add the refundETH() function call
    if eth:
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'refundETH', [], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(tx_data, 0)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# increase_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def increase_liquidity():

    # tokens approvals
    approve_tokens()

    eth_value = get_eth_value()

    amount0_min = 0.1 * amount0_desired # CHANGE
    amount1_min = 0.1 * amount1_desired # CHANGE
    deadline = math.floor(datetime.now().timestamp()+1800)

    tx_data = get_data(UniswapV3.POSITIONS_NFT, 'increaseLiquidity', [[int(nft_position_id), int(amount0_desired), int(amount1_desired), int(amount0_min), int(amount1_min), int(deadline)]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(tx_data, eth_value)
    
    # If one of the two tokens is ETH add the refundETH() function call
    if eth:
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'refundETH', [], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(tx_data, 0)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# remove_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_liquidity():

    liquidity = 1
    amount0_min = 0.1 * amount0_desired # CHANGE
    amount1_min = 0.1 * amount1_desired # CHANGE
    deadline = math.floor(datetime.now().timestamp()+1800)

    # remove liquidity
    tx_data = get_data(UniswapV3.POSITIONS_NFT, 'decreaseLiquidity', [[int(nft_position_id), int(liquidity), int(amount0_min), int(amount1_min), int(deadline)]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(tx_data, 0)
    
    collect()


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# collect
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def collect():

    if option == '1':
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'collect', [[int(nft_position_id), ZERO_ADDRESS, MAX_COLLECT_AMOUNT, MAX_COLLECT_AMOUNT]], ETHEREUM, web3=web3)
    else:  
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'collect', [[int(nft_position_id), avatar_address, MAX_COLLECT_AMOUNT, MAX_COLLECT_AMOUNT]], ETHEREUM, web3=web3)

    if tx_data is not None:
        add_txn_with_role(tx_data, 0)
    
    if option == '1':
        collect_eth_amount = 1 # CHANGE: how to obtain the amount of eth to collect
        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'unwrapWETH9', [int(round(collect_eth_amount)), avatar_address], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(tx_data, 0)
        
        collect_token_amount = 1 # CHANGE: how to obtain the amount of the other token to collect
        if token0_symbol == 'ETH':
            collect_token = token1
        else:
            collect_token = token0

        tx_data = get_data(UniswapV3.POSITIONS_NFT, 'sweepToken', [collect_token, int(round(collect_token_amount)), avatar_address], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(tx_data, 0)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Transaction Builder ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
print()

while proceed:
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
    
    eth = False
    token0_symbol = ''
    token1_symbol = ''
    if operation == '1':
        print()
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

            message = 'Pool: UniswapV3 %s/%s %.2f%%:' % (token0_symbol, token1_symbol, fee/10000)
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
            print()
            #print(f"{bcolors.OKGREEN}{pool}{bcolors.ENDC}")

            if token0 == WETH_ETH and eth == True:
                token0_symbol = 'ETH' 

            if token1 == WETH_ETH and eth == True:
                token1_symbol = 'ETH'
                
    else:
        print()
        nft_position = input_nft_position()
        if nft_position == None:
            break
        else:
            nft_position_id, token0, token0_symbol, token1, token1_symbol, fee = nft_position      

    token0_decimals = get_decimals(token0, ETHEREUM, web3=web3)
    token1_decimals = get_decimals(token1, ETHEREUM, web3=web3)

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
        
        amounts = tokens_amounts()
        amount0_desired = amounts[0]
        amount1_desired = amounts[1]
        print()

        min_price, max_price, tick_lower, tick_upper, current_price, price_range_option = tokens_prices()
        print()
        if price_range_option == '1':
            message = 'The MIN price of %s per %s selected is %.8f\n' % (token1_symbol, token0_symbol, min_price)
            message += 'The MAX price of %s per %s selected is %.8f' % (token1_symbol, token0_symbol, max_price)
        else:
            message = 'The MIN price of %s per %s selected is %.8f\n' % (token0_symbol, token1_symbol, min_price)
            message += 'The MAX price of %s per %s selected is %.8f' % (token0_symbol, token1_symbol, max_price)

        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
        
        add_liquidity()
    
    elif operation == '2':
        print(f"{bcolors.OKBLUE}--------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Increase Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--------------------------{bcolors.ENDC}")
        print()
        
        if nft_position_id != None:
            amounts = tokens_amounts()
            amount0_desired = amounts[0]
            amount1_desired = amounts[1]
            print()

            increase_liquidity()
        
        else:
            break
    
    elif operation == '3':
        print(f"{bcolors.OKBLUE}------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Remove Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}------------------------{bcolors.ENDC}")
        print()

        if nft_position_id != None:
            amounts = tokens_amounts()
            amount0_desired = amounts[0]
            amount1_desired = amounts[1]
            print()

            if eth == True:
                print('Collect ETH or WETH')
                print('1- ETH')
                print('2- WETH')
                print()
            
                option = input('Enter the option: ')
                while option not in ['1','2']:
                    option = input('Enter a valid option (1, 2): ')
                
                if option == '2':
                    if token0_symbol == 'ETH':
                        token0_symbol = 'WETH'
                    else:
                        token1_symbol = 'WETH'
                
                print()

            remove_liquidity()
        
        else:
            break
    
    elif operation == '4':
        print(f"{bcolors.OKBLUE}--------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Collect Fees ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--------------------{bcolors.ENDC}")
        print()

        if nft_position_id != None:
            if eth == True:
                print('Collect ETH or WETH')
                print('1- ETH')
                print('2- WETH')
                print()
            
                option = input('Enter the option: ')
                while option not in ['1','2']:
                    option = input('Enter a valid option (1, 2): ')
                
                if option == '2':
                    if token0_symbol == 'ETH':
                        token0_symbol = 'WETH'
                    else:
                        token1_symbol = 'WETH'
                
                print()
            
            collect()
        
        else:
            break

    print()
    print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--- JSON File Download---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
    print()

    file_name = input('Enter the name of the JSON file: ')
    file_path = str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/%s.json' % file_name
    print()
    try:
        with open(file_path, 'w') as uniswapv3_txn_builder:
            json.dump(json_file, uniswapv3_txn_builder)
        
        message = 'JSON file %s was succesfully downloaded to the path: %s' % ('%s.json' % file_name, file_path)
        print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")
    except:
        message = 'ERROR: JSON file %s download fail' % ('%s.json' % file_name)
        print(f"{bcolors.FAIL}{message}{bcolors.ENDC}")


    break
    

    

    

    
