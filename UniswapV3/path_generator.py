from defi_protocols.functions import get_symbol, balance_of, get_node, get_data, get_decimals
from defi_protocols.UniswapV3 import FEES
from defi_protocols.constants import USDC_ETH, USDT_ETH, DAI_ETH, WETH_ETH, WBTC_ETH
from txn_uniswapv3_helpers import COMP, AAVE, RETH2, SWISE, SETH2
import itertools
from datetime import datetime
import math

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOKENS = [SETH2, COMP, AAVE, RETH2, SWISE, WETH_ETH, USDC_ETH, USDT_ETH, DAI_ETH, WBTC_ETH]

PATHS = {
    COMP: {
        USDC_ETH: [COMP, WETH_ETH, USDC_ETH],
        DAI_ETH: [COMP, WETH_ETH, DAI_ETH],
        WETH_ETH: [COMP, WETH_ETH]
    },
    AAVE: {
        USDC_ETH: [AAVE, WETH_ETH, USDC_ETH],
        DAI_ETH: [AAVE, WETH_ETH, DAI_ETH],
        WETH_ETH: [AAVE, WETH_ETH]
    },
    RETH2: {
        USDC_ETH: [RETH2, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [RETH2, SETH2, WETH_ETH, DAI_ETH],
        WETH_ETH: [RETH2, SETH2, WETH_ETH]
    },
    SWISE: {
        USDC_ETH: [SWISE, SETH2, WETH_ETH, USDC_ETH],
        DAI_ETH: [SWISE, SETH2, WETH_ETH, DAI_ETH],
        WETH_ETH: [SWISE, SETH2, WETH_ETH]
    },
    SETH2: {
        WETH_ETH: [SETH2, WETH_ETH]
    },
    WETH_ETH: {
        SETH2: [WETH_ETH, SETH2],
        USDC_ETH: [WETH_ETH, USDC_ETH],
        USDT_ETH: [WETH_ETH, USDT_ETH],
        DAI_ETH: [WETH_ETH, DAI_ETH],
        WBTC_ETH: [WETH_ETH, WBTC_ETH]
    },
    USDC_ETH: {
        WETH_ETH: [USDC_ETH, WETH_ETH],
        USDT_ETH: [[USDC_ETH, USDT_ETH], [USDC_ETH, WETH_ETH, USDT_ETH]],
        DAI_ETH: [[USDC_ETH, DAI_ETH], [USDC_ETH, WETH_ETH, DAI_ETH]]
    },
    USDT_ETH: {
        WETH_ETH: [USDT_ETH, WETH_ETH],
        USDC_ETH: [[USDT_ETH, USDC_ETH], [USDT_ETH, WETH_ETH, USDC_ETH]],
        DAI_ETH: [[USDT_ETH, DAI_ETH], [USDT_ETH, WETH_ETH, DAI_ETH]]
    },
    DAI_ETH: {
        WETH_ETH: [DAI_ETH, WETH_ETH],
        USDC_ETH: [[DAI_ETH, USDC_ETH], [DAI_ETH, WETH_ETH, USDC_ETH]],
        USDT_ETH: [[DAI_ETH, USDT_ETH], [DAI_ETH, WETH_ETH, USDT_ETH]]
    },
    WBTC_ETH: {
        WETH_ETH: [WBTC_ETH, WETH_ETH]
    },
}

matrix = []
for token in TOKENS:
     for swap_token in PATHS[token]:
        if isinstance(PATHS[token][swap_token][0], list):
            for i in range(len(PATHS[token][swap_token])):
                if len(PATHS[token][swap_token][i])-1 == 1:
                    matrix.append(FEES)
                else:
                    matrix.append([p for p in itertools.product(FEES, repeat=len(PATHS[token][swap_token][i])-1)])
        else:
            if len(PATHS[token][swap_token])-1 == 1:
                matrix.append(FEES)
            else:
                matrix.append([p for p in itertools.product(FEES, repeat=len(PATHS[token][swap_token])-1)])


matrix_index = 0
paths = []
for token in TOKENS:
     for swap_token in PATHS[token]:
        if isinstance(PATHS[token][swap_token][0], list):
            for i in range(len(PATHS[token][swap_token])):
                if len(PATHS[token][swap_token][i])-1 == 1:
                    for fee in matrix[matrix_index]:
                        for j in range(len(PATHS[token][swap_token])-1):
                            if j == 0:
                                path = PATHS[token][swap_token][i][j]
                                path += hex(fee)[2:].rjust(6, '0')
                            path += PATHS[token][swap_token][i][j+1][2:]

                            paths.append(path)
                    
                    matrix_index += 1
                else:
                    for position in matrix[matrix_index]:
                        for j in range(len(PATHS[token][swap_token][i])-1):
                            if j == 0:
                                path = PATHS[token][swap_token][i][j]
                            path += hex(position[j])[2:].rjust(6, '0')
                            path += PATHS[token][swap_token][i][j+1][2:]

                        paths.append(path)
                    
                    matrix_index += 1
        else:
            if len(PATHS[token][swap_token])-1 == 1:
                for fee in matrix[matrix_index]:
                    for i in range(len(PATHS[token][swap_token])-1):
                        if i == 0:
                            path = PATHS[token][swap_token][i]
                            path += hex(fee)[2:].rjust(6, '0')
                        path += PATHS[token][swap_token][i+1][2:]

                        paths.append(path)
                
                matrix_index += 1
                    
            else:
                for position in matrix[matrix_index]:
                    for i in range(len(PATHS[token][swap_token])-1):
                        if i == 0:
                            path = PATHS[token][swap_token][i]
                        path += hex(position[i])[2:].rjust(6, '0')
                        path += PATHS[token][swap_token][i+1][2:]

                    paths.append(path)
                
                matrix_index += 1
            

with open('paths.txt','w') as tfile:
	tfile.write('"{}"'.format('",\n"'.join(paths)))