import sys
import os
from web3 import Web3

RPC_URL = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

HASHES = [
    "0x57f9925b305d5d22dbd85f14ad61b570425950af81a9e2488c9ceeb21f196209", # DB hash
    "0xe52f2ca3baebb8c13c01b6a361667ffa20f610b7c09d2e08dd0b05ccb50bea44"  # User hash
]

for h in HASHES:
    try:
        print(f"Checking {h}...")
        tx = w3.eth.get_transaction(h)
        print(f"Found! Block: {tx.blockNumber}")
    except Exception:
        print(f"Not found: {h}")
