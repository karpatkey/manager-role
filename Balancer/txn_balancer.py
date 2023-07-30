from defi_protocols.functions import get_contract, get_symbol, get_node, get_decimals
from defi_protocols.constants import ETHEREUM, B_80BAL_20_WETH_ETH, ZERO_ADDRESS
from defi_protocols.Balancer import (VAULT, VEBAL, ABI_VAULT, get_gauge_addresses, get_lptoken_data) 
# thegraph queries
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path
import os
import json
import eth_abi

BALANCER_QUERIES = '0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5'

# ABI Balancer Queries - queryExit, queryJoin
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]'

# LP Token ABI - getPoolId, POOL_ID, decimals, getMainToken, version, name
ABI_LPTOKEN = '[{"inputs":[],"name":"getPoolId","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"POOL_ID","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getMainToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"version","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query_pools
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query_pools():

    result = []
    skip = 0
    while True:
    # Initialize subgraph
        subgraph_url = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2"
        balancer_transport=RequestsHTTPTransport(
            url=subgraph_url,
            verify=True,
            retries=3
        )
        client = Client(transport=balancer_transport)

        query_string = '''
        query {{
        pools(where: {{totalLiquidity_gte: 1000}}, first: {first}, skip: {skip}) {{
            id
            address
            poolTypeVersion
            poolType
        }}
        }}
        '''
        num_pools_to_query = 1000
        formatted_query_string = query_string.format(first=num_pools_to_query, skip=skip)
        response = client.execute(gql(formatted_query_string))
        result.extend(response['pools'])

        if len(response['pools']) < 1000:
            break
        else:
            skip = 1000

    return result


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query_pool_type
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query_pool_type(pool_id):

    # Initialize subgraph
    subgraph_url = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2"
    balancer_transport=RequestsHTTPTransport(
        url=subgraph_url,
        verify=True,
        retries=3
    )
    client = Client(transport=balancer_transport)

    query_string = '''
    query {{
    pool(id: {pool_id}) {{
        poolType
    }}
    }}
    '''
    formatted_query_string = query_string.format(pool_id="\""+pool_id+"\"")
    response = client.execute(gql(formatted_query_string))

    return response['pool']['poolType']


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# is_deprecated
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def is_deprecated(pool_id, lptoken_address, pool_tokens, blockchain, web3):

    amounts = []

    for pool_token in pool_tokens:
        if pool_token != lptoken_address:
            amounts.append(10**get_decimals(pool_token, blockchain, web3=web3))

    join_kind = 1 # EXACT_TOKENS_IN_FOR_BPT_OUT
    minimum_bpt = 0
    abi = ['uint256', 'uint256[]', 'uint256']
    data = [join_kind, amounts, minimum_bpt]
    user_data = '0x' + eth_abi.encode(abi, data).hex()

    balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, abi=ABI_BALANCER_QUERIES)

    try:
        join_pool = balancer_queries.functions.queryJoin(pool_id, ZERO_ADDRESS, ZERO_ADDRESS, [pool_tokens, amounts, user_data, False]).call()
    except Exception as e:
        print(e)
        return True
    
    if join_pool[0] == 0:
        return True
    else:
        return False


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_pool_tokens
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_pool_tokens(vault_contract, pool_id, lptoken_address, pool_tokens_array, blockchain, web3):
    
    pool_tokens_data = vault_contract.functions.getPoolTokens(pool_id).call()
    pool_tokens = pool_tokens_data[0]

    for i in range(len(pool_tokens)):
            
        if pool_tokens[i] == lptoken_address:
            continue

        pool_token_address = pool_tokens[i]
        pool_token_symbol = get_symbol(pool_token_address, blockchain)

        pool_token_contract = get_contract(pool_token_address, blockchain, web3=web3, abi=ABI_LPTOKEN)
        try:
            token_pool_id = '0x' + pool_token_contract.functions.getPoolId().call().hex()
        except:
            try:
                token_pool_id = '0x' + pool_token_contract.functions.POOL_ID().call().hex()
            except:
                token_pool_id = '0x'
        
        if token_pool_id != '0x':
            pool_tokens_array.append({
                'address': pool_token_address,
                'symbol': pool_token_symbol,
                'id': token_pool_id,
            })

            pool_token_type = subgraph_query_pool_type(token_pool_id)
            
            try:
                pool_token_version = pool_token_contract.functions.version().call()
            except:
                pool_token_version = None
            
            pool_token_name = pool_token_contract.functions.name().call()

            # pool_token_version != None filters out old bb-a-USD pools and 'bao' not in pool_token_name.lower() filters out bao pools
            if any(pool_token_type in itype for itype in ['ComposableStable', 'GearboxLinear']) and pool_token_version != None and 'bao' not in pool_token_name.lower():
                add_pool_tokens(vault_contract, token_pool_id, pool_token_address, pool_tokens_array, blockchain, web3)
            else:
                try:
                    underlying_token = pool_token_contract.functions.getMainToken().call()
                    underlying_token_contract = get_contract(underlying_token, blockchain, web3=web3, abi=ABI_LPTOKEN)
                    try:
                        underlying_token_pool_id = '0x' + underlying_token_contract.functions.getPoolId().call().hex()
                    except:
                        underlying_token_pool_id = '0x'

                    pool_tokens_array.append({
                        'address': underlying_token,
                        'symbol': get_symbol(underlying_token, blockchain, web3=web3),
                        'id': underlying_token_pool_id
                    })
                
                except:
                    pass
        else:
            pool_tokens_array.append({
                'address': pool_token_address,
                'symbol': pool_token_symbol,
                'id': token_pool_id,
            })


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data(blockchain):

    result = []

    web3 = get_node(blockchain)

    pools = subgraph_query_pools()

    vault_contract = get_contract(VAULT, blockchain, web3=web3, abi=ABI_VAULT)
    
    j = 0
    deprecated = 0
    print(len(pools))
    for pool in pools:
        gauge_address = ZERO_ADDRESS

        lptoken_address = vault_contract.functions.getPool(pool['id']).call()[0]

        pool_tokens_data = vault_contract.functions.getPoolTokens(pool['id']).call()
        pool_tokens = pool_tokens_data[0]

        if is_deprecated(pool['id'], lptoken_address, pool_tokens, blockchain, web3):
            deprecated += 1
            continue

        try:
            gauge_address = get_gauge_addresses(blockchain, 'latest', web3, lptoken_address)[0]
        except:
            gauge_address = ZERO_ADDRESS
        
        pool_name = get_symbol(lptoken_address, blockchain, web3=web3)
        
        pool_tokens_array = []
        add_pool_tokens(vault_contract, pool['id'], lptoken_address, pool_tokens_array, blockchain, web3)
        
        result.append({
            'bpt': lptoken_address,
            'id': pool['id'],
            'name': pool_name, 
            'type': pool['poolType'],
            'gauge': gauge_address,
            'tokens': pool_tokens_array
        })

        print(j)
        j += 1
    
    print(deprecated)
    
    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/balancer_data.json', 'w') as balancer_data_file:
        json.dump(result, balancer_data_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool(pools_data, lptoken_address):

    for pool_data in pools_data:
        if pool_data == lptoken_address:
            return pool_data

    return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pool_data(lptoken_address):

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/balancer_data.json', 'r') as balancer_data_file:
        # Reading from json file
        balancer_data = json.load(balancer_data_file)
        
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_balancer.json', 'r') as txn_balancer_file:
            # Reading from json file
            txn_balancer = json.load(txn_balancer_file)
    except:
        txn_balancer = {}
    
    web3 = get_node(ETHEREUM)
    
    lptoken_address = web3.to_checksum_address(lptoken_address)
    pool = search_pool(balancer_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Balancer Data File' % lptoken_address)
        return
    

    txn_balancer[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    for token in balancer_data[lptoken_address]['tokens']:
        if token != lptoken_address:
            txn_balancer[lptoken_address]['approve'].append({
                'token': token,
                'spender': VAULT
            })
    
    if balancer_data[lptoken_address]['gauge'] != ZERO_ADDRESS:
        txn_balancer[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': balancer_data[lptoken_address]['gauge']
        })
    
    txn_balancer[lptoken_address]['functions'].append({
        'signature': 'joinPool(bytes32,address,address,(address[],uint256[],bytes,bool))',
        'target address': VAULT,
        'avatar address arguments': [1, 2],
        'bytes32': balancer_data[lptoken_address]['pool id']
    })

    txn_balancer[lptoken_address]['functions'].append({
        'signature': 'exitPool(bytes32,address,address,(address[],uint256[],bytes,bool))',
        'target address': VAULT,
        'avatar address arguments': [1, 2],
        'bytes32': balancer_data[lptoken_address]['pool id']
    })

    # result_item['functions'].append({
    #     'signature': 'swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256)',
    #     'target address': VAULT,
    #     'avatar address arguments': [[1,0], [1,2]]
    # })

    # result_item['functions'].append({
    #     'signature': 'batchSwap(uint8,(bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)',
    #     'target address': VAULT,
    #     'avatar address arguments': [[3,0], [3,2]]
    # })

    if balancer_data[lptoken_address]['gauge'] != ZERO_ADDRESS:
        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'deposit(uint256)',
            'target address': balancer_data[lptoken_address]['gauge'],
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'withdraw(uint256)',
            'target address': balancer_data[lptoken_address]['gauge'],
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'claim_rewards()',
            'target address': balancer_data[lptoken_address]['gauge'],
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'mint(address)',
            'target address': '0x239e55f427d44c3cc793f49bfb507ebe76638a2b',
            'address[0]': balancer_data[lptoken_address]['gauge']
        })

    if lptoken_address == B_80BAL_20_WETH_ETH:
        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'create_lock(uint256,uint256)',
            'target address': VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'increase_amount(uint256)',
            'target address': VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'increase_unlock_time(uint256)',
            'target address': VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'withdraw()',
            'target address': VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'claimToken(address,address)',
            'target address': '0xD3cf852898b21fc233251427c2DC93d3d604F3BB',
            'avatar address arguments': [0]
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'claimTokens(address,address[])',
            'target address': '0xD3cf852898b21fc233251427c2DC93d3d604F3BB',
            'avatar address arguments': [0]
        })

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_balancer.json', 'w') as txn_balancer_file:
        json.dump(txn_balancer, txn_balancer_file)


# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# # get_gauges_v2
# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# def get_gauges_v2(blockchain):

#     web3 = get_node(blockchain)

#     try:
#         with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/balancer_gauges_v2', 'r') as gauges_v2_file:
#             # Reading from json file
#             gauges_v2 = json.load(gauges_v2_file)

#             try:
#                 gauges_v2[blockchain]
#             except:
#                 gauges_v2[blockchain] = {}
#     except:
#         gauges_v2 = {}
#         gauges_v2[blockchain] = {}

#     if blockchain == ETHEREUM:
#         gauge_factory_address = LIQUIDITY_GAUGE_FACTORY_ETHEREUM_V2

#     elif blockchain == POLYGON:
#         gauge_factory_address =  LIQUIDITY_GAUGE_FACTORY_POLYGON

#     elif blockchain == ARBITRUM:
#         gauge_factory_address =  LIQUIDITY_GAUGE_FACTORY_ARBITRUM

#     elif blockchain == XDAI:
#         gauge_factory_address =  LIQUIDITY_GAUGE_FACTORY_XDAI
    
#     get_logs_bool = True
#     block_from = 0
#     block_to = last_block(blockchain, web3=web3)
#     hash_overlap = []

#     gauge_created_event = web3.keccak(text=GAUGE_CREATED_EVENT_SIGNATURE).hex()

#     while get_logs_bool:
#         gauge_created_logs = get_logs_http(block_from, block_to, gauge_factory_address, gauge_created_event, blockchain)

#         log_count = len(gauge_created_logs)

#         if log_count != 0:
#             end_block = int(
#                 gauge_created_logs[log_count - 1]['blockNumber'][2:len(gauge_created_logs[log_count - 1]['blockNumber'])], 16)

#             for gauge_created_log in gauge_created_logs:
#                 block_number = int(gauge_created_log['blockNumber'][2:len(gauge_created_log['blockNumber'])], 16)

#                 if gauge_created_log['transactionHash'] in hash_overlap:
#                     continue

#                 if block_number == end_block:
#                     hash_overlap.append(gauge_created_log['transactionHash'])
                
#                 tx = web3.eth.get_transaction(gauge_created_log['transactionHash'])

#                 lptoken_address = web3.to_checksum_address('0x'+tx['input'][34:74])
#                 gauge_address = web3.to_checksum_address('0x' + gauge_created_log['topics'][1][-40:])
                
#                 gauges_v2[blockchain][lptoken_address] = gauge_address

#         if log_count < 1000:
#             get_logs_bool = False

#         else:
#             block_from = block_number

#     with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/balancer_gauges_v2', 'w') as gauges_v2_file:
#         json.dump(gauges_v2, gauges_v2_file)

#pool_data('0xA13a9247ea42D743238089903570127DdA72fE44')
# pool_data('0xfeBb0bbf162E64fb9D0dfe186E517d84C395f016')
# pool_data('0x32296969ef14eb0c6d29669c550d4a0449130230')
transactions_data(ETHEREUM)
# print(subgraph_query_pool_type('0xc443c15033fcb6cf72cc24f1bda0db070ddd9786000000000000000000000593'))
# is_deprecated('0x06df3b2bbb68adc8b0e302443692037ed9f91b42000000000000000000000063', '0x06Df3b2bbB68adc8B0e302443692037ED9f91b42', ['0x6B175474E89094C44Da98b954EedeAC495271d0F', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', '0xdAC17F958D2ee523a2206206994597C13D831ec7'], ETHEREUM, get_node(ETHEREUM))

# result = {}
# response = api_call()

# for pool in response['pools']:
#     result[pool['poolType']] = []

# print(result)

#get_gauges_v2(XDAI)
