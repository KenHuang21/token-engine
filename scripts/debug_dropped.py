import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.cobo_service import cobo_client

TX_ID = "5b63306c-7ae2-41ce-89a2-79101a23eb96"

try:
    print(f"Fetching transaction {TX_ID}...")
    tx = cobo_client.get_transaction(TX_ID)
    print("Raw Transaction Object:")
    print(tx)
    print("\nAttributes:")
    print(f"Status: {tx.status} (Type: {type(tx.status)})")
    if hasattr(tx, 'transaction_hash'):
        print(f"Hash: {tx.transaction_hash}")
except Exception as e:
    print(f"Error: {e}")
