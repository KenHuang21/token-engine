import json
import os
from typing import List, Dict, Any

# Use absolute path for Vercel compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level from 'backend' to root, then into 'backend' (redundant but safe if structure changes)
# Actually, this file is in 'backend/', so DB_FILE should be in the same dir or we resolve from root.
# Let's assume db.json is in 'backend/' alongside database.py
DB_FILE = os.path.join(BASE_DIR, "db.json")

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {"contracts": []}
    with open(DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"contracts": []}

def save_db(data: Dict[str, Any]):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except OSError:
        # Vercel file system is read-only
        print("Warning: Could not write to database (Read-only filesystem)")

def add_contract(contract: Dict[str, Any]):
    db = load_db()
    db["contracts"].append(contract)
    save_db(db)

def get_contracts() -> List[Dict[str, Any]]:
    db = load_db()
    return db["contracts"]

def add_mint_event(event: Dict[str, Any]):
    db = load_db()
    if "mints" not in db:
        db["mints"] = []
    db["mints"].append(event)
    save_db(db)

def get_mint_events(chain_id: str, contract_address: str) -> List[Dict[str, Any]]:
    db = load_db()
    return [
        m for m in db.get("mints", []) 
        if m.get("chain_id") == chain_id and m.get("contract_address").lower() == contract_address.lower()
    ]
