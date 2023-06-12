from defi_protocols.functions import get_symbol
from helper_functions.helper_functions import *
from tqdm import tqdm
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Tokens
CVX = "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
rETH = "0xae78736Cd615f374D3085123A210448E74Fc6393"
stETH = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
wstETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"

# Aave V3 contracts
AAVE_POOL_V3 = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

# Compound V2 contracts
COMPTROLLER = "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"
cUSDC = "0x39AA39c021dfbaE8faC545936693aC917d5E7563"
cDAI = "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643"
COMP = "0xc00e94Cb662C3520282E6f5717214004A7f26888"

# Compound V3 contracts
cUSDCv3 = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"

# Stakewise contracts
STAKEWISE_ETH2_STAKING = "0xC874b064f465bdD6411D45734b56fac750Cda29A"
STAKEWISE_MERKLE_DIS = "0xA3F21010e8b9a3930996C8849Df38f9Ca3647c20"
sETH2 = "0xFe2e637202056d30016725477c5da089Ab0A043A"
rETH2 = "0x20BC832ca081b91433ff6c17f85701B6e92486c5"
SWISE = "0x48C3399719B582dD63eB5AADf12A40B4C3f52FA2"

# Uniswap V3 contracts
UV3_NFT_POSITIONS = "0xC36442b4a4522E871399CD717aBDD847Ab11FE88"
UV3_ROUTER_2 = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"

# Lido contracts
stETH = "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"
wstETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
LDO = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"

# Convex contracts
CONVEX_BOOSTER = "0xF403C135812408BFbE8713b5A23a04b3D48AAE31"
cvxsteCRV = "0x9518c9063eB0262D791f38d8d6Eb0aca33c63ed0"
cvxsteCRV_REWARDER = "0x0A760466E1B4621579a82a39CB56Dda2F4E70f03"
cvxcDAIcUSDC = "0x32512Bee3848bfcBb7bEAf647aa697a100f3b706"
cvxcDAIcUSDC_REWARDER = "0xf34DFF761145FF0B05e917811d488B441F33a968"

# Curve contracts
CURVE_stETH_ETH_POOL = "0xDC24316b9AE028F1497c275EB9192a3Ea0f67022"
CURVE_stETH_ETH_LPTOKEN = "0x06325440D014e39736583c165C2963BA99fAf14E"
CURVE_stETH_ETH_GAUGE = "0x182B723a58739a9c974cFDB385ceaDb237453c28"
CURVE_3POOL = "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7"
crvcDAIcUSDC = "0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2"
cDAIcUSDC_POOL = "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56"
cDAIcUSDC_GAUGE = "0x7ca5b0a2910B33e9759DC7dDB0413949071D7575"
cDAIcUSDC_ZAP = "0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
CRV_MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"
CURVE_STAKE_DEPOSIT_ZAP = "0x271fbE8aB7f1fB262f81C77Ea5303F03DA9d3d6A"

# Aura contracts
AURA_BOOSTER = "0xA57b8d98dAE62B26Ec3bcC4a365338157060B234"
AURA_REWARD_POOL_DEPOSIT_WRAPPER = "0xB188b1CB84Fb0bA13cb9ee1292769F903A9feC59"
AURA_BALANCER_stETH_VAULT = "0xe4683Fe8F53da14cA5DAc4251EaDFb3aa614d528"
AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"

# Balancer contracts
BALANCER_VAULT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
B_stETH_STABLE = "0x32296969Ef14EB0c6d29669C550D4a0449130230"
B_stETH_STABLE_GAUGE = "0xcD4722B7c24C29e0413BDCd9e51404B4539D14aE"
bb_aV3_USD = "0xfeBb0bbf162E64fb9D0dfe186E517d84C395f016"
bb_aV3_DAI = "0x6667c6fa9f2b3Fc1Cc8D85320b62703d938E4385"
bb_aV3_USDT = "0xA1697F9Af0875B63DdC472d6EeBADa8C1fAB8568"
bb_aV3_USDC = "0xcbFA4532D8B2ade2C261D3DD5ef2A2284f792692"
bb_aV3_USD_GAUGE = "0x0052688295413b32626D226a205b95cDB337DE86"
B_rETH_STABLE = "0x1E19CF2D73a72Ef1332C882F20534B6519Be0276"
B_rETH_STABLE_GAUGE = "0x79eF6103A513951a3b25743DB509E267685726B7"
BAL = "0xba100000625a3754423978a60c9317c58a424e3D"

# SushiSwap contracts
SUSHISWAP_ROUTER = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"

# Rocket Pool contracts
ROCKET_POOL_SWAP_ROUTER: "0x16d5a408e807db8ef7c578279beeee6b228f1c1c"

ALLOWANCES = [
    {
        "token": USDC,
        "spender": cUSDCv3

    },
    {
        "token": bb_aV3_USD,
        "spender": AURA_BOOSTER
    },
    {
        "token": B_rETH_STABLE,
        "spender": AURA_BOOSTER
    },
    {
        "token": B_stETH_STABLE,
        "spender": AURA_BOOSTER
    },
    {
        "token": rETH,
        "spender": AURA_REWARD_POOL_DEPOSIT_WRAPPER
    },
    {
        "token": wstETH,
        "spender": AURA_REWARD_POOL_DEPOSIT_WRAPPER
    },
    {
        "token": DAI,
        "spender": BALANCER_VAULT
    },
    {
        "token": bb_aV3_DAI,
        "spender": BALANCER_VAULT
    },
    {
        "token": USDT,
        "spender": BALANCER_VAULT
    },
    {
        "token": bb_aV3_USDT,
        "spender": BALANCER_VAULT
    },
    {
        "token": USDC,
        "spender": BALANCER_VAULT
    },
    {
        "token": bb_aV3_USDC,
        "spender": BALANCER_VAULT
    },
    {
        "token": WETH,
        "spender": BALANCER_VAULT
    },
    {
        "token": wstETH,
        "spender": BALANCER_VAULT
    },
    {
        "token": rETH,
        "spender": BALANCER_VAULT
    },
    {
        "token": B_stETH_STABLE,
        "spender": B_stETH_STABLE_GAUGE
    },
    {
        "token": B_rETH_STABLE,
        "spender": B_rETH_STABLE_GAUGE
    },
    {
        "token": stETH,
        "spender": CURVE_stETH_ETH_POOL
    },
    {
        "token": CURVE_stETH_ETH_LPTOKEN,
        "spender": CURVE_stETH_ETH_GAUGE
    },
    {
        "token": stETH,
        "spender": CURVE_STAKE_DEPOSIT_ZAP
    },
    {
        "token": cDAI,
        "spender": cDAIcUSDC_POOL
    },
    {
        "token": cUSDC,
        "spender": cDAIcUSDC_POOL
    },
    {
        "token": crvcDAIcUSDC,
        "spender": cDAIcUSDC_GAUGE
    },
    {
        "token": DAI,
        "spender": cDAIcUSDC_ZAP
    },
    {
        "token": USDC,
        "spender": cDAIcUSDC_ZAP
    },
    {
        "token": cDAI,
        "spender": CURVE_STAKE_DEPOSIT_ZAP
    },
    {
        "token": cUSDC,
        "spender": CURVE_STAKE_DEPOSIT_ZAP
    },
    {
        "token": DAI,
        "spender": CURVE_STAKE_DEPOSIT_ZAP
    },
    {
        "token": USDC,
        "spender": CURVE_STAKE_DEPOSIT_ZAP
    },
    {
        "token": CURVE_stETH_ETH_LPTOKEN,
        "spender": CONVEX_BOOSTER
    },
    {
        "token": cvxsteCRV,
        "spender": cvxsteCRV_REWARDER
    },
    {
        "token": crvcDAIcUSDC,
        "spender": CONVEX_BOOSTER
    },
    {
        "token": cvxcDAIcUSDC,
        "spender": cvxcDAIcUSDC_REWARDER
    },
    {
        "token": DAI,
        "spender": AAVE_POOL_V3
    },
    {
        "token": USDC,
        "spender": AAVE_POOL_V3
    },
    {
        "token": CVX,
        "spender": UV3_ROUTER_2
    },
    {
        "token": rETH,
        "spender": ROCKET_POOL_SWAP_ROUTER
    },
]

# ALLOWANCES = [
#     {
#         "token": DAI,
#         "spender": CURVE_3POOL
#     },
#     {
#         "token": USDC,
#         "spender": CURVE_3POOL
#     },
#     {
#         "token": USDT,
#         "spender": CURVE_3POOL
#     },
# ]

""" ALLOWANCES = [
    {
        "token": stETH,
        "spender": wstETH
    },
    {
        "token": USDC,
        "spender": cUSDC
    },
    {
        "token": DAI,
        "spender": cDAI
    },
    {
        "token": sETH2,
        "spender": UV3_NFT_POSITIONS
    },
    {
        "token": WETH,
        "spender": UV3_NFT_POSITIONS
    },
    {
        "token": stETH,
        "spender": CURVE_stETH_ETH_POOL
    },
    {
        "token": CURVE_stETH_ETH_LPTOKEN,
        "spender": CURVE_stETH_ETH_GAUGE
    },
    {
        "token": WETH,
        "spender": AURA_REWARD_POOL_DEPOSIT_WRAPPER
    },
    {
        "token": COMP,
        "spender": UV3_ROUTER_2
    },
    {
        "token": rETH2,
        "spender": UV3_ROUTER_2
    },
    {
        "token": SWISE,
        "spender": UV3_ROUTER_2
    },
    {
        "token": sETH2,
        "spender": UV3_ROUTER_2
    },
    {
        "token": CRV,
        "spender": UV3_ROUTER_2
    },
    {
        "token": LDO,
        "spender": UV3_ROUTER_2
    },
    {
        "token": WETH,
        "spender": UV3_ROUTER_2
    },
    {
        "token": USDC,
        "spender": UV3_ROUTER_2
    },
    {
        "token": DAI,
        "spender": UV3_ROUTER_2
    },
    {
        "token": USDT,
        "spender": UV3_ROUTER_2
    },
    {
        "token": AURA,
        "spender": BALANCER_VAULT
    },
    {
        "token": BAL,
        "spender": BALANCER_VAULT
    },
    {
        "token": WETH,
        "spender": BALANCER_VAULT
    },
    {
        "token": COMP,
        "spender": BALANCER_VAULT
    },
    {
        "token": wstETH,
        "spender": BALANCER_VAULT
    },
    {
        "token": COMP,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": BAL,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": LDO,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": CRV,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": WETH,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": USDC,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": DAI,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": USDT,
        "spender": SUSHISWAP_ROUTER
    },
    {
        "token": DAI,
        "spender": CURVE_3POOL
    },
    {
        "token": USDC,
        "spender": CURVE_3POOL
    },
    {
        "token": USDT,
        "spender": CURVE_3POOL
    },
] """

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
web3 = get_node(ETHEREUM)

proceed = True
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Token Approvals ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print()

avatar_address = '0x4F2083f5fBede34C2714aFfb3105539775f7FE64'

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


