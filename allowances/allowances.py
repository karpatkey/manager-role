from defi_protocols.functions import get_symbol
from helper_functions.helper_functions import *
from tqdm import tqdm
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ALLOWANCES = []

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Token Approvals ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print()

avatar_address = input('Enter the Avatar Safe address: ')
while True:
    try:
        avatar_address = web3.toChecksumAddress(avatar_address)
        avatar_contract = get_contract_proxy_abi(avatar_address, AVATAR_PROXY, ETHEREUM)
        avatar_contract.functions.VERSION().call()
        break
    except:
        avatar_address = input('Enter a valid address: ')

print()

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

allowance_range = tqdm(range(len(ALLOWANCES)), desc='')

i = 0
for i in allowance_range:
    allowance_range.set_description('Approving spender in token %s' % get_symbol(ALLOWANCES[i]['token'], ETHEREUM, web3=web3))
    json_file['transactions'].append(
        {
            'to': ALLOWANCES[i]['token'],
            'data': get_data(ALLOWANCES[i]['token'], 'approve', [ALLOWANCES[i]['spender'], MAX_TOKEN_AMOUNT], ETHEREUM, abi_address=TOKEN_PROXY, web3=web3),
            'value': str(0)
        }
    )

    i += 1

print()

if json_file['transactions'] != []:
    json_file_download(json_file)


