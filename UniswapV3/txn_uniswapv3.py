from general.blockchain_functions import *
from defi_protocols import UniswapV3
# thegraph queries
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path
import os
import time

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query(min_tvl_usd=0, min_volume_usd=0):

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
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data(min_tvl_usd=0, min_volume_usd=0):

    pools = subgraph_query(min_tvl_usd=min_tvl_usd, min_volume_usd=min_volume_usd)

    if len(pools) > 0:
        print(len(pools))
        pools = dict(sorted(pools.items(), key=lambda item: item[1][4], reverse=True))
    
        result = []
        i = 0
        for pool in pools:
            fee = pools[pool][2] / 10000
            result.append(
                {
                    'name': 'UniswapV3 %s/%s %s%%' % (get_symbol(pools[pool][0], ETHEREUM), get_symbol(pools[pool][1], ETHEREUM), str(fee)),
                    'address': pool,
                    'tokens': [pools[pool][0], pools[pool][1]],
                    'fee': fee
                }
            )

            print(i)
            i += 1
        
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final_.json', 'w') as uniswapv3_data_file:
            json.dump(result, uniswapv3_data_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool_by_address
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool_by_address(pools_data, pool_address):

    for pool_data in pools_data:
        if pool_data['address'] == pool_address:
            return pool_data

    return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool_by_tokens_fee
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool_by_tokens_fee(pools_data, token0, token1, fee):

    for pool_data in pools_data:
        if token0 in pool_data['tokens'] and token1 in pool_data['tokens'] and pool_data['fee'] == fee:
            try:
                return pool_data
            except:
                return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pool_data(pool_address):

    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final.json', 'r') as uniswapv3_data_file:
            # Reading from json file
            uniswapv3_data = json.load(uniswapv3_data_file)
            uniswapv3_data_file.close()
    except:
        print('UniswapV3 Data File Not Found')
        return
    
    pool = search_pool_by_address(uniswapv3_data, pool_address)
    if pool == None:
        print('Pool address: %s not found in UniswapV3 Data File' % pool_address)
        return
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_uniswapv3.json', 'r') as txn_uniswapv3_file:
            # Reading from json file
            txn_uniswapv3 = json.load(txn_uniswapv3_file)
            txn_uniswapv3_file.close()
    except:
        txn_uniswapv3 = {}
    
    txn_uniswapv3[pool_address] = {
        'approve': [],
        'functions': []
    }

    # APPROVALS
    txn_uniswapv3[pool_address]['approve'].append({
        'token': pool['tokens'][0],
        'spender': UniswapV3.POSITIONS_NFT
    })

    txn_uniswapv3[pool_address]['approve'].append({
        'token': pool['tokens'][1],
        'spender': UniswapV3.POSITIONS_NFT
    })


    # FUNCTIONS
    if WETH_ETH in pool['tokens']:
        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'mint((address,address,uint24,int24,int24,uint256,uint256,uint256,uint256,address,uint256))',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [9],
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'refundETH()',
            'target address': UniswapV3.POSITIONS_NFT,
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'increaseLiquidity((uint256,uint256,uint256,uint256,uint256,uint256))',
            'target address': UniswapV3.POSITIONS_NFT,
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'collect((uint256,address,uint128,uint128))',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [1] # WARNING: CHECK ZERO_ADDRESS
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'unwrapWETH9(uint256,address)',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [1],
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'sweepToken(address,uint256,address)',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [2],
        })

    else:
        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'mint((address,address,uint24,int24,int24,uint256,uint256,uint256,uint256,address,uint256))',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [9],
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'increaseLiquidity((uint256,uint256,uint256,uint256,uint256,uint256))',
            'target address': UniswapV3.POSITIONS_NFT,
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'collect((uint256,address,uint128,uint128))',
            'target address': UniswapV3.POSITIONS_NFT,
            "avatar address arguments": [1]
        })
    

    # Common Functions
    txn_uniswapv3[pool_address]['functions'].append({
        'signature': 'decreaseLiquidity((uint256,uint128,uint256,uint256,uint256))',
        'target address': UniswapV3.POSITIONS_NFT,
    })


    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_uniswapv3.json', 'w') as txn_uniswapv3_file:
        json.dump(txn_uniswapv3, txn_uniswapv3_file)


#transactions_data(min_tvl_usd=1000, min_volume_usd=1000)

#pool_data('0xcbcdf9626bc03e24f779434178a73a0b4bad62ed')
# pool_data('0x6c6bc977e13df9b0de53b251522280bb72383700')

# web3 = get_node(ETHEREUM)

# result = []

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final.json', 'r') as uniswapv3_data_file:
#     # Reading from json file
#     uniswapv3_data = json.load(uniswapv3_data_file)
#     uniswapv3_data_file.close()

# for pool in uniswapv3_data:
#     pool['tokens'][0] = web3.toChecksumAddress(pool['tokens'][0])
#     pool['tokens'][1] = web3.toChecksumAddress(pool['tokens'][1])

#     result.append(pool)

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final.json', 'w') as uniswapv3_data_file:
#     json.dump(result, uniswapv3_data_file)


subgraph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
uniswapv3_transport=RequestsHTTPTransport(
    url=subgraph_url,
    verify=True,
    retries=3
)
client = Client(transport=uniswapv3_transport)

token0 = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'.lower()
token1 = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'.lower()
fee = 3000

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


for pool in response['pools']:
    print(pool)