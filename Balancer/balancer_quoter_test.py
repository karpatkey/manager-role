
from defi_protocols.functions import get_node, get_contract, date_to_block
from defi_protocols.constants import ETHEREUM, DAI_ETH
from defi_protocols.Balancer import VAULT
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

# ABI Balancer Queries - queryExit, queryJoin, querySwap
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]'


web3 = get_node(ETHEREUM)
balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, web3=web3, abi=ABI_BALANCER_QUERIES)
exit_kind = 0 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
abi = ['uint256', 'uint256']
data = [exit_kind, 1]

user_data = '0x' + eth_abi.encode(abi, data).hex()
exit_pool_ = balancer_queries.functions.querySwap([bb_a_DAI_pid, exit_kind, bb_a_DAI, DAI_ETH, 1000000000000000000, '0x'], [VAULT, False, VAULT, False]).call(block_identifier=17929096)
print(exit_pool_)

block = date_to_block('2023-07-31 00:00:00', 'ethereum')
print(block)
web3 = get_node(ETHEREUM)
balancer_queries = get_contract(BALANCER_QUERIES, ETHEREUM, web3=web3, abi=ABI_BALANCER_QUERIES)
exit_kind = 255 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
abi = ['uint256', 'uint256']
data = [exit_kind, 1]

user_data = '0x' + eth_abi.encode(abi, data).hex()
exit_pool_ = balancer_queries.functions.queryExit(bb_a_USD_pid, '0x4971DD016127F390a3EF6b956Ff944d0E2e1e462', '0x4971DD016127F390a3EF6b956Ff944d0E2e1e462', [[bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD], [0, 0, 0, 0], user_data, False]).call()
print(exit_pool_)

web3 = get_node(ETHEREUM)
lp = get_contract(bb_a_USD, ETHEREUM, web3=web3)
vault = get_contract(VAULT, ETHEREUM, web3=web3)
pool_balances = vault.functions.getPoolTokens(bb_a_USD_pid).call()[1]
last_change_block = vault.functions.getPoolTokens(bb_a_USD_pid).call()[2]
swap_fee_percentage = lp.functions.getSwapFeePercentage().call()
exit_kind = 255 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
abi = ['uint256', 'uint256']
data = [exit_kind, 5320659221425715023755]

user_data = '0x' + eth_abi.encode(abi, data).hex()
exit_pool_1 = lp.functions.onExitPool(bb_a_USD_pid, vault.address, vault.address, pool_balances, last_change_block, swap_fee_percentage, user_data).call({"from": vault.address})
print(exit_pool_1)

lp = get_contract(bb_a_DAI, ETHEREUM, web3=web3)
pool_balances = vault.functions.getPoolTokens(bb_a_DAI_pid).call()[1]
last_change_block = vault.functions.getPoolTokens(bb_a_DAI_pid).call()[2]
swap_fee_percentage = lp.functions.getSwapFeePercentage().call()
exit_kind = 255 # EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
abi = ['uint256', 'uint256']
data = [exit_kind, exit_pool_1[0][0]]

user_data = '0x' + eth_abi.encode(abi, data).hex()
exit_pool_2 = lp.functions.onExitPool(bb_a_DAI_pid, vault.address, vault.address, pool_balances, last_change_block, swap_fee_percentage, user_data).call({"from": vault.address})
print(exit_pool_2)