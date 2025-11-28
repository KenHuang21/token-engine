import json
import os
from backend.services.cobo_service import cobo_client
from cobo_waas2.models.transaction_type import TransactionType

DB_FILE = "backend/db.json"
WALLET_ID = "e4288c49-bbf3-47f6-97e5-1bcf0060e53e"
TARGET_ADDRESS = "0xd4402d1e46f1b13b3d1e683b2604c93dd91075b9"

def discover_contracts():
    print(f"🔍 Discovering contracts for wallet {WALLET_ID}...")
    
    # List transactions
    txs = cobo_client.list_transactions(wallet_id=WALLET_ID, limit=50)
    print(f"Found {len(txs)} transactions.")
    
    found_contract = None
    
    for tx in txs:
        # Check if it's a ContractCall
        if tx.type == TransactionType.CONTRACTCALL:
            # Check if it's a deployment (destination address might be empty or match target)
            # Note: Cobo response model for ContractCallDestination might vary.
            # Let's check the transaction details or result.
            
            # If we can't easily distinguish deployment from call without parsing calldata,
            # let's look at the 'result' or 'status'.
            # But wait, the user said "address ... is deployed".
            # So we are looking for a transaction that RESULTED in this address.
            # Or maybe the user means this address IS the contract address?
            # "contract deployed via wallet id ... and address ... is deployed"
            # It's likely 0xd440... is the CONTRACT address.
            # Wait, 0xd440... was the OWNER in my previous code (mock_owner).
            # Let's check if 0xd440... is the wallet address or contract address.
            # In my logs: "Found wallet: ... (0xd4402d1e46f1b13b3d1e683b2604c93dd91075b9)"
            # So 0xd440... is the WALLET address.
            
            # Ah, the user said: "contract deployed via wallet id ... and address 0xd440... is deployed"
            # This might mean: "The contract deployed BY wallet X (address Y) is deployed".
            # So I need to find the contract deployed BY this wallet.
            # I don't know the contract address yet. I need to find it.
            
            # So, look for transactions from this wallet where destination is empty (deployment).
            # Then get the created contract address from the result.
            
            # However, `list_transactions` returns `Transaction` objects.
            # We need to check `destination` inside `source` or `destination` field.
            # Actually `destination` in `Transaction` model.
            
            # Let's inspect the transaction.
            pass

    # Since we are not sure about the structure without running, let's print them first.
    # But to be useful, let's try to find any deployment.
    
    new_contracts = []
    
    for tx in txs:
        if tx.type == TransactionType.CONTRACTCALL:
            # Check destination
            dest = tx.destination
            # If destination type is EVM_Contract and address is empty, it's a deployment.
            # Or if it's a specific "ContractCallDestination" type.
            
            # Let's assume we can check `tx.destination.actual_instance.address`
            address = getattr(tx.destination.actual_instance, 'address', None)
            
            if address == "" or address is None:
                print(f"Found potential deployment TX: {tx.transaction_id}")
                # Get full details to find created address
                details = cobo_client.get_transaction(tx.transaction_id)
                
                # Where is the created address?
                # Usually in `chain_tx_hash` we can find it on explorer, but Cobo might return it?
                # If not, we might just have to add it as "Unknown Address" or use the TX hash.
                # But the user wants to display it.
                
                # Let's assume for now we add it.
                # We need a name.
                name = f"Imported Contract {tx.transaction_id[:8]}"
                
                contract = {
                    "name": name,
                    "symbol": "IMP",
                    "chain_id": tx.chain_id,
                    "contract_address": "Pending", # We don't know it yet from here
                    "type": "MANAGED",
                    "status": "Deployed",
                    "partitions": ["Imported"],
                    "owner": TARGET_ADDRESS,
                    "tx_hash": details.transaction_hash if details else "",
                    "cobo_id": tx.transaction_id
                }
                new_contracts.append(contract)

    if new_contracts:
        print(f"Adding {len(new_contracts)} contracts to DB.")
        
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"contracts": [], "mints": []}
            
        # Avoid duplicates
        existing_ids = [c.get("cobo_id") for c in data["contracts"]]
        
        for c in new_contracts:
            if c["cobo_id"] not in existing_ids:
                data["contracts"].append(c)
                print(f"Added {c['cobo_id']}")
            else:
                print(f"Skipping duplicate {c['cobo_id']}")
                
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print("No deployments found.")

if __name__ == "__main__":
    discover_contracts()
