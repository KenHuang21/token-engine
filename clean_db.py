import json
import os

DB_FILE = "backend/db.json"

def clean_db():
    if not os.path.exists(DB_FILE):
        print("DB file not found.")
        return

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    original_contracts_count = len(data.get("contracts", []))
    original_mints_count = len(data.get("mints", []))

    # Filter contracts: Keep if tx_hash is NOT a hex string starting with 0x (assuming Cobo IDs are UUIDs)
    # Also check if it has a valid UUID format if possible, but !startswith("0x") is a good heuristic given the mock generation.
    # Mock generation: fake_tx = f"0x{os.urandom(32).hex()}"
    real_contracts = [
        c for c in data.get("contracts", [])
        if not c.get("tx_hash", "").startswith("0x")
    ]

    # Filter mints: Keep if tx_id does NOT start with "mock_"
    # Mock generation: tx_id = f"mock_mint_{os.urandom(4).hex()}"
    real_mints = [
        m for m in data.get("mints", [])
        if not m.get("tx_id", "").startswith("mock_")
    ]

    data["contracts"] = real_contracts
    data["mints"] = real_mints

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Cleaned DB.")
    print(f"Contracts: {original_contracts_count} -> {len(real_contracts)}")
    print(f"Mints: {original_mints_count} -> {len(real_mints)}")

if __name__ == "__main__":
    clean_db()
