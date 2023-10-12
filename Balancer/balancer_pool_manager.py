from defi_protocols.functions import get_symbol, balance_of, get_node, get_data, get_decimals, get_contract
from defi_protocols.constants import ETHEREUM
from defi_protocols.Balancer import VAULT
from txn_balancer import subgraph_query_pool_type
from helper_functions.helper_functions import bcolors, json_file_download, continue_execution, add_txn_with_role, input_avatar_roles_module, input_avatar_roles_module_no_checks
from datetime import datetime
import math
import eth_abi


BALANCER_QUERIES = '0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5'

# ABI Balancer Queries - queryExit, queryJoin, querySwap
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]'

# LP Token ABI - getPoolId, decimals, getActualSupply, getVirtualSupply, totalSupply, getBptIndex, balanceOf, getSwapFeePercentage, getRate, getScalingFactors, POOL_ID, inRecoveryMode, version, onExitPool, getMainToken, getWrappedToken, getWrappedTokenRate, getMainIndex, getWrappedIndex
ABI_LPTOKEN = '[{"inputs":[],"name":"getPoolId","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getActualSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getVirtualSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getBptIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getSwapFeePercentage","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getScalingFactors","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"POOL_ID","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"inRecoveryMode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"version","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256[]","name":"balances","type":"uint256[]"},{"internalType":"uint256","name":"lastChangeBlock","type":"uint256"},{"internalType":"uint256","name":"protocolSwapFeePercentage","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"name":"onExitPool","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[],"name":"getMainToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getWrappedToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getWrappedTokenRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getMainIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getWrappedIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# join_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def join_pool():

    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}---------- Join Pool ----------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print()

    assets = vault.functions.getPoolTokens(bpt_pid).call()[0]

    amounts = []
    for asset_in in assets:
        asset_in_symbol = get_symbol(asset_in, ETHEREUM, web3=web3)
        asset_in_balance = balance_of(avatar_address, asset_in, 'latest', ETHEREUM, web3=web3, decimals=False)
        selected_token_decimals = get_decimals(asset_in, ETHEREUM, web3=web3)

        if asset_in_balance > 0:
            print()
            message = str('The amount of %s in the Avatar Safe is: %.18f' % (asset_in_symbol, asset_in_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
            print()
            message = 'If you want to select the MAX amount of %s enter \"max\"' % asset_in_symbol
            print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
            amount = input('Enter the amount of %s to deposit: ' % asset_in_symbol)
            while True:
                try:
                    if amount == 'max':
                        amount = asset_in_balance
                    else:
                        amount = float(amount)
                        amount = amount * (10**selected_token_decimals)
                        if amount > asset_in_balance:
                            print()
                            message = str('Insufficient balance of %s in Avatar Safe: %.18f' % (asset_in_symbol, asset_in_balance / (10**selected_token_decimals))).rstrip('0').rstrip('.')
                            message += (' %s\n') % asset_in_symbol
                            print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                            raise Exception
                    break
                except:
                    amount = input('Enter a valid amount: ')
            
            amounts.append(int(amount))
        
        else:
            amounts.append(0)
    
    if amounts != []:
        print()
        slippage = input('Enter the Slippage Tolerance (%): ')
        while True:
            try:
                slippage = float(slippage)
                if slippage > 0 and slippage <= 100:
                    break
                else:
                    raise Exception
            except:
                slippage = input('Enter a valid amount: ')

        # https://docs.balancer.fi/reference/joins-and-exits/pool-joins.html#arguments-explained
        
        join_kind = 1 # EXACT_TOKENS_IN_FOR_BPT_OUT
        minimum_bpt = 0
        abi = ['uint256', 'uint256[]', 'uint256']
        data = [join_kind, amounts, minimum_bpt]
        user_data = '0x' + eth_abi.encode(abi, data).hex()

        balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, web3=web3, abi=ABI_BALANCER_QUERIES)

        join_pool = balancer_queries.functions.queryJoin(bpt_pid, avatar_address, avatar_address, [assets, amounts, user_data, False]).call()

        minimum_bpt = join_pool[0]
        amounts = [int(amount * (1 + (slippage/100))) for amount in amounts]

        tx_data = get_data(VAULT, 'joinPool', [bpt_pid, avatar_address, avatar_address,[assets, amounts, user_data, False]], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, VAULT, tx_data, 0, json_file, web3=web3)
    
    else:
        message = str('The Avatar Safe has none of the tokens needed to Join the Pool')
        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# exit_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def exit_pool():

    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}---------- Exit Pool ----------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print()

    bpt_symbol = get_symbol(bpt, ETHEREUM, web3=web3)
    bpt_balance = balance_of(avatar_address, bpt, 'latest', ETHEREUM, web3=web3, decimals=False)
    bpt_decimals = get_decimals(bpt, ETHEREUM, web3=web3)
    assets = vault.functions.getPoolTokens(bpt_pid).call()[0]

    if bpt_balance > 0:
        print()
        message = str('The amount of %s in the Avatar Safe is: %.18f' % (bpt_symbol, bpt_balance / (10**bpt_decimals))).rstrip('0').rstrip('.')
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")
        print()
        message = 'If you want to select the MAX amount of %s enter \"max\"' % bpt_symbol
        print(f"{bcolors.WARNING}{bcolors.BOLD}{message}{bcolors.ENDC}")
        bpt_amount = input('Enter the amount of %s to withdraw: ' % bpt_symbol)
        while True:
            try:
                if bpt_amount == 'max':
                    bpt_amount = bpt_balance
                    bpt_amount = int(bpt_amount)
                else:
                    bpt_amount = float(bpt_amount)
                    bpt_amount = bpt_amount * (10**bpt_decimals)
                    bpt_amount = int(bpt_amount)
                    if bpt_amount > bpt_balance:
                        print()
                        message = str('Insufficient balance of %s in Avatar Safe: %.18f' % (bpt_symbol, bpt_balance / (10**bpt_decimals))).rstrip('0').rstrip('.')
                        message += (' %s\n') % bpt_symbol
                        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")
                        raise Exception
                break
            except:
                bpt_amount = input('Enter a valid amount: ')

        print()
        print('Select the ExitKind to be executed: ')
        print('1- EXACT_BPT_IN_FOR_ONE_TOKEN_OUT')
        print('2- EXACT_BPT_IN_FOR_TOKENS_OUT')
        print()

        exit_kind_option = input('Enter the option: ')
        while exit_kind_option not in ['1','2']:
            message = input('Enter a valid option (1, 2): ')
            exit_kind_option = input(message)
        
        if exit_kind_option == '1':
            valid_token_options = []
            for i in range(len(assets)):
                print('%d- %s' % (i+1, get_symbol(assets[i], ETHEREUM, web3=web3)))
                valid_token_options.append(str(i+1))
            
            print()
            token_option = input('Enter the option: ')
            while token_option not in valid_token_options:
                message = 'Enter a valid option (' + ','.join(option for option in valid_token_options) + '): '
                token_option = input(message)

            exit_kind = 0 # EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
            abi = ['uint256', 'uint256', 'uint256']
            data = [exit_kind, bpt_amount, int(token_option)-1]
        else:
            in_recovery_mode = False
            try:
                in_recovery_mode = bpt_contract.function.inRecoveryMode().call()
            except:
                pass

            if in_recovery_mode:
                exit_kind = 255 # RECOVERY_MODE_EXIT_KIND
            else:
                pool_type = subgraph_query_pool_type('0x'+bpt_pid.hex())
                if pool_type == 'ComposableStable':
                    exit_kind = 2 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
                else:
                    exit_kind = 1 # EXACT_BPT_IN_FOR_TOKENS_OUT
                abi = ['uint256', 'uint256']
                data = [exit_kind, bpt_amount]

        user_data = '0x' + eth_abi.encode(abi, data).hex()

        # IMPORTANT: the StablePool JoinKind and ExitKind enums in the Boosted AaveV3 Pool does not match the order in
        # Balancer's documentation. Is very important to check the pools' contracts in orden to be sure.
        # https://docs.balancer.fi/reference/joins-and-exits/pool-exits.html

        balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, web3=web3, abi=ABI_BALANCER_QUERIES)

        exit_pool = balancer_queries.functions.queryExit(bpt_pid, avatar_address, avatar_address, [assets, [0] * len(assets), user_data, False]).call()

        print()
        slippage = input('Enter the Slippage Tolerance (%): ')
        while True:
            try:
                slippage = float(slippage)
                if slippage > 0 and slippage <= 100:
                    break
                else:
                    raise Exception
            except:
                slippage = input('Enter a valid amount: ')
        
        amounts = [int(amount * (1 - (slippage/100))) for amount in exit_pool[1]]

        tx_data = get_data(VAULT, 'exitPool', [bpt_pid, avatar_address, avatar_address,[assets, amounts, user_data, False]], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, VAULT, tx_data, 0, json_file, web3=web3)
    
    else:
        message = str('The Avatar Safe has no BPT amount to Exit the Pool')
        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Balancer Pool Manager ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------------{bcolors.ENDC}")
print()

avatar_address, roles_mod_address = input_avatar_roles_module_no_checks(web3=web3)
# avatar_address = '0xC01318baB7ee1f5ba734172bF7718b5DC6Ec90E1' # '0x4F2083f5fBede34C2714aFfb3105539775f7FE64'
# avatar_address = '0x7f272451089Bf04797E33506D8831781d86A95f4' # 0x53EB19C3A0443b5a12Ed2C7B32d4a27088842E6D
# avatar_address = '0xa7dB55e153C0c71Ff35432a9aBe2A853f886Ce0D' # 0xF63F5FCC54f5fd11f3c098053F330E032E4D9259
# roles_mod_address = '0x1ffAdc16726dd4F91fF275b4bF50651801B06a86' # '0xf20325cf84b72e8BBF8D8984B8f0059B984B390B'

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

vault = get_contract(VAULT, ETHEREUM, web3=web3)

while True:

    while True:
        bpt = input(f"{bcolors.OKBLUE}{bcolors.BOLD}Enter the BPT: {bcolors.ENDC}")
        if web3.is_address(bpt):
            bpt = web3.to_checksum_address(bpt)
            bpt_contract = get_contract(bpt, ETHEREUM, web3=web3, abi=ABI_LPTOKEN)
            try:
                bpt_pid = bpt_contract.functions.getPoolId().call()
                break
            except:
                print(f"{bcolors.FAIL}{bcolors.BOLD}The address entered is not a BPT{bcolors.ENDC}")

    print()
    print(f"{bcolors.OKBLUE}{bcolors.BOLD}Select the action you want to execute:{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}1- Join Pool{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}2- Exit Pool{bcolors.ENDC}")
    print()

    action_option = input('Enter the option: ')
    while action_option not in ['1','2']:
        message = input('Enter a valid option (1, 2): ')
        action_option = input(message)
    
    if action_option == '1':
        join_pool()
    elif action_option == '2':
        exit_pool()
    
    print()
    if json_file['transactions'] != []:
        exec = continue_execution(True)
    else:
        exec = continue_execution()

    print()
    if exec:
        continue
    else:
        if json_file['transactions'] != []:
            json_file_download(json_file)
            print()
            
        break