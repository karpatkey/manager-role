from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols import Curve
from web3.exceptions import ContractLogicError
from pathlib import Path
import os

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TRICRYPTO POOLS (PARTICULAR CASES)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TRICRYPTO_V1_POOL_ADDRESS = '0x80466c64868E1ab14a1Ddf27A676C3fcBE638Fe5'
TRICRYPTO_V2_POOL_ADDRESS = '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Regular Pools ZAP ABI - base_pool
ABI_REGULAR_POOLS_ZAP = '[{"name":"base_pool","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1301}]'

# IMPORTANT: Gauges and ZAPs for Regular Pools can be found in https://curve.fi/contracts


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool(pools_data, lptoken_address):

    for pool_data in pools_data:
        if pool_data['token'] == lptoken_address:
            return pool_data

    return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_gauge_functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_gauge_functions(pool_txns, gauge_address, gauge_type):

    pool_txns['functions'].append({
            'signature': 'deposit(uint256)',
            'target address': gauge_address
        })
    
    if gauge_type != 'LiquidityGauge' and gauge_type != 'LiquidityGaugeReward' and gauge_type != 'LiquidityGaugeV2':
        pool_txns['functions'].append({
            'signature': 'deposit(uint256,address,bool)',
            'target address': gauge_address,
            'avatar address arguments': [1]
        })

    pool_txns['functions'].append({
        'signature': 'withdraw(uint256)',
        'target address': gauge_address
    })

    if gauge_type != 'LiquidityGauge' and gauge_type != 'LiquidityGaugeV2':
        pool_txns['functions'].append({
            'signature': 'withdraw(uint256,bool)',
            'target address': gauge_address
        })

    if gauge_type != 'LiquidityGauge':
        pool_txns['functions'].append({
            'signature': 'claim_rewards(address)',
            'target address': gauge_address,
            'avatar address arguments': [0]
        })


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data(blockchain, all_pools=False):

    result = []
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'r') as curve_data_file:
            # Reading from json file
            curve_data = json.load(curve_data_file)
            curve_data_file.close()
    except:
        curve_data = None
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_zaps.json', 'r') as curve_zaps_file:
            # Reading from json file
            curve_zaps = json.load(curve_zaps_file)
            curve_zaps_file.close()
    except:
        curve_zaps = None

    web3 = get_node(blockchain)

    ids = [0, 3, 5, 6]

    regular_registry_contract = Curve.get_registry_contract(web3, 0, 'latest', blockchain)
    factory_registry_contract = Curve.get_registry_contract(web3, 3, 'latest', blockchain)

    base_pools = []
    for i in range(factory_registry_contract.functions.base_pool_count().call()):
        base_pools.append(factory_registry_contract.functions.base_pool_list(i).call())

    for id in ids:
        registry_contract = Curve.get_registry_contract(web3, id, 'latest', blockchain)

        for i in range(registry_contract.functions.pool_count().call()):
            pool_address = registry_contract.functions.pool_list(i).call()
            pool_contract = get_contract(pool_address, blockchain, web3=web3, block='latest', abi=Curve.ABI_POOL)

            pool_name = 'Curve'
            pool_tokens = []
            next_token = True
            j = 0
            while(next_token == True):

                try:
                    token_address = pool_contract.functions.coins(j).call(block_identifier='latest')

                except ContractLogicError:
                    
                    # If the query fails when i == 0 -> the pool contract must be retrieved with the ABI_POOL_ALETRNATIVE
                    if j == 0:
                        pool_contract = get_contract(pool_address, blockchain, web3=web3, block='latest', abi=Curve.ABI_POOL_ALTERNATIVE)       
                    else:
                        next_token = False
                    
                    continue
                
                except ValueError:
                    next_token = False
                    continue
                
                pool_tokens.append(token_address)
                token_symbol = get_symbol(token_address, blockchain)

                if j == 0:
                    pool_name += ' %s' % token_symbol
                else:
                    pool_name += '/%s' % token_symbol
                
                j += 1

            if id == 0 or id == 5:
                lptoken_address = registry_contract.functions.get_lp_token(pool_address).call()
                gauge_address = registry_contract.functions.get_gauges(pool_address).call()[0]
                gauge_address = list(filter((ZERO_ADDRESS).__ne__, gauge_address))
                
                if gauge_address == []:
                    gauge_address = ZERO_ADDRESS
                else:
                    gauge_address = gauge_address.pop()
            else:
                try:
                    lptoken_address = pool_contract.functions.token().call()
                except:
                    lptoken_address = pool_address
                
                gauge_address = registry_contract.functions.get_gauge(pool_address).call()
            
            lptoken_total_supply = total_supply(lptoken_address, 'latest', blockchain, web3=web3)

            if lptoken_total_supply > 0 or all_pools == True:
            
                if id == 0:
                    try:
                        if gauge_address == ZERO_ADDRESS:
                            #gauge_address = curve_data['regular'][lptoken_address]['liquidity gauge']['address']
                            pool = search_pool(curve_data, lptoken_address)
                            gauge_address = pool['gauge']['address']
                    except:
                        gauge_address = ZERO_ADDRESS

                    pool_data = {
                        'name': pool_name,
                        'type': 'regular',
                        'meta': registry_contract.functions.is_meta(pool_address).call(),
                        'address': pool_address,
                        'token': lptoken_address,
                        'tokens': pool_tokens
                    }

                    if gauge_address != ZERO_ADDRESS:
                        pool_data['gauge'] = {
                            'address': gauge_address,
                            'type': Curve.get_gauge_version(gauge_address, 'latest', blockchain, web3=web3)
                        }
                    
                    try:
                        # Base pools don't have a ZAP
                        if pool_address not in base_pools:
                            pool_data['zap'] = {
                                'address': curve_zaps['regular'][lptoken_address]
                            }
                                
                            zap_contract = get_contract(pool_data['zap']['address'], ETHEREUM, web3=web3, abi=ABI_REGULAR_POOLS_ZAP)
                            
                            try:
                                # Has ZAP and the ZAP has the base_pool function
                                base_pool = zap_contract.functions.base_pool().call()
                                
                                base_pool_tokens = registry_contract.functions.get_coins(base_pool).call()
                                base_pool_tokens = list(filter((ZERO_ADDRESS).__ne__, base_pool_tokens))
                                
                                pool_data['zap']['basePool'] = {
                                    'address': base_pool,
                                    'tokens': base_pool_tokens
                                }
                            except:
                                # Has ZAP and and the ZAP does not have the base_pool function and is a meta pool
                                if pool_data['meta'] == True:
                                    base_pool_lptoken = pool_data['tokens'][1]
                                    pool_data['zap'] = {
                                        'address': curve_zaps['factory'][base_pool_lptoken]
                                    }

                                    base_pool = registry_contract.functions.get_pool_from_lp_token(base_pool_lptoken).call()
                                    
                                    base_pool_tokens = registry_contract.functions.get_coins(base_pool).call()
                                    base_pool_tokens = list(filter((ZERO_ADDRESS).__ne__, base_pool_tokens))
                                
                                    pool_data['zap']['basePool'] = {
                                        'address': base_pool,
                                        'tokens': base_pool_tokens
                                    }
                                # Has ZAP and and the ZAP does not have the base_pool function and is not a meta pool
                                else:
                                    pool_underlying_tokens = registry_contract.functions.get_underlying_coins(pool_address).call()
                                    pool_underlying_tokens = list(filter((ZERO_ADDRESS).__ne__, pool_underlying_tokens))

                                    if len(pool_underlying_tokens) > 0:
                                        # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
                                        if pool_address != TRICRYPTO_V1_POOL_ADDRESS:
                                            pool_data['zap']['underlying'] = pool_underlying_tokens

                    except:
                        # Has no ZAP but can still have underlying tokens that do not match the pool tokens
                        pool_underlying_tokens = registry_contract.functions.get_underlying_coins(pool_address).call()
                        pool_underlying_tokens = list(filter((ZERO_ADDRESS).__ne__, pool_underlying_tokens))
                        # pool_underlying_tokens = list(filter((E_ADDRESS).__ne__, pool_underlying_tokens))

                        if len(pool_data['tokens']) <= len(pool_underlying_tokens) and pool_data['tokens'] != pool_underlying_tokens:
                            pool_data['underlying'] = pool_underlying_tokens
              
                    result.append(pool_data)
                
                elif id == 3:
                    try:
                        if gauge_address == ZERO_ADDRESS:
                            # gauge_address = curve_data['factory'][lptoken_address]['liquidity gauge']['address']
                            pool = search_pool(curve_data, lptoken_address)
                            gauge_address = pool['gauge']['address']
                    except:
                        gauge_address = ZERO_ADDRESS
                    
                    pool_data = {
                        'name': pool_name,
                        'type': 'factory',
                        'meta': registry_contract.functions.is_meta(pool_address).call(),
                        'address': pool_address,
                        'token': lptoken_address,
                        'tokens': pool_tokens
                    }

                    if gauge_address != ZERO_ADDRESS:
                        pool_data['gauge'] = {
                            'address': gauge_address,
                            'type': Curve.get_gauge_version(gauge_address, 'latest', blockchain, web3=web3)
                        }

                    base_pool = registry_contract.functions.get_base_pool(pool_address).call()

                    if base_pool != ZERO_ADDRESS:
                        base_pool_lptoken = regular_registry_contract.functions.get_lp_token(base_pool).call()

                        try:
                            pool_data['zap'] = {
                                'address': curve_zaps['factory'][base_pool_lptoken]
                            }
                            
                            base_pool_tokens = regular_registry_contract.functions.get_coins(base_pool).call()
                            base_pool_tokens = list(filter((ZERO_ADDRESS).__ne__, base_pool_tokens))

                            pool_data['zap']['basePool'] = {
                                'address': base_pool,
                                'tokens': base_pool_tokens
                            }

                        except:
                            pass

                    result.append(pool_data)
                
                elif id == 5:
                    try:
                        if gauge_address == ZERO_ADDRESS:
                            # gauge_address = curve_data['crypto v2'][lptoken_address]['liquidity gauge']['address']
                            pool = search_pool(curve_data, lptoken_address)
                            gauge_address = pool['gauge']['address']
                    except:
                        gauge_address = ZERO_ADDRESS
                    
                    pool_data = {
                        'name': pool_name,
                        'type': 'crypto v2',
                        'meta': False,
                        'address': pool_address,
                        'token': lptoken_address,
                        'tokens': pool_tokens
                    }

                    if len(pool_data['tokens']) == 2 and search_pool(curve_data, pool_data['tokens'][1]) != None:
                        pool_data['meta'] = True

                    if gauge_address != ZERO_ADDRESS:
                        pool_data['gauge'] = {
                            'address': gauge_address,
                            'type': Curve.get_gauge_version(gauge_address, 'latest', blockchain, web3 = web3)
                        }
                    
                    zap_address = registry_contract.functions.get_zap(pool_address).call()
                    if zap_address != ZERO_ADDRESS:
                        pool_data['zap'] = {
                            'address': zap_address
                        }

                        try:
                            zap_contract = get_contract(zap_address, ETHEREUM, web3=web3, abi=ABI_REGULAR_POOLS_ZAP)
                            
                            base_pool = zap_contract.functions.base_pool().call()
                            
                            base_pool_tokens = regular_registry_contract.functions.get_coins(base_pool).call()
                            base_pool_tokens = list(filter((ZERO_ADDRESS).__ne__, base_pool_tokens))

                            pool_data['zap']['basePool'] = {
                                'address': base_pool,
                                'tokens': base_pool_tokens
                            }
                        
                        except:
                            pass

                    result.append(pool_data)
                
                elif id == 6:
                    try:
                        if gauge_address == ZERO_ADDRESS:
                            # gauge_address = curve_data['crypto factory'][lptoken_address]['liquidity gauge']['address']
                            pool = search_pool(curve_data, lptoken_address)
                            gauge_address = pool['gauge']['address']
                    except:
                        gauge_address = ZERO_ADDRESS
                    
                    pool_data = {
                        'name': pool_name,
                        'type': 'crypto factory',
                        'meta': False,
                        'address': pool_address,
                        'token': lptoken_address,
                        'tokens': pool_tokens
                    }

                    if search_pool(curve_data, pool_data['tokens'][1]) != None:
                        pool_data['meta'] = True

                    if gauge_address != ZERO_ADDRESS:
                        pool_data['gauge'] = {
                            'address': gauge_address,
                            'type': Curve.get_gauge_version(gauge_address, 'latest', blockchain, web3=web3)
                        }
                    
                    if X3CRV_ETH in pool_tokens:
                        pool_data['zap'] = {
                            'address': curve_zaps['crypto factory'][X3CRV_ETH]
                        }
                    
                    elif CRV_FRAX_ETH in pool_tokens:
                        pool_data['zap'] = {
                            'address': curve_zaps['crypto factory'][CRV_FRAX_ETH]
                        }
                    
                    try: 
                        zap_contract = get_contract(pool_data['zap']['address'], ETHEREUM, web3=web3, abi=ABI_REGULAR_POOLS_ZAP)
                        
                        base_pool = zap_contract.functions.base_pool().call()
                        
                        base_pool_tokens = regular_registry_contract.functions.get_coins(base_pool).call()
                        base_pool_tokens = list(filter((ZERO_ADDRESS).__ne__, base_pool_tokens))

                        pool_data['zap']['basePool'] = {
                            'address': base_pool,
                            'tokens': base_pool_tokens
                        }
                    
                    except:
                        pass
                    
                    result.append(pool_data)

            print(id, i)

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'w') as curve_data_file:
        json.dump(result, curve_data_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# regular_pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def regular_pool_data(lptoken_address):

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'r') as curve_data_file:
        # Reading from json file
        curve_data = json.load(curve_data_file)
        curve_data_file.close()
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_regular.json', 'r') as txn_regular_file:
            # Reading from json file
            txn_regular = json.load(txn_regular_file)
            txn_regular_file.close()
    except:
        txn_regular = {}
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_zaps.json', 'r') as curve_zaps_file:
            # Reading from json file
            curve_zaps = json.load(curve_zaps_file)
            curve_zaps_file.close()
        
        factory_zaps = list(curve_zaps['factory'].values())
    except:
        curve_zaps = None

    pool = search_pool(curve_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Curve Data File' % lptoken_address)
        return

    txn_regular[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    web3 = get_node(ETHEREUM)

    registry_contract = Curve.get_registry_contract(web3, 0, 'latest', ETHEREUM)

    n_coins = registry_contract.functions.get_n_coins(pool['address']).call()[0]

    # ADD: check if the pool has underlying coins
    try:
        ul_coins = len(pool['underlying'])
    except:
        ul_coins = 0
    
    # ADD: check if the pool has ZAP
    try:
        zap_address = pool['zap']['address']
    except:
        zap_address = ZERO_ADDRESS

    for i in range(n_coins):

        if pool['tokens'][i] != E_ADDRESS:
            txn_regular[lptoken_address]['approve'].append({
                'token': pool['tokens'][i],
                'spender': pool['address']
            })
    
    if ul_coins > 0:
        # ADD: approval of underlying tokens for pools without ZAP
        try:
            for i in range(len(pool['underlying'])):
                txn_regular[lptoken_address]['approve'].append({
                    'token': pool['underlying'][i],
                    'spender': pool['address']
                })
        except:
            pass
    
    txn_regular[lptoken_address]['functions'].append({
        'signature': 'add_liquidity(uint256[%d],uint256)' % n_coins,
        'target address': pool['address']
    })
    
    if ul_coins > 0:
        # ADD: 'signature': 'add_liquidity(uint256[%d],uint256,bool)' for pools without ZAP
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'add_liquidity(uint256[%d],uint256,bool)' % n_coins,
            'target address': pool['address']
        })
    
    # ADD: pools which are not metapools and have a ZAP (with no base pool) do not have the function 'remove_liquidity_one_coin(uint256,int128,uint256)'
    try:
        pool['zap']['underlying']
        # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
        if pool['address'] == TRICRYPTO_V1_POOL_ADDRESS:
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256)',
                'target address': pool['address']
            })
    except:
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_one_coin(uint256,int128,uint256)',
            'target address': pool['address']
        })

        if ul_coins > 0:
            # ADD: 'signature': 'remove_liquidity_one_coin(uint256,int128,uint256,bool)' for pools without ZAP
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_one_coin(uint256,int128,uint256,bool)',
                'target address': pool['address']
            })

    txn_regular[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity(uint256,uint256[%d])' % n_coins,
        'target address': pool['address']
    })

    if ul_coins > 0:
        # ADD: 'signature': 'remove_liquidity(uint256,uint256[%d],bool)' for pools without ZAP
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity(uint256,uint256[%d],bool)' % n_coins,
            'target address': pool['address']
        })

    # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
    if pool['address'] != TRICRYPTO_V1_POOL_ADDRESS:
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_imbalance(uint256[%d],uint256)' % n_coins,
            'target address': pool['address']
        })

    if ul_coins > 0:
        # ADD: 'signature': 'remove_liquidity_imbalance(uint256[%d],uint256,bool)' for pools without ZAP
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_imbalance(uint256[%d],uint256,bool)' % n_coins,
            'target address': pool['address']
        })

    # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
    if pool['address'] == TRICRYPTO_V1_POOL_ADDRESS:
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'exchange(uint256,uint256,uint256,uint256)',
            'target address': pool['address']
        })
    else:
        txn_regular[lptoken_address]['functions'].append({
            'signature': 'exchange(int128,int128,uint256,uint256)',
            'target address': pool['address']
        })

    # ADD: if the pool (meta or not) has ZAP or ul_coins > 0
    if zap_address != ZERO_ADDRESS or ul_coins > 0:
        # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
        if pool['address'] == TRICRYPTO_V1_POOL_ADDRESS:
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'exchange(uint256,uint256,uint256,uint256,bool)',
                'target address': pool['address']
            })
        else:
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'exchange_underlying(int128,int128,uint256,uint256)',
                'target address': pool['address']
            })

        try:
            base_n_coins = len(pool['zap']['basePool']['tokens'])
            n_all_coins = n_coins + base_n_coins - 1
        except:
            n_all_coins = n_coins
    else:
        n_all_coins = n_coins
        
    try:
        gauge_address = pool['gauge']['address']
    except:
        gauge_address = ZERO_ADDRESS
    
    if gauge_address != ZERO_ADDRESS:
        txn_regular[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': gauge_address
        })

        add_gauge_functions(txn_regular[lptoken_address], pool['gauge']['address'], pool['gauge']['type'])

    txn_regular[lptoken_address]['functions'].append({
        'signature': 'mint(address)',
        'target address': '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0',
        'avatar address arguments': [0]
    })
    
    if zap_address != ZERO_ADDRESS:
        # ADD: approvals ZAP
        # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
        if pool['address'] == TRICRYPTO_V1_POOL_ADDRESS:
            for i in range(n_coins):
                txn_regular[lptoken_address]['approve'].append({
                    'token': pool['tokens'][i],
                    'spender': zap_address
                })
        else:
            try:
                for i in range(len(pool['zap']['underlying'])):
                    txn_regular[lptoken_address]['approve'].append({
                    'token': pool['zap']['underlying'][i],
                    'spender': zap_address
                })
            except:
                for i in range(len(pool['zap']['basePool']['tokens'])):
                    txn_regular[lptoken_address]['approve'].append({
                    'token': pool['zap']['basePool']['tokens'][i],
                    'spender': zap_address
                })
        
        if zap_address in factory_zaps:
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'add_liquidity(address,uint256[%d],uint256)' % n_all_coins,
                'target address': zap_address
            })

            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_one_coin(address,uint256,int128,uint256)',
                'target address': zap_address
            })

            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity(address,uint256,uint256[%d])' % n_all_coins,
                'target address': zap_address
            })

            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_imbalance(address,uint256[%d],uint256)' % n_all_coins,
                'target address': zap_address
            })
        
        else:
            txn_regular[lptoken_address]['functions'].append({
                'signature': 'add_liquidity(uint256[%d],uint256)' % n_all_coins,
                'target address': zap_address
            })

            # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
            if pool['address'] == TRICRYPTO_V1_POOL_ADDRESS:
                txn_regular[lptoken_address]['functions'].append({
                    'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256)',
                    'target address': zap_address
                })
            else:
                txn_regular[lptoken_address]['functions'].append({
                    'signature': 'remove_liquidity_one_coin(uint256,int128,uint256)',
                    'target address': zap_address
                })

            txn_regular[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity(uint256,uint256[%d])' % n_all_coins,
                'target address': zap_address
            })

            # Particular Case: Tricrypto v1 (is in the Regular Pools Registry but has the behaviour of a Crypto V2)
            if pool['address'] != TRICRYPTO_V1_POOL_ADDRESS:
                txn_regular[lptoken_address]['functions'].append({
                    'signature': 'remove_liquidity_imbalance(uint256[%d],uint256)' % n_all_coins,
                    'target address': zap_address
                })
    
    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_regular.json', 'w') as txn_regular_file:
        json.dump(txn_regular, txn_regular_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# factory_pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def factory_pool_data(lptoken_address):

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'r') as curve_data_file:
        # Reading from json file
        curve_data = json.load(curve_data_file)
        curve_data_file.close()
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_factory.json', 'r') as txn_factory_file:
            # Reading from json file
            txn_factory = json.load(txn_factory_file)
            txn_factory_file.close()
    except:
        txn_factory = {}

    pool = search_pool(curve_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Curve Data File' % lptoken_address)
        return

    txn_factory[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    web3 = get_node(ETHEREUM)

    registry_contract = Curve.get_registry_contract(web3, 3, 'latest', ETHEREUM)

    coins_data = registry_contract.functions.get_meta_n_coins(pool['address']).call()

    n_coins = coins_data[0]
    underlying_coins = coins_data[1]

    for i in range(n_coins):

        if pool['tokens'][i] != E_ADDRESS:
            txn_factory[lptoken_address]['approve'].append({
                'token': pool['tokens'][i],
                'spender': pool['address']
            })
    
    txn_factory[lptoken_address]['functions'].append({
        'signature': 'add_liquidity(uint256[%d],uint256)' % n_coins,
        'target address': pool['address']
    })

    txn_factory[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity_one_coin(uint256,int128,uint256)',
        'target address': pool['address']
    })

    txn_factory[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity(uint256,uint256[%d])' % n_coins,
        'target address': pool['address']
    })

    txn_factory[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity_imbalance(uint256[%d],uint256)' % n_coins,
        'target address': pool['address']
    })

    txn_factory[lptoken_address]['functions'].append({
        'signature': 'exchange(int128,int128,uint256,uint256)',
        'target address': pool['address']
    })

    if registry_contract.functions.is_meta(pool['address']).call():
        txn_factory[lptoken_address]['functions'].append({
            'signature': 'exchange_underlying(int128,int128,uint256,uint256)',
            'target address': pool['address']
        })

    try:
        gauge_address = pool['gauge']['address']
    except:
        gauge_address = ZERO_ADDRESS
    
    if gauge_address != ZERO_ADDRESS:
        txn_factory[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': gauge_address
        })

        add_gauge_functions(txn_factory[lptoken_address], pool['gauge']['address'], pool['gauge']['type'])

    txn_factory[lptoken_address]['functions'].append({
        'signature': 'mint(address)',
        'target address': '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0',
        'avatar address arguments': [0]
    })

    try:
        zap_address = pool['zap']['address']
    except:
        zap_address = ZERO_ADDRESS
    
    if zap_address != ZERO_ADDRESS:
        # ADD: approvals ZAP
        try:
            for i in range(len(pool['zap']['basePool']['tokens'])):
                txn_factory[lptoken_address]['approve'].append({
                'token': pool['zap']['basePool']['tokens'][i],
                'spender': zap_address
            })
        except:
            pass

        txn_factory[lptoken_address]['functions'].append({
            'signature': 'add_liquidity(address,uint256[%d],uint256)' % underlying_coins,
            'target address': zap_address
        })

        txn_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_one_coin(address,uint256,int128,uint256)',
            'target address': zap_address
        })

        txn_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity(address,uint256,uint256[%d])' % underlying_coins,
            'target address': zap_address
        })

        txn_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_imbalance(address,uint256[%d],uint256)' % underlying_coins,
            'target address': zap_address
        })

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_factory.json', 'w') as txn_factory_file:
        json.dump(txn_factory, txn_factory_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# crypto_v2_pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def crypto_v2_pool_data(lptoken_address):

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'r') as curve_data_file:
        # Reading from json file
        curve_data = json.load(curve_data_file)
        curve_data_file.close()
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_crypto_v2.json', 'r') as txn_crypto_v2_file:
            # Reading from json file
            txn_crypto_v2 = json.load(txn_crypto_v2_file)
            txn_crypto_v2_file.close()
    except:
        txn_crypto_v2 = {}

    pool = search_pool(curve_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Curve Data File' % lptoken_address)
        return

    txn_crypto_v2[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    web3 = get_node(ETHEREUM)

    regular_registry_contract = Curve.get_registry_contract(web3, 0, 'latest', ETHEREUM)
    registry_contract = Curve.get_registry_contract(web3, 5, 'latest', ETHEREUM)

    n_coins = registry_contract.functions.get_n_coins(pool['address']).call()

    for i in range(n_coins):

        if pool['tokens'][i] != E_ADDRESS:
            txn_crypto_v2[lptoken_address]['approve'].append({
                'token': pool['tokens'][i],
                'spender': pool['address']
            })
    
    txn_crypto_v2[lptoken_address]['functions'].append({
        'signature': 'add_liquidity(uint256[%d],uint256)' % n_coins,
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        # Particular Case: Tricrypto V2
        if pool['address'] != TRICRYPTO_V2_POOL_ADDRESS:
            txn_crypto_v2[lptoken_address]['functions'].append({
                'signature': 'add_liquidity(uint256[%d],uint256,bool)' % n_coins,
                'target address': pool['address']
            })

    txn_crypto_v2[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256)',
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        # Particular Case: Tricrypto V2
        if pool['address'] != TRICRYPTO_V2_POOL_ADDRESS:
            txn_crypto_v2[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256,bool)',
                'target address': pool['address']
            })

    txn_crypto_v2[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity(uint256,uint256[%d])' % n_coins,
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        # Particular Case: Tricrypto V2
        if pool['address'] != TRICRYPTO_V2_POOL_ADDRESS:
            txn_crypto_v2[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity(uint256,uint256[%d],bool)' % n_coins,
                'target address': pool['address']
            })

    # IMPORTANT: CHECK IN THE CURVE UI WHICH EXCHANGE FUNCTIONS ARE CALLED
    txn_crypto_v2[lptoken_address]['functions'].append({
        'signature': 'exchange(uint256,uint256,uint256,uint256)',
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        txn_crypto_v2[lptoken_address]['functions'].append({
            'signature': 'exchange(uint256,uint256,uint256,uint256,bool)',
            'target address': pool['address']
        })

        # Particular Case: Tricrypto V2
        if pool['address'] != TRICRYPTO_V2_POOL_ADDRESS:
            txn_crypto_v2[lptoken_address]['functions'].append({
                'signature': 'exchange_underlying(uint256,uint256,uint256,uint256)',
                'target address': pool['address']
            })
        
    try:
        gauge_address = pool['gauge']['address']
    except:
        gauge_address = ZERO_ADDRESS
    
    if gauge_address != ZERO_ADDRESS:
        txn_crypto_v2[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': gauge_address
        })

        add_gauge_functions(txn_crypto_v2[lptoken_address], pool['gauge']['address'], pool['gauge']['type'])

    txn_crypto_v2[lptoken_address]['functions'].append({
        'signature': 'mint(address)',
        'target address': '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0',
        'avatar address arguments': [0]
    })

    try:
        zap_address = pool['zap']['address']
    except:
        zap_address = ZERO_ADDRESS
    
    if zap_address != ZERO_ADDRESS:
        # ADD: approvals ZAP
        # Particular Case: Tricrypto V2
        if pool['address'] == TRICRYPTO_V2_POOL_ADDRESS:
            for i in range(n_coins):
                txn_crypto_v2[lptoken_address]['approve'].append({
                    'token': pool['tokens'][i],
                    'spender': zap_address
                })
        try:
            for i in range(len(pool['zap']['basePool']['tokens'])):
                txn_crypto_v2[lptoken_address]['approve'].append({
                'token': pool['zap']['basePool']['tokens'][i],
                'spender': zap_address
            })
        except:
            pass

        try:
            zap_contract = get_contract(zap_address, ETHEREUM, web3=web3, abi=ABI_REGULAR_POOLS_ZAP)
            base_n_coins = regular_registry_contract.functions.get_n_coins(zap_contract.functions.base_pool().call()).call()[0]
            n_all_coins = n_coins + base_n_coins - 1

            # If the ZAP contract has the base_pool function
            txn_crypto_v2[lptoken_address]['functions'].append({
                'signature': 'exchange_underlying(uint256,uint256,uint256,uint256)',
                'target address': zap_address
            })
        
        except:
            n_all_coins = n_coins
            
        txn_crypto_v2[lptoken_address]['functions'].append({
            'signature': 'add_liquidity(uint256[%d],uint256)' % n_all_coins,
            'target address': zap_address
        })

        txn_crypto_v2[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256)',
            'target address': zap_address
        })

        txn_crypto_v2[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity(uint256,uint256[%d])' % n_all_coins,
            'target address': zap_address
        })         

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_crypto_v2.json', 'w') as txn_crypto_v2_file:
        json.dump(txn_crypto_v2, txn_crypto_v2_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# crypto_factory_pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def crypto_factory_pool_data(lptoken_address):

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_final.json', 'r') as curve_data_file:
        # Reading from json file
        curve_data = json.load(curve_data_file)
        curve_data_file.close()
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_crypto_factory.json', 'r') as txn_crypto_factory_file:
            # Reading from json file
            txn_crypto_factory = json.load(txn_crypto_factory_file)
            txn_crypto_factory_file.close()
    except:
        txn_crypto_factory = {}

    pool = search_pool(curve_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Curve Data File' % lptoken_address)
        return

    txn_crypto_factory[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    web3 = get_node(ETHEREUM)

    regular_registry_contract = Curve.get_registry_contract(web3, 0, 'latest', ETHEREUM)

    n_coins = 2

    for i in range(n_coins):

        if pool['tokens'][i] != E_ADDRESS:
            txn_crypto_factory[lptoken_address]['approve'].append({
                'token': pool['tokens'][i],
                'spender': pool['address']
            })
    
    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'add_liquidity(uint256[%d],uint256)' % n_coins,
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'add_liquidity(uint256[%d],uint256,bool)' % n_coins,
            'target address': pool['address']
        })

    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256)',
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_one_coin(uint256,uint256,uint256,bool)',
            'target address': pool['address']
        })

    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'remove_liquidity(uint256,uint256[%d])' % n_coins,
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity(uint256,uint256[%d],bool)' % n_coins,
            'target address': pool['address']
        })

    # IMPORTANT: CHECK IN THE CURVE UI WHICH EXCHANGE FUNCTIONS ARE CALLED
    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'exchange(uint256,uint256,uint256,uint256)',
        'target address': pool['address']
    })

    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'exchange(uint256,uint256,uint256,uint256,bool)',
        'target address': pool['address']
    })

    if WETH_ETH in pool['tokens']:
        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'exchange_underlying(uint256,uint256,uint256,uint256)',
            'target address': pool['address']
        })
    
    # txn_crypto_factory[lptoken_address]['functions'].append({
    #     'signature': 'exchange_extended(uint256,uint256,uint256,uint256,bool,address,address,bytes32)',
    #     'target address': pool['address']
    # })
    
    try:
        gauge_address = pool['gauge']['address']
    except:
        gauge_address = ZERO_ADDRESS
    
    if gauge_address != ZERO_ADDRESS:
        txn_crypto_factory[lptoken_address]['approve'].append({
            'token': lptoken_address,
            'spender': gauge_address
        })

        add_gauge_functions(txn_crypto_factory[lptoken_address], pool['gauge']['address'], pool['gauge']['type'])

    txn_crypto_factory[lptoken_address]['functions'].append({
        'signature': 'mint(address)',
        'target address': '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0',
        'avatar address arguments': [0]
    })

    try:
        zap_address = pool['zap']['address']
    except:
        zap_address = ZERO_ADDRESS
    
    if zap_address != ZERO_ADDRESS:
        # ADD: approvals ZAP
        try:
            for i in range(len(pool['zap']['basePool']['tokens'])):
                txn_crypto_factory[lptoken_address]['approve'].append({
                'token': pool['zap']['basePool']['tokens'][i],
                'spender': zap_address
            })
        except:
            pass

        try:
            zap_contract = get_contract(zap_address, ETHEREUM, web3=web3, abi=ABI_REGULAR_POOLS_ZAP)
            base_n_coins = regular_registry_contract.functions.get_n_coins(zap_contract.functions.base_pool().call()).call()[0]
            n_all_coins = n_coins + base_n_coins - 1
        
        except:
            n_all_coins = n_coins

        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'add_liquidity(address,uint256[%d],uint256)' % n_all_coins,
            'target address': zap_address
        })

        if WETH_ETH in pool['tokens']:
            txn_crypto_factory[lptoken_address]['functions'].append({
                'signature': 'add_liquidity(address,uint256[%d],uint256,bool)' % n_all_coins,
                'target address': zap_address
            })

        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity_one_coin(address,uint256,uint256,uint256)',
            'target address': zap_address
        })

        if WETH_ETH in pool['tokens']:
            txn_crypto_factory[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity_one_coin(address,uint256,uint256,uint256,bool)',
                'target address': zap_address
            })

        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'remove_liquidity(address,uint256,uint256[%d])' % n_all_coins,
            'target address': zap_address
        })

        if WETH_ETH in pool['tokens']:
            txn_crypto_factory[lptoken_address]['functions'].append({
                'signature': 'remove_liquidity(address,uint256,uint256[%d],bool)' % n_all_coins,
                'target address': zap_address
            })

        # IMPORTANT: CHECK IN THE CURVE UI WHICH EXCHANGE FUNCTIONS ARE CALLED
        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'exchange(address,uint256,uint256,uint256,uint256)',
            'target address': zap_address
        })

        txn_crypto_factory[lptoken_address]['functions'].append({
            'signature': 'exchange(address,uint256,uint256,uint256,uint256,bool)',
            'target address': zap_address
        })

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_crypto_factory.json', 'w') as txn_crypto_factory_file:
        json.dump(txn_crypto_factory, txn_crypto_factory_file)



#regular_pool_data('0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF')
#factory_pool_data('0x67C7f0a63BA70a2dAc69477B716551FC921aed00')
#crypto_v2_pool_data('0x70fc957eb90E37Af82ACDbd12675699797745F68')
#crypto_factory_pool_data('0xf985005a3793DbA4cCe241B3C19ddcd3Fe069ff4')
#crypto_factory_pool_data('0xbE4f3AD6C9458b901C81b734CB22D9eaE9Ad8b50')

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data_filter.json', 'r') as curve_data_file:
#             # Reading from json file
#             curve_data = json.load(curve_data_file)
#             curve_data_file.close()

#print(len(curve_data['regular']), len(curve_data['factory']), len(curve_data['crypto v2']), len(curve_data['crypto factory']))

#transactions_data(ETHEREUM)

# with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/curve_data.json', 'r') as curve_data_file:
#     # Reading from json file
#     curve_data = json.load(curve_data_file)
#     curve_data_file.close()

# for type in curve_data:
#     i = 0

#     for lptoken in curve_data[type]:

#         gauge_address = None

#         if type == 'regular' or type == 'crypto v2':

#             if curve_data[type][lptoken]['liquidity gauge']['address'] != []:

#                 gauge_address = curve_data[type][lptoken]['liquidity gauge']['address'][0]
            
#         else:

#             if curve_data[type][lptoken]['liquidity gauge']['address'] != ZERO_ADDRESS:

#                 gauge_address = curve_data[type][lptoken]['liquidity gauge']['address']
        
#         print(type, lptoken, i)

#         if gauge_address != None:

#             print(gauge_address, Curve.get_gauge_version(gauge_address, 'latest', ETHEREUM))

#             #v5
#             # try:
#             #     gauge_contract.functions.version().call()
#             #     print(gauge_address)
#             # except:
#             #     pass

#             #v4
#             # try:
#             #     getattr(gauge_contract.functions, 'add_reward')
#             #     try:
#             #         getattr(gauge_contract.functions, 'permit')
#             #     except:
#             #         print(gauge_address)
#             # except:
#             #     pass

#             #
#             #RewardsOnlyGauge
#             # try:
#             #     getattr(gauge_contract.functions, 'claimable_reward_write')
#             #     try:
#             #         getattr(gauge_contract.functions, 'set_killed')
#             #     except:
#             #         print(gauge_address)
#             # except:
#             #     pass
            

        
#         i += 1



