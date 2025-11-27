from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.services.contract_service import deploy_erc1400, mint_by_partition, set_document, get_artifact
from backend.database import add_contract, get_contracts, load_db, save_db, add_mint_event, get_mint_events
from backend.services.cobo_service import cobo_client
from web3 import Web3
import time

router = APIRouter()

class DeployRequest(BaseModel):
    chain_id: str
    name: str
    symbol: str
    partitions: List[str]
    supply: int = 0

class MintRequest(BaseModel):
    chain_id: str
    contract_address: str
    partition: str
    to_address: str
    amount: int

class DocumentRequest(BaseModel):
    chain_id: str
    contract_address: str
    name: str
    uri: str
    hash: str

@router.get("/tokens")
def get_tokens():
    contracts = load_db().get("contracts", [])
    updated = False
    
    for c in contracts:
        if c.get("status") in ["Submitted", "Pending"] and c.get("tx_id"):
            try:
                # Check Cobo Status
                print(f"Checking status for {c['name']} (Tx: {c['tx_id']})")
                tx = cobo_client.get_transaction(c["tx_id"])
                if tx:
                    print(f"Got Cobo status: {tx.status} (str: {str(tx.status)})")
                    # Map Cobo status to our status
                    # Cobo statuses: Submitted, Pending, Success, Failed
                    
                    # Update status
                    if hasattr(tx, 'transaction_hash') and tx.transaction_hash:
                        c["tx_hash"] = tx.transaction_hash
                    
                    status_str = str(tx.status)
                    if status_str == "TransactionStatus.COMPLETED" or status_str == "Completed" or status_str == "TransactionStatus.SUCCESS" or status_str == "Success":
                        print("Marking as Deployed")
                        c["status"] = "Deployed"
                        # Try to get contract address from chain if missing
                        if not c.get("contract_address") and c.get("tx_hash"):
                            try:
                                w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/")) # Hardcoded BSC for MVP
                                receipt = w3.eth.get_transaction_receipt(c["tx_hash"])
                                if receipt and receipt.contractAddress:
                                    c["contract_address"] = receipt.contractAddress
                            except Exception as e:
                                print(f"Failed to get receipt: {e}")
                    elif status_str == "TransactionStatus.FAILED" or status_str == "Failed":
                        c["status"] = "Failed"
                    elif status_str in ["TransactionStatus.BROADCASTING", "Broadcasting", "TransactionStatus.PENDING", "Pending"]:
                         # Check if dropped/replaced
                         if c.get("tx_hash"):
                             try:
                                 w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
                                 w3.eth.get_transaction(c["tx_hash"])
                             except Exception:
                                 # Transaction not found on chain, likely dropped/replaced
                                 print(f"Transaction {c['tx_hash']} not found on chain. Marking as Failed.")
                                 c["status"] = "Failed"
                    
                    updated = True
            except Exception as e:
                print(f"Failed to update status for {c['name']}: {e}")
    
    if updated:
        # Save back to DB (Need to expose save_db or just rely on memory for this session? No, must save)
        # We need to import save_db from database
        save_db({"contracts": contracts})
        
    return contracts

@router.post("/tokens/deploy")
def deploy_token(request: DeployRequest):
    try:
        result = deploy_erc1400(
            chain_id=request.chain_id,
            name=request.name,
            symbol=request.symbol,
            partitions=request.partitions,
            supply=request.supply
        )
        
        # Save to DB
        contract_info = {
            "type": "MANAGED",
            "chain_id": request.chain_id,
            "name": request.name,
            "symbol": request.symbol,
            "partitions": request.partitions,
            "wallet_id": result["wallet_id"],
            "owner": result["owner"],
            "tx_id": result["tx_id"],
            "status": "Pending"
        }
        add_contract(contract_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokens/mint")
def mint_token(request: MintRequest):
    try:
        result = mint_by_partition(
            chain_id=request.chain_id,
            contract_address=request.contract_address,
            partition=request.partition,
            to_address=request.to_address,
            amount=request.amount
        )
        
        # Track in DB
        add_mint_event({
            "chain_id": request.chain_id,
            "contract_address": request.contract_address,
            "partition": request.partition,
            "to_address": request.to_address,
            "amount": request.amount,
            "tx_id": result.get("tx_id"),
            "timestamp": int(time.time())
        })
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Minting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{chain_id}/{address}/holders")
def get_token_holders(chain_id: str, address: str):
    events = get_mint_events(chain_id, address)
    
    # Aggregate balances
    holders = {}
    for e in events:
        recipient = e["to_address"]
        partition = e["partition"]
        amount = e["amount"]
        
        key = f"{recipient}_{partition}"
        if key not in holders:
            holders[key] = {
                "address": recipient,
                "partition": partition,
                "balance": 0
            }
        holders[key]["balance"] += amount
        
    return list(holders.values())

@router.post("/tokens/document")
def upload_document(request: DocumentRequest):
    try:
        return set_document(
            chain_id=request.chain_id,
            contract_address=request.contract_address,
            name=request.name,
            uri=request.uri,
            doc_hash=request.hash
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ByowSyncRequest(BaseModel):
    chain_id: str
    address: str
    name: str
    symbol: str
    owner: str
    tx_hash: Optional[str] = None

@router.post("/sync/byow")
def sync_byow(request: ByowSyncRequest):
    contract_info = {
        "type": "BYOW",
        "chain_id": request.chain_id,
        "contract_address": request.address, # Use consistent naming
        "name": request.name,
        "symbol": request.symbol,
        "owner": request.owner,
        "tx_hash": request.tx_hash,
        "status": "Deployed",
        "partitions": ["Class A"] # Default for BYOW MVP
    }
    add_contract(contract_info)
    return {"status": "Synced"}
@router.get("/artifacts")
def get_artifacts_endpoint():
    return get_artifact()
