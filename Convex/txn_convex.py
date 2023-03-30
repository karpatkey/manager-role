from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols import Convex
from pathlib import Path
import os


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# search_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_pool(pools_data, lptoken_address):

    for pool_data in pools_data:
        if pool_data['LPtoken'] == lptoken_address:
            return pool_data

    return None


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# transactions_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def transactions_data():

    result = []

    web3 = get_node(ETHEREUM)

    booster = get_contract(Convex.BOOSTER, ETHEREUM, web3=web3)

    for i in range(booster.functions.poolLength().call()):
        
        pool_info = booster.functions.poolInfo(i).call()

        # pool_info[5] = shutdown
        if pool_info[5] == False:

            lptoken_symbol = get_symbol(pool_info[0], ETHEREUM, web3=web3)
            
            pool_data = {
                'name': 'Convex %s' % lptoken_symbol,
                'LPtoken': pool_info[0],
                'wrappedToken': pool_info[1],
                'rewarder':pool_info[3]
            }

            result.append(pool_data)

            print(i)

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/convex_data_final.json', 'w') as convex_data_file:
        json.dump(result, convex_data_file)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# pool_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pool_data(lptoken_address):

    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/convex_data_final.json', 'r') as convex_data_file:
            # Reading from json file
            convex_data = json.load(convex_data_file)
            convex_data_file.close()
    except:
        print('Convex Data File Not Found')
        return
    
    pool = search_pool(convex_data, lptoken_address)
    if pool == None:
        print('LP Token: %s not found in Convex Data File' % lptoken_address)
        return
    
    try:
        with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_convex_pools.json', 'r') as txn_convex_file:
            # Reading from json file
            txn_convex = json.load(txn_convex_file)
            txn_convex_file.close()
    except:
        txn_convex = {}
    
    txn_convex[lptoken_address] = {
        'approve': [],
        'functions': []
    }

    # APPROVALS
    txn_convex[lptoken_address]['approve'].append({
        'token': pool['LPtoken'],
        'spender': Convex.BOOSTER
    })

    txn_convex[lptoken_address]['approve'].append({
        'token': pool['wrappedToken'],
        'spender': pool['rewarder']
    })


    # FUNCTIONS


    txn_convex[lptoken_address]['functions'].append({
        'signature': 'depositAll(uint256,bool)',
        'target address': Convex.BOOSTER
    })



    txn_convex[lptoken_address]['functions'].append({
        'signature': 'stake(uint256)',
        'target address': pool['rewarder']
    })


    #Unstake & Withdraw button in the UI
    txn_convex[lptoken_address]['functions'].append({
        'signature': 'withdrawAndUnwrap(uint256,bool)',
        'target address': pool['rewarder']
    })

    txn_convex[lptoken_address]['functions'].append({
        'signature': 'getReward(address,bool)',
        'target address': pool['rewarder'],
        'avatar address arguments': [0]
    })

    #Second form with the Advanced settings in the UI

    txn_convex[lptoken_address]['functions'].append({
        'signature': 'deposit(uint256,uint256,bool)',
        'target address': Convex.BOOSTER
    })

    #Unstake button in UI
    txn_convex[lptoken_address]['functions'].append({
        'signature': 'withdraw(uint256,bool)',
        'target address': pool['rewarder']
    })
    #Withdraw button in UI
    txn_convex[lptoken_address]['functions'].append({
        'signature': 'withdraw(uint256,uint256)',
        'target address': Convex.BOOSTER
    })


    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/txn_convex_pools.json', 'w') as txn_convex_file:
        json.dump(txn_convex, txn_convex_file)


pool_data('0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2')

#transactions_data()