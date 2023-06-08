from txn_uniswapv3_helpers import subgraph_query_all_pools
from defi_protocols.functions import get_symbol
from defi_protocols.constants import ETHEREUM, WETH_ETH
from defi_protocols.UniswapV3 import POSITIONS_NFT
from pathlib import Path
import os
import json


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data(min_tvl_usd=0, min_volume_usd=0):

    pools = subgraph_query_all_pools(min_tvl_usd=min_tvl_usd, min_volume_usd=min_volume_usd)

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
        'spender': POSITIONS_NFT
    })

    txn_uniswapv3[pool_address]['approve'].append({
        'token': pool['tokens'][1],
        'spender': POSITIONS_NFT
    })


    # FUNCTIONS
    if WETH_ETH in pool['tokens']:
        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'mint((address,address,uint24,int24,int24,uint256,uint256,uint256,uint256,address,uint256))',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [9],
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'refundETH()',
            'target address': POSITIONS_NFT,
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'increaseLiquidity((uint256,uint256,uint256,uint256,uint256,uint256))',
            'target address': POSITIONS_NFT,
            'use ETH': True
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'collect((uint256,address,uint128,uint128))',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [1] # WARNING: CHECK ZERO_ADDRESS
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'unwrapWETH9(uint256,address)',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [1],
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'sweepToken(address,uint256,address)',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [2],
        })

    else:
        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'mint((address,address,uint24,int24,int24,uint256,uint256,uint256,uint256,address,uint256))',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [9],
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'increaseLiquidity((uint256,uint256,uint256,uint256,uint256,uint256))',
            'target address': POSITIONS_NFT,
        })

        txn_uniswapv3[pool_address]['functions'].append({
            'signature': 'collect((uint256,address,uint128,uint128))',
            'target address': POSITIONS_NFT,
            "avatar address arguments": [1]
        })
    

    # Common Functions
    txn_uniswapv3[pool_address]['functions'].append({
        'signature': 'decreaseLiquidity((uint256,uint128,uint256,uint256,uint256))',
        'target address': POSITIONS_NFT,
    })


    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_uniswapv3.json', 'w') as txn_uniswapv3_file:
        json.dump(txn_uniswapv3, txn_uniswapv3_file)


#transactions_data(min_tvl_usd=1000)

#pool_data('0xcbcdf9626bc03e24f779434178a73a0b4bad62ed')
# pool_data('0x6c6bc977e13df9b0de53b251522280bb72383700')

# web3 = get_node(ETHEREUM)

# result = []

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final.json', 'r') as uniswapv3_data_file:
#     # Reading from json file
#     uniswapv3_data = json.load(uniswapv3_data_file)
#     uniswapv3_data_file.close()

# for pool in uniswapv3_data:
#     pool['tokens'][0] = web3.to_checksum_address(pool['tokens'][0])
#     pool['tokens'][1] = web3.to_checksum_address(pool['tokens'][1])

#     result.append(pool)

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/uniswapv3_data_final.json', 'w') as uniswapv3_data_file:
#     json.dump(result, uniswapv3_data_file)

#print(subgraph_query_pool('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', WETH_ETH, 0.3))

#print(subgraph_query_pool('0x48C3399719B582dD63eB5AADf12A40B4C3f52FA2', '0xFe2e637202056d30016725477c5da089Ab0A043A', 3000))