from txn_uniswapv3_helpers import *
from defi_protocols.UniswapV3 import ABI_POOL, ABI_POSITIONS_NFT, ABI_FACTORY, FEES, POSITIONS_NFT, FACTORY, get_rate_uniswap_v3, get_fee
from defi_protocols.prices.prices import get_price
from defi_protocols.functions import get_contract, get_symbol, get_data, get_node, get_decimals
from defi_protocols.constants import ETHEREUM, WETH_ETH, ZERO_ADDRESS
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MAX_COLLECT_AMOUNT = 340282366920938463463374607431768211455

MIN = 'MIN'

MAX = 'MAX'

TICK_SPACING = {
    FEES[0]: 1,
    FEES[1]: 10,
    FEES[2]: 60,
    FEES[3]: 200
}


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
    
    if token0 == WETH_ETH or token1 == WETH_ETH:
        print()
        print('Select the token you prefer to add: ')
        print('1- ETH')
        print('2- WETH')
        print()
        token_option_eth = input('Enter the Token: ')
        while token_option_eth not in ['1','2']:
            token_option_eth = input('Enter a valid option (1 or 2): ')
        
        if token_option_eth == '1':
            eth = True
            if token0_symbol == 'WETH':
                token0_symbol = 'ETH'
            else:
                token1_symbol = 'ETH'
        
    if token_option == '1':
        selected_token = token0
        selected_token_symbol = token0_symbol
        selected_token_decimals = token0_decimals
    else:
        selected_token = token1
        selected_token_symbol = token1_symbol
        selected_token_decimals = token1_decimals
    
    if selected_token == WETH_ETH and eth:
        selected_token = ZERO_ADDRESS
    
    print()
    
    selected_token_balance = get_selected_token_balance(avatar_address, selected_token, selected_token_symbol, selected_token_decimals, web3=web3)
    if selected_token_balance == 0:
        return None
    
    print()

    if operation == '1':
        return get_amounts_desired(avatar_address, pool_contract, operation, token_option, selected_token_balance, selected_token_decimals, selected_token_symbol, token0, token0_decimals, token0_symbol, token1, token1_decimals, token1_symbol, positions_nft_contract, tick_lower=tick_lower, tick_upper=tick_upper, current_price=current_price, web3=web3)
    else:
        return get_amounts_desired(avatar_address, pool_contract, operation, token_option, selected_token_balance, selected_token_decimals, selected_token_symbol, token0, token0_decimals, token0_symbol, token1, token1_decimals, token1_symbol, positions_nft_contract, nft_position_id=nft_position_id, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# set_price
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def set_price(price_range_option, min_max, current_price, min_price=0):

    if price_range_option == '1':
        price = input('Enter the %s Price of %s per %s desired: ' % (min_max, token1_symbol, token0_symbol))
    else:
        price = input('Enter the %s Price of %s per %s desired: ' % (min_max, token0_symbol, token1_symbol))
    
    while True:
        try:
            price = float(price)
            if min_max == MAX:
                if min_price >= price:
                    print()
                    print(f"{bcolors.FAIL}{bcolors.BOLD}The MAX price must be greater than the MIN price{bcolors.ENDC}")
                    print()
                    raise Exception

                if current_price >= price:
                    print()
                    print(f"{bcolors.FAIL}{bcolors.BOLD}The MAX price must be greater than the current price{bcolors.ENDC}")
                    print()
                    raise Exception
            else:
                if current_price <= price:
                    print()
                    print(f"{bcolors.FAIL}{bcolors.BOLD}The MIN price must be lower than the current price{bcolors.ENDC}")
                    print()
                    raise Exception
            
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
    
    print(str('1- %.18f' % price1).rstrip('0').rstrip('.'))
    print(str('2- %.18f' % price2).rstrip('0').rstrip('.'))
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
# pool_price_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pool_price_data():

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

    if pool_address != ZERO_ADDRESS:
        current_price = get_rate_uniswap_v3(token0, token1, 'latest', ETHEREUM, fee=fee)
    else:
        token0_price = get_price(token0, 'latest', ETHEREUM, web3=web3)[0]
        token1_price = get_price(token1, 'latest', ETHEREUM, web3=web3)[0]

        if token0_price != None and token1_price != None:
            current_price = token0_price / token1_price
        else:
            print(f"{bcolors.FAIL}{bcolors.BOLD}Error while fetching the tokens prices{bcolors.ENDC}")
            return None
    
    if price_range_option == '1':
        message = ('The current price of %s per %s is %.18f' % (token1_symbol, token0_symbol, current_price)).rstrip('0').rstrip('.')
    else:
        message = ('The current price of %s per %s is %.18f' % (token0_symbol, token1_symbol, 1 / current_price)).rstrip('0').rstrip('.')
    
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

    if pool_address == ZERO_ADDRESS:
        print()
        current_price = input('Enter the pool price: ')
        while True:
            try:
                current_price = float(current_price)
                break
            except:
                current_price = input('Enter a valid price: ')
    
    print()
    min_price, tick1 = set_price(price_range_option, MIN, current_price)
    print()
    max_price, tick2 = set_price(price_range_option, MAX, current_price, min_price=min_price)

    if tick1 <= tick2:
        tick_lower = tick1
        tick_upper = tick2
    else:
        tick_lower = tick2
        tick_upper = tick1

    return min_price, max_price, tick_lower, tick_upper, current_price, price_range_option


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_eth_value
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_eth_value():

    eth_value = 0
    if eth == True:
        if token0 == WETH_ETH:
            eth_value = amount0_desired
        else:
            eth_value = amount1_desired
    
    return eth_value


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# input_nft_position
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def input_nft_position():

    nft_indexes = positions_nft_contract.functions.balanceOf(avatar_address).call()
    
    if nft_indexes == 0:
        message = 'ERROR: No NFT Position IDs found in Safe: %s' % avatar_address
        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
        return None
    else:
        safe_positions = []
        valid_options = []
        print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- NFT Positions IDs ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
        print()
        valid_ntfs_counter = 0
        for i in range(nft_indexes):
            nft_position_id = positions_nft_contract.functions.tokenOfOwnerByIndex(avatar_address, i).call()
            position = positions_nft_contract.functions.positions(nft_position_id).call()
            token0 = position[2]
            token0_symbol = get_symbol(token0, ETHEREUM, web3=web3)
            token1 = position[3]
            token1_symbol = get_symbol(token1, ETHEREUM, web3=web3)
            fee = position[4]
            liquidity = position[7]

            if liquidity > 0:
                valid_ntfs_counter += 1
                safe_positions.append([nft_position_id, token0, token0_symbol, token1, token1_symbol, fee, liquidity])
                valid_options.append(str(valid_ntfs_counter))

                print('%d- %d: %s/%s, %.2f%%' % (valid_ntfs_counter, nft_position_id, token0_symbol, token1_symbol, fee/10000))

        print()
        option = input('Enter the NFT Position ID option: ')
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
    approve_tokens(avatar_address, roles_mod_address, token0, token1, POSITIONS_NFT, json_file, web3=web3, eth=eth)

    eth_value = get_eth_value()
    
    # createAndInitializePoolIfNecessary
    if pool_address == ZERO_ADDRESS:
        sqrt_price_x96 = math.sqrt(current_price * 10**(token1_decimals - token0_decimals)) * (2**96)
        tx_data = get_data(POSITIONS_NFT, 'createAndInitializePoolIfNecessary', [token0, token1, fee, int(sqrt_price_x96)], ETHEREUM, web3=web3)
        
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, eth_value, json_file, web3=web3)
    
    # mint
    amount0_min = 0.9 * amount0_desired
    amount1_min = 0.95 * amount1_desired
    deadline = math.floor(datetime.now().timestamp()+1800)
    tx_data = get_data(POSITIONS_NFT, 'mint', [[token0, token1, int(fee), int(tick_lower), int(tick_upper), int(round(amount0_desired)), int(round(amount1_desired)), int(round(amount0_min)), int(round(amount1_min)), avatar_address, int(deadline)]], ETHEREUM, web3=web3)

    if tx_data is not None:
        add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, eth_value, json_file, web3=web3)
    
    # If one of the two tokens is ETH add the refundETH() function call
    if eth:
        tx_data = get_data(POSITIONS_NFT, 'refundETH', [], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# increase_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def increase_liquidity():

    # tokens approvals
    approve_tokens(avatar_address, roles_mod_address, token0, token1, POSITIONS_NFT, json_file, web3=web3, eth=eth)

    eth_value = get_eth_value()

    amount0_min = 0.9 * amount0_desired
    amount1_min = 0.95 * amount1_desired
    deadline = math.floor(datetime.now().timestamp()+1800)

    tx_data = get_data(POSITIONS_NFT, 'increaseLiquidity', [[int(nft_position_id), int(amount0_desired), int(amount1_desired), int(amount0_min), int(amount1_min), int(deadline)]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, eth_value, json_file, web3=web3)
    
    # If one of the two tokens is ETH add the refundETH() function call
    if eth:
        tx_data = get_data(POSITIONS_NFT, 'refundETH', [], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# remove_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_liquidity():

    amount0_min = 0.9 * amount0_desired
    amount1_min = 0.95 * amount1_desired

    deadline = math.floor(datetime.now().timestamp()+1800)

    # remove liquidity
    tx_data = get_data(POSITIONS_NFT, 'decreaseLiquidity', [[int(nft_position_id), int(removed_liquidity), int(amount0_min), int(amount1_min), int(deadline)]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)
    
    collect()


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# collect
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def collect():

    position_fees = get_fee(nft_position_id, 'latest', ETHEREUM, web3=web3, decimals=False)
    if position_fees != None:
        message = str('Unclaimed fees: %.18f' % (position_fees[0][1] / (10**token0_decimals))).rstrip('0').rstrip('.')
        message += (' %s and %.18f' % (token0_symbol, position_fees[1][1] / (10**token1_decimals))).rstrip('0').rstrip('.')
        message += ' %s' % (token1_symbol)
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}Error while retrieving the unclaimed fees{bcolors.ENDC}")
        exit()
    
    if collect_option == '1':
        tx_data = get_data(POSITIONS_NFT, 'collect', [[int(nft_position_id), ZERO_ADDRESS, MAX_COLLECT_AMOUNT, MAX_COLLECT_AMOUNT]], ETHEREUM, web3=web3)
    else:  
        tx_data = get_data(POSITIONS_NFT, 'collect', [[int(nft_position_id), avatar_address, MAX_COLLECT_AMOUNT, MAX_COLLECT_AMOUNT]], ETHEREUM, web3=web3)

    if tx_data is not None:
        add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)
    
    if collect_option == '1':
        
        if position_fees[0][0] == WETH_ETH:
            collect_eth_amount = position_fees[0][1]
            collect_token = token1
            collect_token_amount = position_fees[1][1]
        else:
            collect_eth_amount = position_fees[1][1]
            collect_token = token0
            collect_token_amount = position_fees[0][1]
            
        tx_data = get_data(POSITIONS_NFT, 'unwrapWETH9', [int(round(collect_eth_amount)), avatar_address], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)     

        tx_data = get_data(POSITIONS_NFT, 'sweepToken', [collect_token, int(round(collect_token_amount)), avatar_address], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, POSITIONS_NFT, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Transaction Builder ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------------{bcolors.ENDC}")
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

positions_nft_contract = get_contract(POSITIONS_NFT, ETHEREUM, web3=web3, abi=ABI_POSITIONS_NFT)
factory_contract = get_contract(FACTORY, ETHEREUM, web3=web3, abi=ABI_FACTORY)
pool_address = ZERO_ADDRESS
pool_contract = None

while True:
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
        print(f"{bcolors.WARNING}{bcolors.BOLD}If one of the tokens is ETH press Enter{bcolors.ENDC}")
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
            fee = FEES[0]
        elif fee == '2':
            fee = FEES[1]
        elif fee == '3':
            fee = FEES[2]
        elif fee == '4':
            fee = FEES[3]
        
        print()

        token0 = web3.toChecksumAddress(token0)
        token1 = web3.toChecksumAddress(token1)
        
        if token0 > token1:
            token0, token1 = token1, token0
        
        token0_symbol = get_symbol(token0, ETHEREUM, web3=web3)
        token1_symbol = get_symbol(token1, ETHEREUM, web3=web3)
        
        pool_address = factory_contract.functions.getPool(token0, token1, fee).call()
        
        if pool_address == ZERO_ADDRESS:
            message = 'Warning: No pool in Uniswap V3 for tokens: %s and %s, with Fee: %.2f%%' % (token0_symbol, token1_symbol, fee/10000)
            print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
            print()
            
        if token0 == WETH_ETH and eth == True:
            token0_symbol = 'ETH'
        
        if token1 == WETH_ETH and eth == True:
            token1_symbol = 'ETH'

        message = 'Pool: UniswapV3 %s/%s %.2f%%:' % (token0_symbol, token1_symbol, fee/10000)
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()
                
    else:
        print()
        nft_position = input_nft_position()
        if nft_position == None:
            break
        else:
            nft_position_id, token0, token0_symbol, token1, token1_symbol, fee, liquidity = nft_position
            pool_address = factory_contract.functions.getPool(token0, token1, fee).call()

    if pool_address != ZERO_ADDRESS:
        pool_contract = get_contract(pool_address, ETHEREUM, web3=web3, abi=ABI_POOL)

    token0_decimals = get_decimals(token0, ETHEREUM, web3=web3)
    token1_decimals = get_decimals(token1, ETHEREUM, web3=web3)
    
    if operation == '1':
        print(f"{bcolors.OKBLUE}---------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Add Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}---------------------{bcolors.ENDC}")
        print()

        pool_info = pool_price_data()
        if pool_info != None:
            min_price, max_price, tick_lower, tick_upper, current_price, price_range_option = pool_info

            print()
            amounts = tokens_amounts()
            
            if amounts != None:
                amount0_desired = amounts[0]
                amount1_desired = amounts[1]

                print()
                if price_range_option == '1':
                    message = ('The MIN price of %s per %s selected is %.18f' % (token1_symbol, token0_symbol, min_price)).rstrip('0').rstrip('.')
                    message += ('\nThe MAX price of %s per %s selected is %.18f' % (token1_symbol, token0_symbol, max_price)).rstrip('0').rstrip('.')
                else:
                    message = ('The MIN price of %s per %s selected is %.18f' % (token0_symbol, token1_symbol, min_price)).rstrip('0').rstrip('.')
                    message += ('\nThe MAX price of %s per %s selected is %.18f' % (token0_symbol, token1_symbol, max_price)).rstrip('0').rstrip('.')
                
                message += ('\nThe amount of %s desired is %.18f' % (token0_symbol, amount0_desired / (10**token0_decimals))).rstrip('0').rstrip('.')
                message += ('\nThe amount of %s desired is %.18f' % (token1_symbol, amount1_desired / (10**token1_decimals))).rstrip('0').rstrip('.')

                print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

                print()
                add_liquidity()
    
    elif operation == '2':
        print(f"{bcolors.OKBLUE}--------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Increase Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--------------------------{bcolors.ENDC}")
        print()
        
        if nft_position_id != None:
            amounts = tokens_amounts()
            
            if amounts != None:
                amount0_desired = amounts[0]
                amount1_desired = amounts[1]
                
                print()
                message = ('The amount of %s desired is %.18f' % (token0_symbol, amount0_desired / (10**token0_decimals))).rstrip('0').rstrip('.')
                message += ('\nThe amount of %s desired is %.18f' % (token1_symbol, amount1_desired / (10**token1_decimals))).rstrip('0').rstrip('.')

                print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

                print()
                increase_liquidity()
    
    elif operation == '3':
        print(f"{bcolors.OKBLUE}------------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Remove Liquidity ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}------------------------{bcolors.ENDC}")
        print()

        if nft_position_id != None:
            removed_liquidity, amount0_desired, amount1_desired = get_removed_liquidity(avatar_address, nft_position_id, liquidity, token0_symbol, token1_symbol, token0_decimals, token1_decimals, web3=web3)
            
            collect_option = 0
            if token0 == WETH_ETH or token1 == WETH_ETH:
                print('Collect ETH or WETH:')
                print('1- ETH')
                print('2- WETH')
                print()
            
                collect_option = input('Enter the option: ')
                while collect_option not in ['1','2']:
                    collect_option = input('Enter a valid option (1 or 2): ')
                
                if collect_option == '2':
                    if token0_symbol == 'ETH':
                        token0_symbol = 'WETH'
                    else:
                        token1_symbol = 'WETH'

            print()
            remove_liquidity()
    
    elif operation == '4':
        print(f"{bcolors.OKBLUE}--------------------{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--- Collect Fees ---{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}--------------------{bcolors.ENDC}")
        print()

        if nft_position_id != None:
            collect_option = 0
            if token0 == WETH_ETH or token1 ==WETH_ETH:
                print('Collect ETH or WETH:')
                print('1- ETH')
                print('2- WETH')
                print()

                collect_option = input('Enter the option: ')
                while collect_option not in ['1','2']:
                    collect_option = input('Enter a valid option (1 or 2): ')
                
                if collect_option == '2':
                    if token0_symbol == 'ETH':
                        token0_symbol = 'WETH'
                    else:
                        token1_symbol = 'WETH'
            print()
            collect()

    
    if json_file['transactions'] != []:
        json_file_download(json_file)
        break
    else:
        restart_end()