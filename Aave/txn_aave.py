from defi_protocols.functions import *
from defi_protocols.constants import *
from defi_protocols import Aave
from pathlib import Path
from helper_functions.helper_functions import * 
import os

PDPV3_ETHEREUM = '0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# reserves_tokens_data
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def reserves_tokens_data(version=2):

    # try:
    #     with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/reserves_tokens_data.json', 'r') as reserves_tokens_file:
    #         # Reading from json file
    #         reserves_tokens_data = json.load(reserves_tokens_file)
    # except:
    reserves_tokens_data = []
    
    web3 = get_node(ETHEREUM)

    if version == 2:
        pdp_contract = get_contract(Aave.PDP_ETHEREUM, ETHEREUM, web3=web3, abi=Aave.ABI_PDP)
    elif version == 3:
        pdp_contract = get_contract(PDPV3_ETHEREUM, ETHEREUM, web3=web3, abi=Aave.ABI_PDP)
    else:
        return "Error: wrong version!"

    reserves_tokens = pdp_contract.functions.getAllReservesTokens().call()
    
    print(len(reserves_tokens))
    i = 1
    for reserve_token in reserves_tokens:
        token_data = {}

        token_data['symbol'] = reserve_token[0]
        token_data['token'] = reserve_token[1]

        token_config = pdp_contract.functions.getReserveConfigurationData(token_data['token']).call()

        token_data['usageAsCollateralEnabled'] = token_config[5]
        token_data['borrowingEnabled'] = token_config[6]
        token_data['stableBorrowRateEnabled'] = token_config[7]
        token_data['isActive'] = token_config[8]
        token_data['isFrozen'] = token_config[9]

        token_addresses = pdp_contract.functions.getReserveTokensAddresses(token_data['token']).call()

        token_data['aTokenAddress'] = token_addresses[0]
        token_data['stableDebtTokenAddress'] = token_addresses[1]
        token_data['variableDebtTokenAddress'] = token_addresses[2]

        reserves_tokens_data.append(token_data)

        print(i)
        i += 1


    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/reserves_tokens_data_v' + str(version) + '.json', 'w') as reserves_tokens_file:
        json.dump(reserves_tokens_data, reserves_tokens_file)


# reserves_tokens_data()

# web3 = get_node(ETHEREUM)
# avatar_address = '0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89'
# roles_mod_address = '0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9'

# json_file = {
#     'version': '1.0',
#     'chainId': '1',
#     'meta': {
#         'name': None,
#         'description': '',
#         'txBuilderVersion': '1.8.0'
#     },
#     'createdAt': math.floor(datetime.now().timestamp()*1000),
#     'transactions': []
# }
# tx_data = get_data(STKAAVE_ETH, 'redeem', [avatar_address, 16907290000000000000002], ETHEREUM, web3=web3)
# if tx_data is not None:
#     add_txn_with_role(roles_mod_address, STKAAVE_ETH, tx_data, 0, json_file, web3=web3)

# json_file_download(json_file)
