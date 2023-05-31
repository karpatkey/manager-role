from defi_protocols.functions import get_node, get_data, balance_of, get_symbol, get_decimals
from defi_protocols.constants import ETHEREUM, ZERO_ADDRESS
from defi_protocols.UniswapV3 import UNISWAPV3_ROUTER2, UNISWAPV3_QUOTER, ABI_QUOTER_V3, get_rate_uniswap_v3, underlying
from helper_functions.helper_functions import *
# thegraph queries
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import time
from decimal import Decimal
from tqdm import tqdm

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FEES
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Possible Fees for Uniwsap v3 Pools
FEES: list = [100, 500, 3000, 10000]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query_pool(token0, token1, fee):

    subgraph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    uniswapv3_transport=RequestsHTTPTransport(
        url=subgraph_url,
        verify=True,
        retries=3
    )
    client = Client(transport=uniswapv3_transport)

    token0 = token0.lower()
    token1 = token1.lower()

    query_string = '''
    query {{
    pools(where: {{token0_:{{id_in:["{token0}""{token1}"]}} token1_:{{id_in:["{token0}""{token1}"]}}feeTier: "{fee}"}})
        {{
            id
            token0{{id}}
            token1{{id}}
            feeTier
            volumeUSD
            totalValueLockedUSD
            createdAtTimestamp
        }}
    }}
    '''

    formatted_query_string = query_string.format(token0=token0, token1=token1, fee=fee)
    response = client.execute(gql(formatted_query_string))

    if response['pools'] != []:
        return response['pools']
    else:
        return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query_all_pools
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query_all_pools(min_tvl_usd=0, min_volume_usd=0):

    # Initialize subgraph
    subgraph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    uniswapv3_transport=RequestsHTTPTransport(
        url=subgraph_url,
        verify=True,
        retries=3
    )
    client = Client(transport=uniswapv3_transport)

    # all_found = False
    # skip = 0
    # num_pools_to_query = 1000
    # pools = []

    # try:
    #     while not all_found:
    #         query_string = '''
    #         query {{
    #         pools(first: {first}, skip: {skip}) {{
    #             id
    #             token0{{id}}
    #             token1{{id}}
    #         }}
    #         }}
    #         '''
            
    #         formatted_query_string = query_string.format(first=num_pools_to_query, skip=skip)
    #         response = client.execute(gql(formatted_query_string))

    #         for pool in response['pools']:
    #             pools.append(pool)

    #         if len(response['pools']) < 1000:
    #             all_found = True
    #         else:
    #             skip += 1000

    pools = {}
    last_timestamp = 0
    all_found = False

    web3 = get_node(ETHEREUM)

    try:
        query_string = '''
        query {{
        pools(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc) 
            {{
                id
                token0{{id}}
                token1{{id}}
                feeTier
                volumeUSD
                totalValueLockedUSD
                createdAtTimestamp
            }}
        }}
        '''

        formatted_query_string = query_string.format()
        response = client.execute(gql(formatted_query_string))

        for pool in response['pools']:
            volume_usd = float(pool['volumeUSD'])
            tvl_usd = float(pool['totalValueLockedUSD'])
            
            # try:
            #     total_supply_token0 = total_supply(pool['token0']['id'], 'latest', ETHEREUM, web3=web3)
            # except:
            #     continue
            
            # try:
                # total_supply_token1 = total_supply(pool['token1']['id'], 'latest', ETHEREUM, web3=web3)
            # except:
            #     continue

            # if volume_usd > 0 and tvl_usd > 100 and total_supply_token0 > 0 and total_supply_token1 > 0:
            if volume_usd >= min_volume_usd and tvl_usd >= min_tvl_usd:
                pools[pool['id']] = [web3.toChecksumAddress(pool['token0']['id']), web3.toChecksumAddress(pool['token1']['id']), int(pool['feeTier']), volume_usd, tvl_usd]

        if len(response['pools']) < 1000:
            all_found = True
        else:
            last_timestamp = int(pool['createdAtTimestamp']) - 1
    
    except Exception as Ex:
        print(Ex)
    
    if not all_found and last_timestamp > 0:

        try:
            while not all_found:
                query_string = '''
                query {{
                pools(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc
                where: {{createdAtTimestamp_gt: {last_timestamp} }})
                    {{
                        id
                        token0{{id}}
                        token1{{id}}
                        feeTier
                        volumeUSD
                        totalValueLockedUSD
                        createdAtTimestamp
                    }}
                }}
                '''

                formatted_query_string = query_string.format(last_timestamp=last_timestamp)
                response = client.execute(gql(formatted_query_string))

                for pool in response['pools']:
                    volume_usd = float(pool['volumeUSD'])
                    tvl_usd = float(pool['totalValueLockedUSD'])
                    
                    # try:
                    #     total_supply_token0 = total_supply(pool['token0']['id'], 'latest', ETHEREUM, web3=web3)
                    # except:
                    #     continue
                    
                    # try:
                    #     total_supply_token1 = total_supply(pool['token1']['id'], 'latest', ETHEREUM, web3=web3)
                    # except:
                    #     continue

                    # if volume_usd > 0 and tvl_usd > 100 and total_supply_token0 > 0 and total_supply_token1 > 0:
                    if volume_usd >= min_volume_usd and tvl_usd >= min_tvl_usd:
                        pools[pool['id']] = [web3.toChecksumAddress(pool['token0']['id']), web3.toChecksumAddress(pool['token1']['id']), int(pool['feeTier']), volume_usd, tvl_usd]

                if len(response['pools']) < 1000:
                    all_found = True
                else:
                    last_timestamp = int(pool['createdAtTimestamp']) - 1
                    time.sleep(5)
        
        except Exception as Ex:
            print(Ex)
        
    return pools


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# select_path
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def select_path(paths, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)
    
    if isinstance(paths[0], list):
        print('Select the path: ')
        i = 1
        valid_path_options = []
        path_strings = []
        for path in paths:
            path_symbols = [get_symbol(path_token, ETHEREUM, web3=web3) for path_token in path]
            path_string = '[{}]'.format('->'.join(path_symbols))
            path_strings.append(path_string)
            print('%d- %s' % (i, path_string))
            valid_path_options.append(i)
            i += 1
        
        print()
        path_option = input('Enter the path: ')
        while int(path_option) not in valid_path_options:
            message = 'Enter a valid option (' + ','.join(str(option) for option in valid_path_options) + '): '
            path_option = input(message)
        
        print()
        # return list(paths)[int(path_option)-1], get_rate(list(paths)[int(path_option)-1], web3=web3)
        path = list(paths)[int(path_option)-1]
        path_string = path_strings[int(path_option)-1]
    
    else:
        path_symbols = [get_symbol(path_token, ETHEREUM, web3=web3) for path_token in paths]
        path_string = '[{}]'.format('->'.join(path_symbols))
        path = paths
        # return paths, get_rate(paths, web3=web3)
    
    message = 'Path: %s\n' % path_string
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
    
    return paths


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# set_min_amount_out_and_fee
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def set_min_amount_out_and_fee(selected_token, selected_swap_token, amount, selected_swap_token_symbol, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    # amount_out_min = input('Enter the MIN amount out: ')
    # while True:
    #     try:
    #         amount_out_min = float(amount_out_min)

    #         return amount_out_min
    #     except:
    #         amount_out_min = input('Enter a valid amount: ')
    
    quoter_contract = get_contract(UNISWAPV3_QUOTER, ETHEREUM, web3=web3, abi=ABI_QUOTER_V3)

    amounts_out = []
    for fee in FEES:
        try:
            amounts_out.append(quoter_contract.functions.quoteExactInputSingle(selected_token, selected_swap_token, int(fee), int(amount), int(0)).call())
        except:
            amounts_out.append(0)
    
    amount_out = max(amounts_out)
    fee = FEES[amounts_out.index(amount_out)]

    selected_swap_token_decimals = get_decimals(selected_swap_token, ETHEREUM, web3=web3)

    print(f"{bcolors.OKBLUE}{bcolors.BOLD}Best quote results:{bcolors.ENDC}")
    message = str('Amount Out: %.18f' % (amount_out/10**selected_swap_token_decimals)).rstrip('0').rstrip('.')
    message += '\nFee: %s%%\n' % (str(fee/10000))
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

    message = 'If you want to select the MAX Amount Out of %s enter \"max\"' % selected_swap_token_symbol
    print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
    input_amount_out = input('Enter the Amount Out of %s: ' % selected_swap_token_symbol)
    while True:
        try:
            if input_amount_out == 'max':
                input_amount_out = amount_out
            else:
                input_amount_out = float(input_amount_out)
                input_amount_out = input_amount_out * (10**selected_swap_token_decimals)
                if input_amount_out > amount_out:
                    print()
                    message = str('Input Amount Out must be lower than %.18f' % (amount_out/10**selected_swap_token_decimals)).rstrip('0').rstrip('.')
                    message += (' %s\n') % selected_swap_token_symbol
                    print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                    raise Exception
                else:
                    amount_out = input_amount_out
            break
        except:
            input_amount_out = input('Enter a valid amount: ')

    return [amount_out, fee]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# select_fee
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def select_fee(selected_token, selected_swap_token, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    print('Select the Fee for the UniswapV3 %s/%s pool: ' % (selected_token, selected_swap_token))
    print()
    print('1- 0.01%')
    print('2- 0.05%')
    print('3- 0.3%')
    print('4- 1%')
    print()
    
    fee_option = input('Enter the Fee: ')
    while fee_option not in ['1','2','3','4']:
        fee_option = input('Enter a valid option (1, 2, 3 or 4): ')
    
    if fee_option == '1':
        return FEES[0]
    elif fee_option == '2':
        return FEES[1]
    elif fee_option == '3':
        return FEES[2]
    elif fee_option == '4':
        return FEES[3]


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_rate
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_rate(path, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    result_rates = []
    path_symbols = [get_symbol(path_token, ETHEREUM, web3=web3) for path_token in path]
    path_string = '[{}]'.format(','.join(path_symbols))
    message = 'Searching for the best rate with the path %s...\n' % path_string
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}{message}{bcolors.ENDC}")
    for i in tqdm(range(len(path)-1)):
        rates = []
        for fee in tqdm(FEES):
            rate = get_rate_uniswap_v3(path[i], path[i+1], 'latest', ETHEREUM, web3=web3, fee=fee)
            if rate != None:
                rates.append(rate)
        
        max_rate = max(rates)
        result_rates.append(max_rate)

    print()

    result_rate = 1
    for rate in result_rates:
        result_rate = result_rate * rate
    
    return result_rate


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# swap_selected_token_v2
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def swap_selected_token_v2(avatar_address, roles_mod_address, path, amount_out_min, token, token_balance, swap_token, json_file, web3=None):

    approve_token(avatar_address, roles_mod_address, token, UNISWAPV3_ROUTER2, json_file, web3=web3)
    approve_token(avatar_address, roles_mod_address, swap_token, UNISWAPV3_ROUTER2, json_file, web3=web3)
 
    tx_data = get_data(UNISWAPV3_ROUTER2, 'swapExactTokensForTokens', [int(round(token_balance)), int(round(amount_out_min)), path, avatar_address], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(roles_mod_address, UNISWAPV3_ROUTER2, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# swap_selected_token_v3
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def swap_selected_token_v3(avatar_address, roles_mod_address, fee, amount_out_min, token, token_balance, swap_token, json_file, web3=None):

    approve_token(avatar_address, roles_mod_address, token, UNISWAPV3_ROUTER2, json_file, web3=web3)
    approve_token(avatar_address, roles_mod_address, swap_token, UNISWAPV3_ROUTER2, json_file, web3=web3)
 
    tx_data = get_data(UNISWAPV3_ROUTER2, 'exactInputSingle', [[token, swap_token, int(fee), avatar_address, int(round(token_balance)), int(round(amount_out_min)), 0]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(roles_mod_address, UNISWAPV3_ROUTER2, tx_data, 0, json_file, web3=web3)


# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# # swap_selected_token
# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# def swap_selected_token(avatar_address, roles_mod_address, path, rate, token, token_balance, token_symbol, swap_token, swap_token_symbol, json_file, web3=None):
    
#     if web3 is None:
#         web3 = get_node(ETHEREUM)

#     expected_amount = rate * token_balance
#     message = ('Expected amount of %s for the %.18f' % (swap_token_symbol, token_balance)).rstrip('0').rstrip('.')
#     message += (' of %s is: %.18f' % (token_symbol, expected_amount)).rstrip('0').rstrip('.')
#     print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

#     print()

#     print('Do you wish to proceed: ')
#     print('1- Yes')
#     print('2- No')
#     print()

#     option = input('Enter the option: ')
#     while option not in ['1','2']:
#         option = input('Enter a valid option (1, 2): ')
    
#     if option == '1':

#         while True:
#             print()
#             print(f"{bcolors.WARNING}{bcolors.BOLD}The percentage must be greater than 0% and lower or equal to 100%{bcolors.ENDC}")
#             slippage = input('Enter the MAX percentage of slippage tolerance: ')
#             while True:
#                 try:
#                     slippage = float(slippage)
#                     if slippage <= 0 or slippage > 100:
#                         raise Exception
#                     else:
#                         break
#                 except:
#                     slippage = input('Enter a valid percentage: ')
            
#             print()

#             amount_out_min = (100 - slippage) * expected_amount / 100
#             message = ('The MIN amount of %s for the %.18f' % (swap_token_symbol, token_balance)).rstrip('0').rstrip('.')
#             message += (' of %s is: %.18f' % (token_symbol, amount_out_min)).rstrip('0').rstrip('.')
#             print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

#             print()
#             print('Do you wish to proceed: ')
#             print('1- Yes')
#             print('2- No')
#             print()

#             option = input('Enter the option: ')
#             while option not in ['1','2']:
#                 option = input('Enter a valid option (1, 2): ')
            
#             if option == '1':
#                 approve_token(avatar_address, roles_mod_address, token, UNISWAPV3_ROUTER2, json_file, web3=web3)
#                 approve_token(avatar_address, roles_mod_address, swap_token, UNISWAPV3_ROUTER2, json_file, web3=web3)
                
#                 token_balance = token_balance * (10**get_decimals(token, ETHEREUM, web3=web3))
#                 amount_out_min = amount_out_min * (10**get_decimals(swap_token, ETHEREUM, web3=web3))
#                 tx_data = get_data(UNISWAPV3_ROUTER2, 'swapExactTokensForTokens', [int(round(token_balance)), int(round(amount_out_min)), path, avatar_address], ETHEREUM, web3=web3)
#                 if tx_data is not None:
#                     add_txn_with_role(roles_mod_address, UNISWAPV3_ROUTER2, tx_data, 0, json_file, web3=web3)
                
#                 break


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_amount1
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_amount1(positions_nft_contract, pool_contract, nft_position_id, amount0_desired, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    position_data = positions_nft_contract.functions.positions(nft_position_id).call()
    tick_lower = position_data[5]
    tick_upper = position_data[6]

    sqrt_price_x96 = pool_contract.functions.slot0().call()[0]

    amount1_desired = Decimal(amount0_desired * sqrt_price_x96 * 1.0001**(tick_upper/2)*(sqrt_price_x96-1.0001**(tick_lower/2)*(2**96)))/Decimal((2**96) * (1.0001**(tick_upper/2)*(2**96)-sqrt_price_x96))

    return int(amount1_desired)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_amount0
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_amount0(positions_nft_contract, pool_contract, nft_position_id, amount1_desired, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    position_data = positions_nft_contract.functions.positions(nft_position_id).call()
    tick_lower = position_data[5]
    tick_upper = position_data[6]

    sqrt_price_x96 = pool_contract.functions.slot0().call()[0]

    amount0_desired = Decimal(amount1_desired * (2**96) * (1.0001**(tick_upper/2)*(2**96)-sqrt_price_x96)) / (Decimal(sqrt_price_x96 * 1.0001**(tick_upper/2)*(sqrt_price_x96-1.0001**(tick_lower/2)*(2**96))))

    return int(amount0_desired)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_amount1_mint
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_amount1_mint(pool_contract, tick_lower, tick_upper, amount0_desired, current_price=0, token0_decimals=0, token1_decimals=0, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    if pool_contract == None:
        current_price = Decimal(current_price)
        sqrt_price = current_price.sqrt()
        amount0_desired = amount0_desired / (10**token0_decimals)
        amount1_desired = int(Decimal(amount0_desired) * sqrt_price * Decimal(1.0001)**Decimal(tick_upper/2)*Decimal(10**((token1_decimals+token0_decimals)/2))*(sqrt_price*Decimal(10**((token1_decimals-token0_decimals)/2))-Decimal(1.0001)**Decimal(tick_lower/2))/(Decimal(1.0001)**Decimal(tick_upper/2)-sqrt_price*Decimal(10**((token1_decimals-token0_decimals)/2))))
    else:
        sqrt_price_x96 = pool_contract.functions.slot0().call()[0]
        amount1_desired = Decimal(amount0_desired * sqrt_price_x96 * 1.0001**(tick_upper/2)*(sqrt_price_x96-1.0001**(tick_lower/2)*(2**96)))/Decimal((2**96) * (1.0001**(tick_upper/2)*(2**96)-sqrt_price_x96))

    return int(amount1_desired)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_amount0_mint
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_amount0_mint(pool_contract, tick_lower, tick_upper, amount1_desired, current_price=0, token0_decimals=0, token1_decimals=0, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    
    if pool_contract == None:
        current_price = Decimal(current_price)
        sqrt_price = current_price.sqrt()
        amount1_desired = amount1_desired / (10**token1_decimals)
        amount0_desired = int(Decimal(amount1_desired) * (Decimal(1.0001)**Decimal(tick_upper/2)-sqrt_price*Decimal(10**((token1_decimals-token0_decimals)/2))) / (sqrt_price * Decimal(1.0001)**Decimal(tick_upper/2)*Decimal(10**((token1_decimals+token0_decimals)/2))*(sqrt_price*Decimal(10**((token1_decimals-token0_decimals)/2))-Decimal(1.0001)**Decimal(tick_lower/2))))
    else:
        sqrt_price_x96 = pool_contract.functions.slot0().call()[0]
        amount0_desired = Decimal(amount1_desired * (2**96) * (1.0001**(tick_upper/2)*(2**96)-sqrt_price_x96)) / (Decimal(sqrt_price_x96 * 1.0001**(tick_upper/2)*(sqrt_price_x96-1.0001**(tick_lower/2)*(2**96))))

    return int(amount0_desired)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_selected_token_balance
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_selected_token_balance(avatar_address, token_address, token_symbol, token_decimals, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    selected_token_balance = 0

    selected_token_balance = balance_of(avatar_address, token_address, 'latest', ETHEREUM, decimals=False, web3=web3)
    
    if selected_token_balance == 0:
        message = 'Avatar Safe has no remaining balance of %s' % (token_symbol)
        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()
    else:
        message = ('The balance of %s in the Avatar Safe is %.18f' % (token_symbol, selected_token_balance / (10**token_decimals))).rstrip('0').rstrip('.')
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
    
    return selected_token_balance


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_removed_liquidity
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_removed_liquidity(avatar_address, nft_position_id, liquidity, token0_symbol, token1_symbol, token0_decimals, token1_decimals, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    nft_position_balances = underlying(avatar_address, nft_position_id, 'latest', ETHEREUM, web3=web3, decimals=False)
    
    if nft_position_balances == None:
        print(f"{bcolors.FAIL}{bcolors.BOLD}Error while retrieving the position balances{bcolors.ENDC}")
        exit()

    message = ('The balance of %s in the NFT Position is %.18f' % (token0_symbol, nft_position_balances[0][1] / (10**token0_decimals))).rstrip('0').rstrip('.')
    message += ('\nThe balance of %s in the NFT Position is %.18f' % (token1_symbol, nft_position_balances[1][1] / (10**token1_decimals))).rstrip('0').rstrip('.')
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
    print()

    print(f"{bcolors.WARNING}{bcolors.BOLD}The percentage must be greater than 0% and lower or equal to 100%{bcolors.ENDC}")
    percentage_removed_liquidity = input('Enter the percentage of liquidity to remove: ')
    while True:
        try:
            percentage_removed_liquidity = float(percentage_removed_liquidity)
            if percentage_removed_liquidity <= 0 or percentage_removed_liquidity > 100:
                raise Exception
            else:
                break
        except:
            percentage_removed_liquidity = input('Enter a valid percentage: ')

    print()
    amount0_desired = nft_position_balances[0][1] * percentage_removed_liquidity / 100 
    amount1_desired = nft_position_balances[1][1] * percentage_removed_liquidity / 100 
    message = ('The balance of %s to be removed is %.18f' % (token0_symbol, amount0_desired / (10**token0_decimals))).rstrip('0').rstrip('.')
    message += ('\nThe balance of %s to be removed is %.18f' % (token1_symbol, amount1_desired / (10**token1_decimals))).rstrip('0').rstrip('.')
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
    print()

    removed_liquidity = liquidity * percentage_removed_liquidity / 100
    
    return removed_liquidity, amount0_desired, amount1_desired


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_amounts_desired
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_amounts_desired(avatar_address, pool_contract, operation, token_option, selected_token_balance, selected_token_decimals, selected_token_symbol, token0, token0_decimals, token0_symbol, token1, token1_decimals, token1_symbol, positions_nft_contract, nft_position_id=0, tick_lower=0, tick_upper=0, current_price=0, web3=None):

    amount0_desired = 0
    amount1_desired = 0
    message = 'If you want to select the MAX amount of %s enter \"max\"' %  (selected_token_symbol)
    print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
    
    if token_option == '1':
        amount0_desired = input('Enter the Amount of %s: ' % token0_symbol)
    elif token_option == '2':
        amount1_desired = input('Enter the Amount of %s: ' % token1_symbol)

    while True:
        try:
            if token_option == '1':
                if amount0_desired == 'max':
                    amount0_desired = selected_token_balance
                else:
                    amount0_desired = float(amount0_desired) * (10**token0_decimals)
                
                if amount0_desired > selected_token_balance:
                    print()
                    message = ('Insufficient balance of %s in Avatar Safe\nThe balance of %s is %.18f' % (selected_token_symbol, selected_token_symbol, selected_token_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
                    print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                    print()
                    raise Exception
                
                if operation == '1':
                    amount1_desired = get_amount1_mint(pool_contract, tick_lower, tick_upper, amount0_desired, current_price=current_price, token0_decimals=token0_decimals, token1_decimals=token1_decimals, web3=web3)
                else:
                    amount1_desired = get_amount1(positions_nft_contract, pool_contract, nft_position_id, amount0_desired, web3=web3)
                
                if token1_symbol == 'ETH':
                    token1_balance = balance_of(avatar_address, ZERO_ADDRESS, 'latest', ETHEREUM, web3=web3, decimals=False)
                else:
                    token1_balance = balance_of(avatar_address, token1, 'latest', ETHEREUM, web3=web3, decimals=False)
                
                if token1_balance < amount1_desired:
                    print()
                    message = ('Insufficient balance of %s in Avatar Safe: %.18f' % (token1_symbol, balance_of(avatar_address, token1, 'latest', ETHEREUM, web3=web3))).rstrip('0').rstrip('.')
                    message += (' %s\nThe desired amount of %s is %.18f' % (token1_symbol, token1_symbol, amount1_desired / (10**token1_decimals))).rstrip('0').rstrip('.')
                    print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                    print()
                    raise Exception
                
            elif token_option == '2':
                if amount1_desired == 'max':
                    amount1_desired = selected_token_balance
                else:
                    amount1_desired = float(amount1_desired) * (10**token1_decimals)

                if amount1_desired > selected_token_balance:
                    print()
                    message = ('Insufficient balance of %s in Avatar Safe\nThe balance of %s is %.18f' % (selected_token_symbol, selected_token_symbol, selected_token_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
                    print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                    print()
                    raise Exception
     
                if operation == '1':
                    amount0_desired = get_amount0_mint(pool_contract, tick_lower, tick_upper, amount1_desired, current_price=current_price, token0_decimals=token0_decimals, token1_decimals=token1_decimals, web3=web3)
                else:
                    amount0_desired = get_amount0(positions_nft_contract, pool_contract, nft_position_id, amount1_desired, web3=web3)
                
                if token0_symbol == 'ETH':
                    token0_balance = balance_of(avatar_address, ZERO_ADDRESS, 'latest', ETHEREUM, web3=web3, decimals=False)
                else:
                    token0_balance = balance_of(avatar_address, token0, 'latest', ETHEREUM, web3=web3, decimals=False)
                
                if token0_balance < amount0_desired:
                    print()
                    message = ('Insufficient balance of %s in Avatar Safe: %.18f' % (token0_symbol, balance_of(avatar_address, token0, 'latest', ETHEREUM, web3=web3))).rstrip('0').rstrip('.')
                    message += (' %s\nThe desired amount of %s is %.18f' % (token0_symbol, token0_symbol, amount0_desired / (10**token0_decimals))).rstrip('0').rstrip('.')
                    print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                    print()
                    raise Exception
            break
            
        except:
            if token_option == '1':
                amount0_desired = input('Enter a valid amount: ')
            elif token_option == '2':
                amount1_desired = input('Enter a valid amount: ')
    
    return amount0_desired, amount1_desired
