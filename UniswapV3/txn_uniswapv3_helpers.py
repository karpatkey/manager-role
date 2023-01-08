from defi_protocols.functions import get_node, get_data, get_contract, get_decimals, balance_of
from defi_protocols.constants import ETHEREUM, WETH_ETH, ZERO_ADDRESS
from defi_protocols.UniswapV3 import POSITIONS_NFT, FEES, UNISWAPV3_ROUTER2, get_rate_uniswap_v3, underlying
# thegraph queries
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json
from pathlib import Path
import os
import time
from decimal import Decimal

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
COMP = '0xc00e94Cb662C3520282E6f5717214004A7f26888'
AAVE = '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'
RETH2 = '0x20BC832ca081b91433ff6c17f85701B6e92486c5'
SWISE = '0x48C3399719B582dD63eB5AADf12A40B4C3f52FA2'
SETH2 = '0xFe2e637202056d30016725477c5da089Ab0A043A'

MAX_TOKEN_AMOUNT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

TOKEN_PROXY = '0xa2327a938Febf5FEC13baCFb16Ae10EcBc4cbDCF'

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
# approve_tokens
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def approve_tokens(avatar_address, roles_mod_address, token0, token1, spender_address, json_file, web3=None, eth=False):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    # approve Token0
    if (token0 == WETH_ETH and eth == False) or token0 != WETH_ETH:
        token0_contract = get_contract(token0, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
        if token0_contract.functions.allowance(avatar_address, spender_address).call() == 0:
            tx_data = get_data(token0, 'approve', [spender_address, MAX_TOKEN_AMOUNT], ETHEREUM, abi_address=TOKEN_PROXY, web3=web3)
            if tx_data is not None:
                add_txn_with_role(roles_mod_address, token0, tx_data, 0, json_file, web3=web3)

    # approve Token1
    if (token1 == WETH_ETH and eth == False) or token1 != WETH_ETH:
        token1_contract = get_contract(token1, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
        if token1_contract.functions.allowance(avatar_address, spender_address).call() == 0:
            tx_data = get_data(token1, 'approve', [spender_address, MAX_TOKEN_AMOUNT], ETHEREUM, abi_address=TOKEN_PROXY, web3=web3)
            if tx_data is not None:
                add_txn_with_role(roles_mod_address, token1, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_txn_with_role
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_txn_with_role(roles_mod_address, to_address, tx_data, eth_value, json_file, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [to_address, int(eth_value), tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
    if exec_data is not None:   
        json_file['transactions'].append(
            {
                'to': roles_mod_address,
                'data': exec_data,
                'value': str(0)
            }
        )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_rate
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_rate(path, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    result_rates = []
    for i in range(len(path)-1):
        rates = []
        for fee in FEES:
            rate = get_rate_uniswap_v3(path[i], path[i+1], 'latest', ETHEREUM, web3=web3, fee=fee)
            if rate != None:
                rates.append(rate)
        
        min_rate = min(rates)
        result_rates.append(min_rate)

    result_rate = 1

    for rate in result_rates:
        result_rate = result_rate * rate
    
    return result_rate


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# json_file_download
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def json_file_download(json_file):

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


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# swap_selected_token
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def swap_selected_token(avatar_address, roles_mod_address, path, token, token_balance, token_symbol, swap_token, swap_token_symbol, json_file, web3=None):
    
    if web3 is None:
        web3 = get_node(ETHEREUM)

    rate = get_rate(path)

    expected_amount = rate * token_balance
    message = ('Expected amount of %s for the %.18f' % (swap_token_symbol, token_balance)).rstrip('0').rstrip('.')
    message += (' of %s is: %.18f' % (token_symbol, expected_amount)).rstrip('0').rstrip('.')
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

    print()

    print('Do you wish to proceed: ')
    print('1- Yes')
    print('2- No')
    print()

    option = input('Enter the option: ')
    while option not in ['1','2']:
        option = input('Enter a valid option (1, 2): ')
    
    if option == '1':

        while True:
            print()
            print(f"{bcolors.WARNING}{bcolors.BOLD}The percentage must be greater than 0% and lower or equal to 100%{bcolors.ENDC}")
            slippage = input('Enter the MAX percentage of slippage tolerance: ')
            while True:
                try:
                    slippage = float(slippage)
                    if slippage <= 0 or slippage > 100:
                        raise Exception
                    else:
                        break
                except:
                    slippage = input('Enter a valid percentage: ')
            
            print()

            amount_out_min = (100 - slippage) * expected_amount / 100
            message = ('The MIN amount of %s for the %.18f' % (swap_token_symbol, token_balance)).rstrip('0').rstrip('.')
            message += (' of %s is: %.18f' % (token_symbol, amount_out_min)).rstrip('0').rstrip('.')
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

            print()
            print('Do you wish to proceed: ')
            print('1- Yes')
            print('2- No')
            print()

            option = input('Enter the option: ')
            while option not in ['1','2']:
                option = input('Enter a valid option (1, 2): ')
            
            print()
            if option == '1':
                approve_tokens(avatar_address, roles_mod_address, token, swap_token, UNISWAPV3_ROUTER2, json_file, web3=web3)
                
                token_balance = token_balance * (10**get_decimals(token, ETHEREUM, web3=web3))
                amount_out_min = amount_out_min * (10**get_decimals(swap_token, ETHEREUM, web3=web3))
                tx_data = get_data(UNISWAPV3_ROUTER2, 'swapExactTokensForTokens', [int(round(token_balance)), int(round(amount_out_min)), path, avatar_address], ETHEREUM, web3=web3)
                if tx_data is not None:
                    add_txn_with_role(roles_mod_address, tx_data, 0, json_file, web3=web3)
                
                break


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# restart_end
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def restart_end():

    print(f"{bcolors.WARNING}{bcolors.BOLD}No transactions were recorded{bcolors.ENDC}")
    print()
    print('Do you wish to restart?')
    print('1- Yes')
    print('2- No')
    print()

    option = input('Enter the option: ')
    while option not in ['1','2']:
        option = input('Enter a valid option (1, 2): ')
    
    if option == '2':
        exit()
    else:
        print()


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