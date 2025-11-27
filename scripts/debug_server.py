import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting debug script...")

try:
    print("Importing database...")
    from backend.database import load_db
    print("Loading DB...")
    db = load_db()
    print(f"DB loaded. Contracts: {len(db.get('contracts', []))}")
except Exception as e:
    print(f"DB Error: {e}")

try:
    print("Importing cobo_service...")
    from backend.services.cobo_service import cobo_client
    print("Cobo client imported.")
    if cobo_client.api_client:
        print("Cobo client initialized successfully.")
    else:
        print("Cobo client initialization failed (expected if env vars missing).")
except Exception as e:
    print(f"Cobo Error: {e}")

try:
    print("Importing routes...")
    from backend.api import routes
    print("Routes imported.")
except Exception as e:
    print(f"Routes Error: {e}")

print("Debug finished.")
