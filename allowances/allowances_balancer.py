from defi_protocols.functions import get_symbol
from helper_functions.helper_functions import *
from tqdm import tqdm
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Tokens
BAL = "0xba100000625a3754423978a60c9317c58a424e3D"
MTA = "0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2"
D2D = "0x43D4A3cd90ddD2F8f4f693170C9c8098163502ad"
COMP = "0xc00e94Cb662C3520282E6f5717214004A7f26888"
AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
rETH2 = "0x20BC832ca081b91433ff6c17f85701B6e92486c5"
SWISE = "0x48e5413b73add2434e47504E2a22d14940dBFe78"
sETH2 = "0xFe2e637202056d30016725477c5da089Ab0A043A"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

# Across V2 contracts
ACROSS_HUB_POOL_V2 = "0xc186fA914353c44b2E33eBE05f21846F1048bEda"

# Aave V3 contracts
AAVE_POOL_V3 = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

# Silo V2 contracts
SILO_ROUTER_V2 = "0x8658047e48CC09161f4152c79155Dac1d710Ff0a"

# mStable V2 contracts
stkMTA = "0x8f2326316eC696F6d023E37A9931c2b2C177a3D7"

# Balancer contracts
BALANCER_VAULT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

# Cowswap contracts
GPv2_VAULT_RELAYER = "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110"

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ALLOWANCES = [
    {
        "token": BAL,
        "spender": AAVE_POOL_V3
    },
    {
        "token": BAL,
        "spender": ACROSS_HUB_POOL_V2
    },
    {
        "token": BAL,
        "spender": SILO_ROUTER_V2
    },
    {
        "token": MTA,
        "spender": stkMTA
    },
    {
        "token": BAL,
        "spender": BALANCER_VAULT
    },
    {
        "token": D2D,
        "spender": BALANCER_VAULT
    },
    {
        "token": COMP,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": AAVE,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": rETH2,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": SWISE,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": sETH2,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": WETH,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": USDC,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": DAI,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": USDT,
        "spender": GPv2_VAULT_RELAYER
    },
    {
        "token": WBTC,
        "spender": GPv2_VAULT_RELAYER
    }
]



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Token Approvals ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
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

