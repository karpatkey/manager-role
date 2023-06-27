from defi_protocols import Compound
from defi_protocols.functions import get_contract, get_symbol, get_node
from defi_protocols.constants import ETHEREUM, E_ADDRESS
from pathlib import Path
import os
import json
from web3.exceptions import BadFunctionCallOutput

COMETS = [
    {
        'address': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
        'symbol': 'cUSDCv3'
    },
    {
        'address': '0xA17581A9E3356d9A858b789D68B4d866e593aE94',
        'symbol': 'cWETHv3'
    }
]

# numAssets, getAssetInfo, baseToken
ABI_COMET = '[{"inputs":[],"name":"numAssets","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint8","name":"i","type":"uint8"}],"name":"getAssetInfo","outputs":[{"components":[{"internalType":"uint8","name":"offset","type":"uint8"},{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"priceFeed","type":"address"},{"internalType":"uint64","name":"scale","type":"uint64"},{"internalType":"uint64","name":"borrowCollateralFactor","type":"uint64"},{"internalType":"uint64","name":"liquidateCollateralFactor","type":"uint64"},{"internalType":"uint64","name":"liquidationFactor","type":"uint64"},{"internalType":"uint128","name":"supplyCap","type":"uint128"}],"internalType":"struct CometCore.AssetInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"baseToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

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

    for comet in COMETS:
        comet_contract = get_contract(comet['address'], blockchain, web3=web3, abi=ABI_COMET)
        comet_data = {}
        comet_data['address'] = comet['address']
        comet_data['symbol'] = comet['symbol']
        base_token = comet_contract.functions.baseToken().call()
        base_token_symbol = get_symbol(base_token, blockchain, web3=web3)
        
        if base_token_symbol == 'WETH':
            comet_data['borrowToken'] = {
                'address': E_ADDRESS,
                'symbol': 'ETH'
            }
        else:
            comet_data['borrowToken'] = {
                'address': base_token,
                'symbol': base_token_symbol
            }

        comet_data['collateralTokens'] = []

        markets_len = comet_contract.functions.numAssets().call()

        print(markets_len)
        for i in range(markets_len):
            market = {}

            market['address'] = comet_contract.functions.getAssetInfo(i).call()[1]
            market['symbol'] = get_symbol(market['address'], blockchain, web3=web3)

            if market['symbol'] == 'WETH':
                market['address'] = E_ADDRESS
                market['symbol'] = 'ETH'

            comet_data['collateralTokens'].append(market)

            print(i)
            i+=1
        
        result.append(comet_data)

    with open(str(Path(os.path.abspath(__file__)).resolve().parents[0])+'/markets_data_v3.json', 'w') as markets_data_file:
        json.dump(result, markets_data_file)

#markets_data_v2(ETHEREUM)
markets_data_v3(ETHEREUM)