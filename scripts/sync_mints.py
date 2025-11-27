import sys
import os
import json
import time
from web3 import Web3
from hexbytes import HexBytes

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import load_db, save_db, add_mint_event

# Configuration
RPC_URL = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_abi():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/artifacts/SimpleERC1400.json'))
    with open(path, 'r') as f:
        return json.load(f)['abi']

def sync_mints():
    db = load_db()
    contracts = db.get("contracts", [])
    abi = get_abi()
    
    print(f"Syncing mints for {len(contracts)} contracts...")
    
    for c in contracts:
        if c.get("status") != "Deployed" or not c.get("contract_address"):
            continue
            
        address = c["contract_address"]
        print(f"Checking {c['name']} at {address}...")
        
        contract = w3.eth.contract(address=address, abi=abi)
        
        # Fetch IssuedByPartition events
        # In production, we should track last synced block. For MVP, look back 5000 blocks.
        try:
            # Sync specific transactions
            tx_hashes = [
                "0xc24c45cc22d4a91419497590bd763303d20499f7fe472ec8ee302a5058864293", # Class A
                "0x7db1c6e182c92be4a8f406c10c3f058895a3d043473cc5b09c10dcc7e2fa475a"  # Class B
            ]
            
            for tx_hash in tx_hashes:
                print(f"Syncing specific tx: {tx_hash}")
                try:
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    logs = receipt['logs']
                    print(f"Found {len(logs)} logs in tx.")
                    
                    events = []
                    for log in logs:
                        try:
                            # Process log using contract event wrapper
                            events.append(contract.events.IssuedByPartition().process_log(log))
                        except Exception as e:
                            pass # Not an IssuedByPartition event
                    
                    for e in events:
                        # Check if event belongs to this contract
                        if e['address'].lower() != address.lower():
                            continue
                            
                        # Parse event
                        args = e['args']
                        partition_bytes = args['partition']
                        to_address = args['to']
                        amount = args['value']
                        
                        # Decode partition (bytes32 to string)
                        try:
                            partition = partition_bytes.decode('utf-8').rstrip('\x00')
                        except:
                            partition = partition_bytes.hex()
                        
                        # Check if already exists
                        existing = [m for m in db.get("mints", []) if m.get("tx_id") == tx_hash]
                        
                        if not existing:
                            print(f"Adding mint: {amount} to {to_address} ({partition})")
                            add_mint_event({
                                "chain_id": c["chain_id"],
                                "contract_address": address,
                                "partition": partition,
                                "to_address": to_address,
                                "amount": amount,
                                "tx_id": tx_hash,
                                "timestamp": int(time.time())
                            })
                        else:
                            print(f"Skipping existing mint {tx_hash}")
                except Exception as e:
                    print(f"Error syncing {tx_hash}: {e}")
                    
        except Exception as err:
            print(f"Error syncing {address}: {err}")

if __name__ == "__main__":
    sync_mints()
