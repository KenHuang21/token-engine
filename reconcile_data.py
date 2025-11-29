import json
import os
import sys
from web3 import Web3
from backend.services.cobo_service import cobo_client

# Setup Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
DB_FILE = os.path.join(BASE_DIR, "db.json")

# Setup Web3
BSC_RPC = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(BSC_RPC))

def load_db():
    if not os.path.exists(DB_FILE):
        print(f"❌ DB file not found at {DB_FILE}")
        return {"contracts": [], "mints": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("💾 Database updated.")

def verify_cobo_tx(tx_id):
    try:
        tx = cobo_client.get_transaction(tx_id)
        if not tx:
            return False
        # Check if successful or pending (broadcasting)
        status = str(tx.status)
        return status in ["TransactionStatus.SUCCESS", "TransactionStatus.BROADCASTING", "TransactionStatus.PENDING_APPROVAL", "TransactionStatus.QUEUED"]
    except Exception as e:
        print(f"⚠️ Cobo check failed for {tx_id}: {e}")
        return False # Assume invalid if not found or error

def verify_chain_tx(tx_hash):
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return receipt.status == 1
    except Exception:
        # If receipt not found, it might be dropped or invalid
        return False

def reconcile():
    print("🔍 Starting Reconciliation...")
    data = load_db()
    
    valid_contracts = []
    valid_mints = []
    
    # 1. Reconcile Contracts
    print(f"Checking {len(data.get('contracts', []))} contracts...")
    for c in data.get("contracts", []):
        is_valid = False
        name = c.get("name", "Unknown")
        
        # Check based on type
        if c.get("cobo_id"):
            # Managed
            if verify_cobo_tx(c["cobo_id"]):
                is_valid = True
            else:
                print(f"❌ Removing Invalid Managed Contract: {name} (Cobo ID: {c['cobo_id']})")
        
        elif c.get("tx_hash") and c["tx_hash"].startswith("0x"):
            # Self-Custody
            if verify_chain_tx(c["tx_hash"]):
                is_valid = True
            else:
                print(f"❌ Removing Invalid Self-Custody Contract: {name} (Tx: {c['tx_hash']})")
        else:
            # No ID or Hash? Invalid.
            print(f"❌ Removing Malformed Contract: {name}")
            
        if is_valid:
            valid_contracts.append(c)

    # 2. Reconcile Mints
    print(f"Checking {len(data.get('mints', []))} mints...")
    for m in data.get("mints", []):
        is_valid = False
        tx_id = m.get("tx_id", "")
        
        if not tx_id:
            continue
            
        if tx_id.startswith("mock_"):
            # Mock data - User asked to "clean up", so maybe remove mocks?
            # Let's assume we remove mocks if we are doing "onchain verification"
            print(f"❌ Removing Mock Mint: {tx_id}")
            is_valid = False
        elif tx_id.startswith("0x"):
            # Chain Hash
            if verify_chain_tx(tx_id):
                is_valid = True
            else:
                print(f"❌ Removing Failed/Missing Chain Mint: {tx_id}")
        else:
            # Assume Cobo UUID
            if verify_cobo_tx(tx_id):
                is_valid = True
            else:
                print(f"❌ Removing Failed/Missing Cobo Mint: {tx_id}")
        
        if is_valid:
            valid_mints.append(m)
            
    # Summary
    print(f"Contracts: {len(data.get('contracts', []))} -> {len(valid_contracts)}")
    print(f"Mints: {len(data.get('mints', []))} -> {len(valid_mints)}")
    
    # Save
    data["contracts"] = valid_contracts
    data["mints"] = valid_mints
    save_db(data)

if __name__ == "__main__":
    reconcile()
