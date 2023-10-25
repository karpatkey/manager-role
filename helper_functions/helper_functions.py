from defi_protocols.functions import get_node, get_data, get_contract, get_contract_proxy_abi, search_proxy_impl_address
from defi_protocols.constants import ETHEREUM, WETH_ETH, ZERO_ADDRESS, POLYGON, XDAI, BINANCE, AVALANCHE, FANTOM, OPTIMISM, ARBITRUM, API_ETHERSCAN_GETSOURCECODE, API_POLYGONSCAN_GETSOURCECODE, API_GNOSISSCAN_GETSOURCECODE, API_BINANCE_GETSOURCECODE, API_AVALANCHE_GETSOURCECODE, API_FANTOM_GETSOURCECODE, API_OPTIMISM_GETSOURCECODE, API_ARBITRUM_GETSOURCECODE, API_KEY_ETHERSCAN, API_KEY_POLSCAN, API_KEY_GNOSISSCAN, API_KEY_BINANCE, API_KEY_AVALANCHE, API_KEY_FANTOM, API_KEY_OPTIMISM, API_KEY_ARBITRUM
import requests
from web3 import Web3
import json
from pathlib import Path
import os

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MAX_TOKEN_AMOUNT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

TOKEN_PROXY = '0xa2327a938Febf5FEC13baCFb16Ae10EcBc4cbDCF'
AVATAR_PROXY = '0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552'
ROLES_MOD_PROXY = '0x85388a8cd772b19a468F982Dc264C238856939C9'

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

ParameterType = {
    0: 'Static',
    1: 'Dynamic',
    2: 'Dynamic32'
}
Comparison = {
    0: 'EqualTo',
    1: 'GreaterThan',
    2: 'LessThan',
    3: 'OneOf'
}

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ABI_ALLOWANCE = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# input_avatar_roles_module
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def input_avatar_roles_module(web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    avatar_address = input('Enter the Avatar Safe address: ')
    while True:
        try:
            avatar_address = web3.to_checksum_address(avatar_address)
            avatar_contract = get_contract_proxy_abi(avatar_address, AVATAR_PROXY, ETHEREUM)
            avatar_contract.functions.VERSION().call()
            break
        except:
            avatar_address = input('Enter a valid address: ')

    print()

    roles_mod_address = input('Enter the Roles Module address: ')
    while True:
        try:
            roles_mod_address = web3.to_checksum_address(roles_mod_address)
            roles_mod_contract = get_contract_proxy_abi(roles_mod_address, ROLES_MOD_PROXY, ETHEREUM)
            roles_mod_contract.functions.avatar().call()
            break
        except:
            roles_mod_address = input('Enter a valid address: ')

    print()

    return avatar_address, roles_mod_address


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# input_avatar_roles_module_no_checks
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def input_avatar_roles_module_no_checks(web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    avatar_address = input('Enter the Avatar Safe address: ')
    while True:
        try:
            avatar_address = web3.to_checksum_address(avatar_address)
            break
        except:
            avatar_address = input('Enter a valid address: ')

    print()

    roles_mod_address = input('Enter the Roles Module address: ')
    while True:
        try:
            roles_mod_address = web3.to_checksum_address(roles_mod_address)
            break
        except:
            roles_mod_address = input('Enter a valid address: ')

    print()

    return avatar_address, roles_mod_address


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_txn_with_role
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_txn_with_role(roles_mod_address, to_address, tx_data, eth_value, json_file, web3=None):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [to_address, int(eth_value), tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address=ROLES_MOD_PROXY)
    if exec_data is not None:   
        json_file['transactions'].append(
            {
                'to': roles_mod_address,
                'data': exec_data,
                'value': str(int(0))
            }
        )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# approve_token
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def approve_token(avatar_address, roles_mod_address, token, spender_address, json_file, web3=None, eth=False):

    if web3 is None:
        web3 = get_node(ETHEREUM)

    # approve Token
    if (token == WETH_ETH and eth == False) or token != WETH_ETH:
        token0_contract = get_contract(token, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
        if token0_contract.functions.allowance(avatar_address, spender_address).call() == 0:
            tx_data = get_data(token, 'approve', [spender_address, MAX_TOKEN_AMOUNT], ETHEREUM, abi_address=TOKEN_PROXY, web3=web3)
            if tx_data is not None:
                add_txn_with_role(roles_mod_address, token, tx_data, 0, json_file, web3=web3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# json_file_download
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def json_file_download(json_file):

    print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}--- JSON File Download---{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
    print()

    file_name = input('Enter the name of the JSON file: ')
    file_path = str(Path(os.path.abspath(__file__)).resolve().parents[1])+'/%s.json' % file_name
    print()
    try:
        with open(file_path, 'w') as file:
            json.dump(json_file, file, indent=4)
        
        message = 'JSON file %s was succesfully downloaded to the path: %s' % ('%s.json' % file_name, file_path)
        print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")
    except Exception as e:
        message = 'ERROR: JSON file %s download fail' % ('%s.json' % file_name)
        print(f"{bcolors.FAIL}{message}{bcolors.ENDC}")


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# continue_execution
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def continue_execution(json_has_txns=False):

    if not json_has_txns:
        print(f"{bcolors.WARNING}{bcolors.BOLD}No transactions were recorded{bcolors.ENDC}")
        print()

    print('Do you wish to add more transactions?')
    print('1- Yes')
    print('2- No')
    print()

    option = input('Enter the option: ')
    while option not in ['1','2']:
        option = input('Enter a valid option (1, 2): ')
    
    if option == '2':
        return False
    else:
        return True


# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# # restart_end
# #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# def restart_end():

#     print(f"{bcolors.WARNING}{bcolors.BOLD}No transactions were recorded{bcolors.ENDC}")
#     print()
#     print('Do you wish to restart?')
#     print('1- Yes')
#     print('2- No')
#     print()

#     option = input('Enter the option: ')
#     while option not in ['1','2']:
#         option = input('Enter a valid option (1, 2): ')
    
#     if option == '2':
#         exit()
#     else:
#         print()

def get_contract_name_from_scan(contract_address, blockchain):
    contract_name = ''

    if blockchain == ETHEREUM:
        data = requests.get(API_ETHERSCAN_GETSOURCECODE % (contract_address, API_KEY_ETHERSCAN)).json()

    elif blockchain == POLYGON:
        data = requests.get(API_POLYGONSCAN_GETSOURCECODE % (contract_address, API_KEY_POLSCAN)).json()

    elif blockchain == XDAI:
        data = requests.get(API_GNOSISSCAN_GETSOURCECODE % (contract_address, API_KEY_GNOSISSCAN)).json()

    elif blockchain == BINANCE:
        data = requests.get(API_BINANCE_GETSOURCECODE % (contract_address, API_KEY_BINANCE)).json()

    elif blockchain == AVALANCHE:
        data = requests.get(API_AVALANCHE_GETSOURCECODE % (contract_address, API_KEY_AVALANCHE)).json()

    elif blockchain == FANTOM:
        data = requests.get(API_FANTOM_GETSOURCECODE % (contract_address, API_KEY_FANTOM)).json()

    elif blockchain == OPTIMISM:
        data = requests.get(API_OPTIMISM_GETSOURCECODE % (contract_address, API_KEY_OPTIMISM)).json()

    elif blockchain == ARBITRUM:
        data = requests.get(API_ARBITRUM_GETSOURCECODE % (contract_address, API_KEY_ARBITRUM)).json()

    if data["message"] == "OK":
        contract_name = data["result"][0]["ContractName"]

    return contract_name

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# decode_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def decode_data(contract_address, data, blockchain):
    web3 = get_node(blockchain)
    
    # If the contract does not have the function, it checks if there is a proxy implementation
    proxy_impl_address = search_proxy_impl_address(contract_address, blockchain, web3=web3)

    if proxy_impl_address != ZERO_ADDRESS and proxy_impl_address != '':
        contract = get_contract_proxy_abi(contract_address, proxy_impl_address, blockchain, web3=web3)
    else:
        contract = get_contract(contract_address, blockchain)

    func_obj, func_params = contract.decode_function_input(data)

    func_name = requests.get("https://api.openchain.xyz/signature-database/v1/lookup?function=%s&filter=true" % data[:10]).json()['result']['function'][data[:10]][0]['name']

    for func_param in func_params:
        if isinstance(func_params[func_param], bytes):
            func_params[func_param] = '0x' + func_params[func_param].hex()
            if func_param == 'functionSig':
                selector = func_params[func_param]
                selector_names = requests.get("https://api.openchain.xyz/signature-database/v1/lookup?function=%s&filter=true" % selector).json()['result']['function'][selector]
                
                # If the contract does not have the function, it checks if there is a proxy implementation
                proxy_impl_address = search_proxy_impl_address(func_params['targetAddress'], blockchain, web3=web3)

                if proxy_impl_address != ZERO_ADDRESS and proxy_impl_address != '':
                    target_contract = get_contract_proxy_abi(func_params['targetAddress'], proxy_impl_address, blockchain, web3=web3)
                else:
                    target_contract = get_contract(func_params['targetAddress'], blockchain)
                
                signature = ''
                for selector_name in selector_names:
                    try:
                        getattr(target_contract.functions, selector_name['name'][:selector_name['name'].index('(')])
                        signature = selector_name['name']
                        break
                    except:
                        continue
                    
                func_params[func_param] = {
                    'selector': selector,
                    'signature': signature,
                }

        elif isinstance(func_params[func_param], tuple) or isinstance(func_params[func_param], list):
            func_params[func_param] = list(func_params[func_param])
            for i in range(len(func_params[func_param])):
                if func_param == 'paramType':
                    func_params[func_param][i] = str(func_params[func_param][i]) + ': ' + ParameterType[func_params[func_param][i]]
                elif func_param == 'paramComp':
                    func_params[func_param][i] = str(func_params[func_param][i]) + ': ' + Comparison[func_params[func_param][i]]
                if isinstance(func_params[func_param][i], bytes):
                    func_params[func_param][i] = '0x' + func_params[func_param][i].hex()
        
        else:
            if func_param == 'paramType':
                func_params[func_param] = str(func_params[func_param]) + ': ' + ParameterType[func_params[func_param]]
    
    try:
        contract_name = contract.functions.symbol().call()
    except:
        contract_name = get_contract_name_from_scan(contract_address, blockchain)

    entry = {
        'target': contract_address,
        'contractName': contract_name,
        'functionName': func_name,
        'params': func_params,
    }

    return entry
