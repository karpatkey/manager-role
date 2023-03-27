from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols import Balancer
# thegraph queries
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path
import os


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# subgraph_query
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def subgraph_query():

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
        pools(first: {first}, skip: {skip}) {{
            id
            address
            poolType
            strategyType
            swapFee
            amp
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
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data(blockchain):

    result = {}

    web3 = get_node(blockchain)

    pools = subgraph_query()

    vault_contract = get_contract(Balancer.VAULT, blockchain, web3=web3, abi=Balancer.ABI_VAULT, block='latest')

    gauge_factory_address = Balancer.get_gauge_factory_address(blockchain)
    gauge_factory_contract = get_contract(gauge_factory_address, blockchain, web3=web3, abi=Balancer.ABI_LIQUIDITY_GAUGE_FACTORY,  block='latest')

    j = 0
    for pool in pools:

        lptoken_address = vault_contract.functions.getPool(pool['id']).call()[0]
        
        gauge_address = gauge_factory_contract.functions.getPoolGauge(lptoken_address).call()

        lptoken_data = Balancer.get_lptoken_data(lptoken_address, 'latest', blockchain, web3=web3)

        pool_tokens_data = vault_contract.functions.getPoolTokens(lptoken_data['poolId']).call(block_identifier='latest')
        pool_tokens = pool_tokens_data[0]

        pool_id_hex = '0x' + lptoken_data['poolId'].hex()

        pool_name = 'Balancer'

        for i in range(len(pool_tokens)):

            if i == lptoken_data['bptIndex']:
                continue

            token_address = pool_tokens[i]
            token_symbol = get_symbol(token_address, blockchain)

            if i == 0:
                pool_name += ' %s' % token_symbol
            else:
                pool_name += '/%s' % token_symbol
        
        result[lptoken_address] = {
            'pool id': pool_id_hex,
            'pool name': pool_name, 
            'pool type': pool['poolType'],
            'gauge': gauge_address,
            'tokens': pool_tokens
        }

        print(j)
        j += 1
    
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
        balancer_data_file.close()
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_balancer.json', 'r') as txn_balancer_file:
            # Reading from json file
            txn_balancer = json.load(txn_balancer_file)
            txn_balancer_file.close()
    except:
        txn_balancer = {}
    
    web3 = get_node(ETHEREUM)
    
    lptoken_address = web3.toChecksumAddress(lptoken_address)
    pool = search_pool(balancer_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Balancer Data File' % lptoken_address)
        return
    

    txn_balancer[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    for token in balancer_data[lptoken_address]['tokens']:
        txn_balancer[lptoken_address]['approve'].append({
            'token': token,
            'spender': Balancer.VAULT
        })
    
    if balancer_data[lptoken_address]['gauge'] != ZERO_ADDRESS:
        txn_balancer[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': balancer_data[lptoken_address]['gauge']
        })
    
    txn_balancer[lptoken_address]['functions'].append({
        'signature': 'joinPool(bytes32,address,address,(address[],uint256[],bytes,bool))',
        'target address': Balancer.VAULT,
        'avatar address arguments': [1, 2],
        'bytes32': balancer_data[lptoken_address]['pool id']
    })

    txn_balancer[lptoken_address]['functions'].append({
        'signature': 'exitPool(bytes32,address,address,(address[],uint256[],bytes,bool))',
        'target address': Balancer.VAULT,
        'avatar address arguments': [1, 2],
        'bytes32': balancer_data[lptoken_address]['pool id']
    })

    # result_item['functions'].append({
    #     'signature': 'swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256)',
    #     'target address': Balancer.VAULT,
    #     'avatar address arguments': [[1,0], [1,2]]
    # })

    # result_item['functions'].append({
    #     'signature': 'batchSwap(uint8,(bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)',
    #     'target address': Balancer.VAULT,
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
            'target address': Balancer.VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'increase_amount(uint256)',
            'target address': Balancer.VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'increase_unlock_time(uint256)',
            'target address': Balancer.VEBAL,
        })

        txn_balancer[lptoken_address]['functions'].append({
            'signature': 'withdraw()',
            'target address': Balancer.VEBAL,
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


#pool_data('0xA13a9247ea42D743238089903570127DdA72fE44')
#pool_data('0xfF083f57A556bfB3BBe46Ea1B4Fa154b2b1FBe88')
#transactions_data(ETHEREUM)

# result = {}
# response = api_call()

# for pool in response['pools']:
#     result[pool['poolType']] = []

# print(result)
