from defi_protocols.functions import get_symbol, balance_of, get_node, get_data, get_decimals, get_contract
from defi_protocols.constants import ETHEREUM, DAI_ETH, USDC_ETH, USDT_ETH
from defi_protocols.Balancer import VAULT
from helper_functions.helper_functions import bcolors, json_file_download, continue_execution, add_txn_with_role
from datetime import datetime
import math
import eth_abi

bb_a_USD = "0xfeBb0bbf162E64fb9D0dfe186E517d84C395f016"
bb_a_DAI = "0x6667c6fa9f2b3Fc1Cc8D85320b62703d938E4385"
bb_a_USDT = "0xA1697F9Af0875B63DdC472d6EeBADa8C1fAB8568"
bb_a_USDC = "0xcbFA4532D8B2ade2C261D3DD5ef2A2284f792692"

bb_a_USD_pid = "0xfebb0bbf162e64fb9d0dfe186e517d84c395f016000000000000000000000502"
bb_a_DAI_pid = "0x6667c6fa9f2b3fc1cc8d85320b62703d938e43850000000000000000000004fb"
bb_a_USDT_pid = "0xa1697f9af0875b63ddc472d6eebada8c1fab85680000000000000000000004f9"
bb_a_USDC_pid = "0xcbfa4532d8b2ade2c261d3dd5ef2a2284f7926920000000000000000000004fa"

BALANCER_QUERIES = '0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5'

# ABI Balancer Queries - queryExit, queryJoin
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# swap
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def swap():

    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}---------- Swap ----------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------{bcolors.ENDC}")
    print()

    print('Select the swap you want to execute: ')
    print('1- DAI -> bb-a-DAI')
    print('2- bb-a-DAI -> DAI')
    print('3- USDT -> bb-a-USDT')
    print('4- bb-a-USDT -> USDT')
    print('5- USDC -> bb-a-USDC')
    print('6- bb-a-USDC -> USDC')
    print()

    swap_option = input('Enter the option: ')
    while swap_option not in ['1','2','3','4','5','6']:
        swap_option = input('Enter a valid option (1, 2, 3 4, 5 or 6): ')
    
    if swap_option == '1' or swap_option == '2':
        pool_id = bb_a_DAI_pid

        if swap_option == '1':
            asset_in = DAI_ETH
            asset_out = bb_a_DAI
        else:
            asset_in = bb_a_DAI
            asset_out = DAI_ETH

    elif swap_option == '3' or swap_option == '4':
        pool_id = bb_a_USDT

        if swap_option == '3':
            asset_in = USDT_ETH
            asset_out = bb_a_USDT
        else:
            asset_in = bb_a_USDT
            asset_out = USDT_ETH
    
    elif swap_option == '5' or swap_option == '6':
        pool_id = bb_a_USDT

        if swap_option == '5':
            asset_in = USDC_ETH
            asset_out = bb_a_USDC
        else:
            asset_in = bb_a_USDC
            asset_out = USDC_ETH
    
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
        amount = input('Enter the amount of %s to swap: ' % asset_in_symbol)
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
        
        deadline = math.floor((datetime.now().timestamp() + 3600) * 1000)
        tx_data = get_data(VAULT, 'swap', [[pool_id, 0, asset_in, asset_out, int(amount), '0x'],[avatar_address, False, avatar_address, False],0,deadline], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, VAULT, tx_data, 0, json_file, web3=web3)
    else:
        print()
        message = 'Avatar Safe has no remaining balance of %s' % (asset_in_symbol)
        print(f"{bcolors.FAIL}{bcolors.BOLD}{message}{bcolors.ENDC}")


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# join_pool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def join_pool():

    print()
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}---------- Join Pool ----------{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
    print()

    amounts = []
    for asset_in in [bb_a_DAI, bb_a_USDT, bb_a_USDC]:
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

        join_pool = balancer_queries.functions.queryJoin(bb_a_USD_pid, avatar_address, avatar_address, [[bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD], amounts, user_data, False]).call()

        minimum_bpt = join_pool[0]
        amounts = [int(amount * (1 + (slippage/100))) for amount in amounts]

        amounts.append(0) # bb-a-USD amount
        tx_data = get_data(VAULT, 'joinPool', [bb_a_USD_pid, avatar_address, avatar_address,[[bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD], amounts, user_data, False]], ETHEREUM, web3=web3)
        if tx_data is not None:
            add_txn_with_role(roles_mod_address, VAULT, tx_data, 0, json_file, web3=web3)
    
    else:
        message = str('The Avatar Safe has none of the tokens needed to Join the Boosted Aave V3 pool')
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

    bpt_symbol = get_symbol(bb_a_USD, ETHEREUM, web3=web3)
    bpt_balance = balance_of(avatar_address, bb_a_USD, 'latest', ETHEREUM, web3=web3, decimals=False)
    bpt_decimals = get_decimals(bb_a_USD, ETHEREUM, web3=web3)

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
    print('2- EXACT_BPT_IN_FOR_ALL_TOKENS_OUT')
    print()

    exit_kind_option = input('Enter the option: ')
    while exit_kind_option not in ['1','2']:
        message = input('Enter a valid option (1, 2): ')
        exit_kind_option = input(message)
    
    if exit_kind_option == '1':
        print()
        print('Select the token to be withdrawn: ')
        print('1- bb-a-DAI')
        print('2- bb-a-USDT')
        print('3- bb-a-USDC')
        print()
        
        token_option = input('Enter the option: ')
        while token_option not in ['1','2', '3']:
            message = input('Enter a valid option (1, 2, 3): ')
            token_option = input(message)

        exit_kind = 0 # EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
        abi = ['uint256', 'uint256', 'uint256']
        data = [exit_kind, bpt_amount, int(token_option)-1]
    else:
        exit_kind = 2 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
        abi = ['uint256', 'uint256']
        data = [exit_kind, bpt_amount]

    user_data = '0x' + eth_abi.encode(abi, data).hex()

    # IMPORTANT: the StablePool JoinKind and ExitKind enums in the Boosted AaveV3 Pool does not match the order in
    # Balancer's documentation. Is very important to check the pools' contracts in orden to be sure.
    # https://docs.balancer.fi/reference/joins-and-exits/pool-exits.html

    balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, web3=web3, abi=ABI_BALANCER_QUERIES)

    exit_pool = balancer_queries.functions.queryExit(bb_a_USD_pid, avatar_address, avatar_address, [[bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD], [0, 0, 0, 0], user_data, False]).call()

    print()
    slippage = input('Enter the Slippage Tolerance (%): ')
    while True:
        try:
            slippage = int(slippage)
            if slippage > 0 and slippage <= 100:
                break
            else:
                raise Exception
        except:
            slippage = input('Enter a valid amount: ')
    
    amounts = [int(amount * (1 - (slippage/100))) for amount in exit_pool[1]]

    tx_data = get_data(VAULT, 'exitPool', [bb_a_USD_pid, avatar_address, avatar_address,[[bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD], amounts, user_data, False]], ETHEREUM, web3=web3)
    if tx_data is not None:
        add_txn_with_role(roles_mod_address, VAULT, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Balancer Boosted Aave V3 USD Manager ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--------------------------------------------{bcolors.ENDC}")
print()

avatar_address = '0x4F2083f5fBede34C2714aFfb3105539775f7FE64'
# avatar_address = '0x7f272451089Bf04797E33506D8831781d86A95f4'
# avatar_address = '0x854B004700885A61107B458f11eCC169A019b764'
roles_mod_address = '0xf20325cf84b72e8BBF8D8984B8f0059B984B390B'

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

while True:

    print(f"{bcolors.OKBLUE}{bcolors.BOLD}Select the action you want to execute:{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}1- Swap{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}2- Join Pool{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}3- Exit Pool{bcolors.ENDC}")
    print()

    action_option = input('Enter the option: ')
    while action_option not in ['1','2','3']:
        message = input('Enter a valid option (1, 2, 3): ')
        action_option = input(message)
    
    if action_option == '1':
        swap()
    elif action_option == '2':
        join_pool()
    elif action_option == '3':
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