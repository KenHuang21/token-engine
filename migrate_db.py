import json
import os

DB_FILE = "backend/db.json"

def migrate_db():
    if not os.path.exists(DB_FILE):
        print("DB file not found.")
        return

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    updated = False
    for c in data.get("contracts", []):
        # Check if tx_hash looks like a UUID (Cobo ID) and cobo_id is missing
        tx_hash = c.get("tx_hash", "")
        if len(tx_hash) == 36 and "-" in tx_hash and not c.get("cobo_id"):
            print(f"Migrating contract {c['name']}...")
            c["cobo_id"] = tx_hash
            c["tx_hash"] = "" # Clear it, will be resolved to chain hash
            c["status"] = "Pending" # Force resolution
            updated = True

    if updated:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("DB migrated.")
    else:
        print("No migration needed.")

if __name__ == "__main__":
    migrate_db()
