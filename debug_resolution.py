import os
import sys
from web3 import Web3
from backend.services.cobo_service import cobo_client

# Mock settings if needed, or rely on env
# Assuming env vars are set in the shell running this

def resolve_contract_address(tx_hash: str):
    print(f"Resolving {tx_hash}...")
    rpc_url = "https://bsc-dataseed.binance.org/"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        print(f"Receipt found. Status: {receipt.status}")
        print(f"Contract Address: {receipt.contractAddress}")
        return receipt.contractAddress
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    cobo_id = "758088a9-e23a-4d0b-9ec2-f6c69933baf0"
    print(f"Fetching Cobo TX {cobo_id}...")
    try:
        tx = cobo_client.get_transaction(cobo_id)
        print(f"Cobo Status: {tx.status}")
        print(f"Chain Hash: {tx.transaction_hash}")
        
        if tx.transaction_hash:
            resolve_contract_address(tx.transaction_hash)
        else:
            print("No chain hash yet.")
            
    except Exception as e:
        print(f"Cobo Error: {e}")

if __name__ == "__main__":
    main()
