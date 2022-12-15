from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols import Aura
from defi_protocols import Balancer
from pathlib import Path
import os


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool(pools_data, lptoken_address):

    for pool_data in pools_data:
        if pool_data['token'] == lptoken_address:
            return pool_data
    
    return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# claim_rewards_contracts
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def claim_rewards_contracts():

    result = {
        'rewardContracts': [],
        'extraRewardContracts': [],
        'tokenRewardContracts': [Aura.EXTRA_REWARDS_DISTRIBUTOR]
    }

    web3 = get_node(ETHEREUM)

    booster = get_contract(Aura.BOOSTER, ETHEREUM, web3=web3)

    for i in range(booster.functions.poolLength().call()):
        
        pool_info = booster.functions.poolInfo(i).call()

        if pool_info[5] == False:

            rewarder_contract = get_contract(pool_info[3], ETHEREUM, web3=web3, abi=Aura.ABI_REWARDER)

            result['rewardContracts'].append(pool_info[3])

            for j in range(rewarder_contract.functions.extraRewardsLength().call()):
                result['extraRewardContracts'].append(rewarder_contract.functions.extraRewards(j).call())

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/claim_rewards_contracts.json', 'w') as claim_rewards_contracts_file:
        json.dump(result, claim_rewards_contracts_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data():

    result = []

    web3 = get_node(ETHEREUM)

    booster = get_contract(Aura.BOOSTER, ETHEREUM, web3=web3)

    for i in range(booster.functions.poolLength().call()):
        
        pool_info = booster.functions.poolInfo(i).call()

        # pool_info[5] = shutdown
        if pool_info[5] == False:

            lptoken_symbol = get_symbol(pool_info[0], ETHEREUM, web3=web3)

            lptoken_data = Balancer.get_lptoken_data(pool_info[0], 'latest', ETHEREUM, web3=web3)

            if lptoken_data['isBoosted'] == False:
                vault_contract = get_contract(Balancer.VAULT, ETHEREUM, web3=web3, abi=Balancer.ABI_VAULT)
                pool_tokens = vault_contract.functions.getPoolTokens(lptoken_data['poolId']).call()[0]
                
                pool_data = {
                    'name': 'Aura %s' % lptoken_symbol,
                    'token': pool_info[0],
                    'tokens': pool_tokens,
                    'rewarder':pool_info[3]
                }
            
            else:
                pool_data = {
                    'name': 'Aura %s' % lptoken_symbol,
                    'token': pool_info[0],
                    'rewarder':pool_info[3]
                }

            result.append(pool_data)

            print(i)

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/aura_data_final.json', 'w') as aura_data_file:
        json.dump(result, aura_data_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pool_data(lptoken_address):

    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/aura_data_final.json', 'r') as aura_data_file:
            # Reading from json file
            aura_data = json.load(aura_data_file)
            aura_data_file.close()
    except:
        print('Aura Data File Not Found')
        return
    
    pool = search_pool(aura_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Aura Data File' % lptoken_address)
        return
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_aura_pools.json', 'r') as txn_aura_file:
            # Reading from json file
            txn_aura = json.load(txn_aura_file)
            txn_aura_file.close()
    except:
        txn_aura = {}
    
    txn_aura[lptoken_address] = {
        'approve': [],
        'functions': []
    }
    
    web3 = get_node(ETHEREUM)
    
    lptoken_data = Balancer.get_lptoken_data(lptoken_address, 'latest', ETHEREUM, web3=web3)

    # APPROVALS
    txn_aura[lptoken_address]['approve'].append({
        'token': lptoken_address,
        'spender': Aura.BOOSTER
    })
    
    if lptoken_data['isBoosted'] == False:
        vault_contract = get_contract(Balancer.VAULT, ETHEREUM, web3=web3, abi=Balancer.ABI_VAULT)
        pool_tokens = vault_contract.functions.getPoolTokens(lptoken_data['poolId']).call()[0]

        for pool_token in pool_tokens:
            txn_aura[lptoken_address]['approve'].append({
                'token': pool_token,
                'spender': Aura.REWARD_POOL_DEPOSIT_WRAPPER
            })

    # FUNCTIONS
    txn_aura[lptoken_address]['functions'].append({
        'signature': 'deposit(uint256,uint256,bool)',
        'target address': Aura.BOOSTER
    })

    if lptoken_data['isBoosted'] == False:
        txn_aura[lptoken_address]['functions'].append({
            'signature': 'depositSingle(address,address,uint256,bytes32,(address[],uint256[],bytes,bool))',
            'target address': Aura.REWARD_POOL_DEPOSIT_WRAPPER
        })

    txn_aura[lptoken_address]['functions'].append({
        'signature': 'withdrawAndUnwrap(uint256,bool)',
        'target address': pool['rewarder']
    })

    txn_aura[lptoken_address]['functions'].append({
        'signature': 'getReward()',
        'target address': pool['rewarder'],
    })

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_aura_pools.json', 'w') as txn_aura_file:
        json.dump(txn_aura, txn_aura_file)


#pool_data('0x32296969Ef14EB0c6d29669C550D4a0449130230')

#transactions_data()

#claim_rewards_contracts()