import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.cobo_service import cobo_client

TX_ID = "9fa3df2e-88ee-42cd-acaf-d5d72d519093"

try:
    print(f"Fetching transaction {TX_ID}...")
    tx = cobo_client.get_transaction(TX_ID)
    print("Raw Transaction Object:")
    print(tx)
    print("\nAttributes:")
    print(f"Status: {tx.status} (Type: {type(tx.status)})")
    print(f"Hash: {tx.transaction_hash}")
except Exception as e:
    print(f"Error: {e}")
