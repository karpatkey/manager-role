from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols.UniswapV3 import *
from txn_uniswapv3 import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SETH2 = '0xFe2e637202056d30016725477c5da089Ab0A043A'
COMP = '0xc00e94Cb662C3520282E6f5717214004A7f26888'
AAVE = '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'
RETH2 = '0x20BC832ca081b91433ff6c17f85701B6e92486c5'
SWISE = '0x48C3399719B582dD63eB5AADf12A40B4C3f52FA2'

TOKENS = [SETH2, COMP, AAVE, RETH2, SWISE]

PATHS = {
    COMP: {
        USDC_ETH: [COMP, WETH_ETH, USDC_ETH],
        DAI_ETH: [COMP, WETH_ETH, DAI_ETH]
    },
    AAVE: {
        USDC_ETH: [AAVE, WETH_ETH, USDC_ETH],
        DAI_ETH: [AAVE, WETH_ETH, DAI_ETH]
    },
    RETH2: {
        USDC_ETH: [RETH2, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [RETH2, SETH2, WETH_ETH, DAI_ETH]
    },
    SWISE: {
        USDC_ETH: [SWISE, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [SWISE, SETH2, WETH_ETH, DAI_ETH]
    },
    SETH2: {
        WETH_ETH: [SETH2, WETH_ETH]
    }
}

MAX_TOKEN_AMOUNT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

UNISWAPV3_ROUTER = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'

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
# approve_tokens
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def approve_tokens():

    # approve Reward Token
    reward_token_contract = get_contract(selected_token, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
    if reward_token_contract.functions.allowance(avatar_address, UNISWAPV3_ROUTER).call() == 0:
        tx_data = get_data(selected_token, 'approve', [UNISWAPV3_ROUTER, MAX_TOKEN_AMOUNT], ETHEREUM, web3=web3)
        if tx_data is not None:
            exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [selected_token, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
            if exec_data is not None:
                json_file['transactions'].append(
                    {
                        'to': roles_mod_address,
                        'data': exec_data,
                        'value': 0
                    }
                )

    # approve Swap Token
    swap_token_contract = get_contract(swap_token, ETHEREUM, web3=web3, abi=ABI_ALLOWANCE)
    if swap_token_contract.functions.allowance(avatar_address, UNISWAPV3_ROUTER).call() == 0:
        tx_data = get_data(swap_token_contract, 'approve', [UNISWAPV3_ROUTER, MAX_TOKEN_AMOUNT], ETHEREUM, web3=web3)
        if tx_data is not None:
            exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [swap_token_contract, 0, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
            if exec_data is not None:
                json_file['transactions'].append(
                    {
                        'to': roles_mod_address,
                        'data': exec_data,
                        'value': 0
                    }
                )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# add_txn_with_role
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def add_txn_with_role(tx_data, eth_value):

    exec_data = get_data(roles_mod_address, 'execTransactionWithRole', [UniswapV3.POSITIONS_NFT, eth_value, tx_data, 0, 1, False], ETHEREUM, web3=web3, abi_address='0x8c858908D5f4cEF92f2B2277CB38248D39513f45')
    if exec_data is not None:   
        json_file['transactions'].append(
            {
                'to': roles_mod_address,
                'data': exec_data,
                'value': str(0)
            }
        )


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# get_rate
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_rate():

    result_rates = []
    for i in range(len(path)-1):
        rates = []
        for fee in FEES:
            rate = get_rate_uniswap_v3(path[i], path[i+1], 'latest', ETHEREUM, web3=web3, fee=fee)
            if rate != None:
                rates.append(rate)
        
        min_rate = min(rates)
        result_rates.append(min_rate)

    result_rate = 1

    for rate in result_rates:
        result_rate = result_rate * rate
    
    return result_rate


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# swap_selected_token
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def swap_selected_token():
    
    rate = get_rate()

    expected_amount = rate * token_balance
    
    message = 'Expected amount of %s for the %f of %s is: %f' %(swap_token_symbol, token_balance, token_symbol, expected_amount)
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}")

    print()

    print('Do you wish to proceed: ')
    print('1- Yes')
    print('2- No')
    print()

    option = input('Enter the option: ')
    while option not in ['1','2']:
        option = input('Enter a valid option (1, 2): ')
    
    if option == '1': 
        approve_tokens()

        tx_data = get_data(UNISWAPV3_ROUTER, 'swapExactTokensForTokens', [token_balance, amount_out_min, path, avatar_address])
        if tx_data is not None:
            add_txn_with_role(tx_data, 0)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                       
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- UniswapV3 Token Swapper ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-------------------------------{bcolors.ENDC}")
print()

avatar_address = input('Enter the Avatar Safe address: ')
while not web3.isAddress(avatar_address):
    avatar_address = input('Enter a valid address: ')

web3.toChecksumAddress(avatar_address)
print()

roles_mod_address = input('Enter the Roles Module address: ')
while not web3.isAddress(roles_mod_address):
    roles_mod_address = input('Enter a valid address: ')

web3.toChecksumAddress(roles_mod_address)
print()

print('Select the token to swap: ')
print(f"{bcolors.WARNING}If you choose sETH2, it will automatically be swapped by WETH{bcolors.ENDC}")
print()
valid_token_options = []
for i in range(len(TOKENS)):
    print('%d- %s' % (i+1, get_symbol(TOKENS[i], ETHEREUM, web3=web3)))
    valid_token_options.append(str(i+1))

print()
token_option = input('Enter the token: ') 
while token_option not in valid_token_options:
    message = 'Enter a valid option (' + ','.join(option for option in valid_token_options) + '): '
    token_option = input(message)

print()
selected_token = TOKENS[int(token_option)-1]
token_symbol = get_symbol(selected_token, ETHEREUM, web3=web3)
token_balance = balance_of(avatar_address, selected_token, 'latest', ETHEREUM, web3=web3)
message = 'Selected Token: %s\nBalance: %f' % (token_symbol, token_balance)
print(f"{bcolors.OKBLUE}{bcolors.BOLD}{message}{bcolors.ENDC}")
print()

if selected_token != SETH2:
    print('Select the token to swap the %s balance for: ' % token_symbol)
    print('1- USDC')
    print('2- DAI')
    print()
    swap_option = input('Enter the option: ')
    while swap_option not in ['1','2']:
        swap_option = input('Enter a valid option (1, 2): ')
    
    if swap_option == '1':
        swap_token = USDC_ETH
        swap_token_symbol = 'USDC'
    elif swap_option == '2':
        swap_token = DAI_ETH
        swap_token_symbol = 'DAI'

else:
    swap_token = WETH_ETH
    swap_token_symbol = 'WETH'
    
path = PATHS[selected_token][swap_token]

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

print()

swap_selected_token()

print()
print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
print(f"{bcolors.OKBLUE}--- JSON File Download---{bcolors.ENDC}")
print(f"{bcolors.OKBLUE}-------------------------{bcolors.ENDC}")
print()

file_name = input('Enter the name of the JSON file: ')
file_path = str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/%s.json' % file_name
print()
try:
    with open(file_path, 'w') as uniswapv3_txn_builder:
        json.dump(json_file, uniswapv3_txn_builder)
    
    message = 'JSON file %s was succesfully downloaded to the path: %s' % ('%s.json' % file_name, file_path)
    print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")
except:
    message = 'ERROR: JSON file %s download fail' % ('%s.json' % file_name)
    print(f"{bcolors.FAIL}{message}{bcolors.ENDC}")