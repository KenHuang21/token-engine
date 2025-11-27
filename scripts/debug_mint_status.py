import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.cobo_service import cobo_client

TX_ID = "9735c5b2-37fe-453f-a9fb-2417ad6203e3"

try:
    print(f"Fetching transaction {TX_ID}...")
    tx = cobo_client.get_transaction(TX_ID)
    print("Raw Transaction Object:")
    print(tx)
    print("\nAttributes:")
    print(f"Status: {tx.status}")
    if hasattr(tx, 'transaction_hash'):
        print(f"Hash: {tx.transaction_hash}")
except Exception as e:
    print(f"Error: {e}")
