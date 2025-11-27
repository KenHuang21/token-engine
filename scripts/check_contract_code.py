import sys
import os
from web3 import Web3

RPC_URL = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDRESS = "0x8183F65a9f2EC6B9bF4c07Fc9B41Ef0A9E316d2f"

try:
    print(f"Checking code at {CONTRACT_ADDRESS}...")
    code = w3.eth.get_code(CONTRACT_ADDRESS)
    if code and code != b'':
        print("Contract exists! Code length:", len(code))
    else:
        print("No code found at address.")
except Exception as e:
    print(f"Error: {e}")
