from defi_protocols.functions import get_node, get_contract
from defi_protocols.constants import ETHEREUM

# Current Deployments: https://docs.rocketpool.net/overview/contracts-integrations.html

# https://docs.rocketpool.net/developers/usage/contracts/contracts.html
# The central hub of the network is the RocketStorage contract, which is responsible for storing the state of the 
# entire protocol. This is implemented through the use of maps for key-value storage, and getter and setter methods for 
# reading and writing values for a key.
# The RocketStorage contract also stores the addresses of all other network contracts (keyed by name), 
# and restricts data modification to those contracts only.
# Because of Rocket Pool's architecture, the addresses of other contracts should not be used directly but retrieved 
# from the blockchain before use. Network upgrades may have occurred since the previous interaction, resulting in 
# outdated addresses. RocketStorage can never change address, so it is safe to store a reference to it.

ROCKET_STORAGE = '0x1d8f8f00cfa6758d7bE78336684788Fb0ee0Fa46'

web3 = get_node(ETHEREUM)
# https://web3py.readthedocs.io/en/stable/web3.main.html -> see Web3.solidity_keccak
rocket_pool_key = web3.solidity_keccak(["string", "string"],["contract.address", "rocketDepositPool"]).hex()

rocket_storage = get_contract(ROCKET_STORAGE, ETHEREUM)
rocket_pool_address = rocket_storage.functions.getAddress(rocket_pool_key).call()

print(rocket_pool_address)