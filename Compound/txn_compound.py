from defi_protocols import Compound
from defi_protocols.functions import get_contract, get_symbol, get_node
from defi_protocols.constants import ETHEREUM, E_ADDRESS
from pathlib import Path
import os
import json
from web3.exceptions import BadFunctionCallOutput

cUSDCv3 = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"

# numAssets, getAssetInfo
ABI_CTOKENV3 = '[{"inputs":[],"name":"numAssets","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint8","name":"i","type":"uint8"}],"name":"getAssetInfo","outputs":[{"components":[{"internalType":"uint8","name":"offset","type":"uint8"},{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"priceFeed","type":"address"},{"internalType":"uint64","name":"scale","type":"uint64"},{"internalType":"uint64","name":"borrowCollateralFactor","type":"uint64"},{"internalType":"uint64","name":"liquidateCollateralFactor","type":"uint64"},{"internalType":"uint64","name":"liquidationFactor","type":"uint64"},{"internalType":"uint128","name":"supplyCap","type":"uint128"}],"internalType":"struct CometCore.AssetInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]'

# Comptroller ABI - getAllMarkets, mintGuardianPaused
ABI_COMPTROLLER = '[{"constant":true,"inputs":[],"name":"getAllMarkets","outputs":[{"internalType":"contract CToken[]","name":"","type":"address[]"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"mintGuardianPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"}]'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# markets_data_v2
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def markets_data_v2(blockchain):
    result = []

    web3 = get_node(blockchain)

    comptroller_address = Compound.get_comptoller_address(blockchain)
    comptroller_contract = get_contract(comptroller_address, blockchain, web3=web3, abi=ABI_COMPTROLLER)

    markets = comptroller_contract.functions.getAllMarkets().call()

    print(len(markets))
    i = 1
    for ctoken in markets:
        market = {}
        ctoken_contract = get_contract(ctoken, blockchain, web3=web3, abi=Compound.ABI_CTOKEN)
        market['cToken'] = ctoken
        try:
            market['token'] = ctoken_contract.functions.underlying().call()
        except BadFunctionCallOutput:
            market['token'] = E_ADDRESS
        
        market['symbol'] = get_symbol(market['token'], blockchain, web3=web3)
        market['mint_paused'] = comptroller_contract.functions.mintGuardianPaused(ctoken).call()

        result.append(market)

        print(i)
        i+=1

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/markets_data_v2.json', 'w') as markets_data_file:
        json.dump(result, markets_data_file)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# markets_data_v3
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def markets_data_v3(blockchain):
    result = []

    web3 = get_node(blockchain)

    comet_contract = get_contract(cUSDCv3, blockchain, web3=web3, abi=ABI_CTOKENV3)

    markets_len = comet_contract.functions.numAssets().call()

    print(markets_len)
    for i in range(markets_len):
        market = {}

        market['token'] = comet_contract.functions.getAssetInfo(i).call()[1]
        market['symbol'] = get_symbol(market['token'], blockchain, web3=web3)

        result.append(market)

        print(i)
        i+=1

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/markets_data_v3.json', 'w') as markets_data_file:
        json.dump(result, markets_data_file)

markets_data_v2(ETHEREUM)
#markets_data_v3(ETHEREUM)