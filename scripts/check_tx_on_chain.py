import sys
import os
from web3 import Web3

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.cobo_service import cobo_client

RPC_URL = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

TX_HASH = "0x57f9925b305d5d22dbd85f14ad61b570425950af81a9e2488c9ceeb21f196209"
SENDER = "0xD4402D1e46f1B13b3D1E683b2604C93dD91075B9"

try:
    print(f"Checking tx: {TX_HASH}")
    try:
        tx = w3.eth.get_transaction(TX_HASH)
        print("Transaction found on chain (Pending or Mined).")
        print(tx)
    except Exception:
        print("Transaction NOT found on chain.")
        
    # Check nonce
    current_nonce = w3.eth.get_transaction_count(SENDER)
    print(f"Current Nonce for {SENDER}: {current_nonce}")
    
except Exception as e:
    print(f"Error: {e}")
