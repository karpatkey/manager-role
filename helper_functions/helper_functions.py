from defi_protocols.functions import get_node, get_data, get_contract, get_contract_proxy_abi, search_proxy_impl_address
from defi_protocols.constants import ETHEREUM, WETH_ETH, ZERO_ADDRESS
import requests
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
        elif isinstance(func_params[func_param], tuple) or isinstance(func_params[func_param], list):
            func_params[func_param] = list(func_params[func_param])
            for i in range(len(func_params[func_param])):
                if isinstance(func_params[func_param][i], bytes):
                    func_params[func_param][i] = '0x' + func_params[func_param][i].hex()

    return [func_name, func_params]
