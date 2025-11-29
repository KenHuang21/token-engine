import uvicorn
import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3
from backend.services.cobo_service import cobo_client
from backend.config.settings import settings

print(f"DEBUG: Cobo URL from settings: {settings.cobo_api_url}")
print(f"DEBUG: Cobo Key present: {bool(settings.cobo_api_private_key)}")
# --- 1. App Initialization ---
app = FastAPI(title="White-Label Tokenization Platform")

# --- 2. CORS Configuration (CRITICAL) ---
# This whitelist MUST include your Vercel URL exactly as it appears in the browser bar
origins = [
    "http://localhost:5173",             # Local Vite
    "http://127.0.0.1:5173",             # Local Vite (Alternative)
    "https://token-engine.vercel.app",   # Production Vercel App
    # Add any specific preview URLs if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Database Mock (File Persistence) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "db.json")

def get_contracts():
    """Safe read of the DB file."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            # Handle both list (legacy) and dict (new) formats
            if isinstance(data, list):
                return data
            return data.get("contracts", [])
    except Exception:
        return []

def resolve_contract_address(tx_hash: str, chain_id: str = "BSC_BNB") -> Optional[str]:
    """Fetches the contract address from the transaction receipt."""
    try:
        # Determine RPC URL based on chain_id
        rpc_url = "https://bsc-dataseed.binance.org/" # Default to BSC
        if chain_id == "ETH_SEPOLIA":
             rpc_url = "https://rpc.sepolia.org"
        elif chain_id == "MATIC_POLYGON":
             rpc_url = "https://polygon-rpc.com"
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return receipt.get("contractAddress")
    except Exception as e:
        print(f"Error fetching receipt for {tx_hash}: {e}")
        return None

def get_mints():
    """Safe read of mints from DB file."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return []
            return data.get("mints", [])
    except Exception:
        return []

def save_contract(contract_data):
    """Safe write to the DB file."""
    if not os.path.exists(DB_FILE):
        data = {"contracts": [], "mints": []}
    else:
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    data = {"contracts": data, "mints": []}
        except Exception:
            data = {"contracts": [], "mints": []}
    
    data["contracts"].append(contract_data)
    
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- 4. Pydantic Models ---
class DeployRequest(BaseModel):
    chain_id: str = "BSC"
    name: str
    symbol: str
    partitions: List[str]
    supply: int

class MintRequest(BaseModel):
    chain_id: str
    contract_address: str
    partition: str
    to_address: str
    amount: float

class DocumentRequest(BaseModel):
    chain_id: str
    contract_address: str
    name: str
    uri: str
    contract_address: str
    name: str
    uri: str
    hash: str

class RegisterTokenRequest(BaseModel):
    chain_id: str
    name: str
    symbol: str
    contract_address: str
    tx_hash: str
    partitions: List[str]
    owner: str
    type: str = "SELF_CUSTODY"

class RegisterMintRequest(BaseModel):
    chain_id: str
    contract_address: str
    partition: str
    to_address: str
    amount: float
    tx_hash: str

# --- 5. API Endpoints (ALIGNED WITH FRONTEND) ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is Live"}

# FIX: Renamed from /contracts to /tokens to match Frontend
@app.get("/tokens")
def list_tokens():
    contracts = get_contracts()
    
    # Check for pending contracts and resolve address
    updated = False
    for c in contracts:
        if c.get("status") == "Pending" and c.get("cobo_id"):
            try:
                print(f"Checking status for pending contract {c['name']} (Cobo ID: {c['cobo_id']})...")
                tx_details = cobo_client.get_transaction(c['cobo_id'])
                
                if tx_details and str(tx_details.status) == "TransactionStatus.SUCCESS":
                    # Transaction confirmed by Cobo. Now get on-chain address.
                    chain_tx_hash = tx_details.transaction_hash
                    print(f"Cobo TX Success. Chain Hash: {chain_tx_hash}")
                    
                    c["status"] = "Deployed"
                    c["tx_hash"] = chain_tx_hash
                    c["status"] = "Deployed"
                    c["tx_hash"] = chain_tx_hash
                    
                    # Resolve Contract Address
                    real_address = resolve_contract_address(chain_tx_hash, c.get("chain_id", "BSC_BNB"))
                    if real_address:
                        c["contract_address"] = real_address
                        print(f"✅ Resolved Contract Address: {real_address}")
                    else:
                        print("⚠️ Could not resolve contract address from receipt yet.")
                        # Keep status as Pending if we really need the address, or mark Deployed but with missing address?
                        # For now, let's keep it Deployed but address might be wrong if not found.
                        # Actually, if we can't get the address, maybe we shouldn't mark it Deployed?
                        # But the TX is success.
                        pass
                        
                    updated = True
                elif tx_details and str(tx_details.status) == "TransactionStatus.FAILED":
                     c["status"] = "Failed"
                     updated = True
            except Exception as e:
                print(f"Failed to resolve contract: {e}")

    if updated:
        # Save back to DB
        # We need to load fresh, update, save.
        # But here we modified 'contracts' list which is from get_contracts()
        # We need to save the whole structure.
        # get_contracts returns list, we need to wrap in dict
        data = {"contracts": contracts, "mints": get_mints()} # get_mints is not efficient here, better load raw
        # Re-implement save logic safely
        with open(DB_FILE, "r") as f:
            full_data = json.load(f)
        full_data["contracts"] = contracts
        with open(DB_FILE, "w") as f:
            json.dump(full_data, f, indent=2)

    return contracts

# FIX: Renamed from /deploy to /tokens/deploy to match Frontend
# FIX: Renamed from /deploy to /tokens/deploy to match Frontend
@app.post("/tokens/deploy")
def deploy_token(req: DeployRequest):
    print(f"🚀 Deploying {req.name}...")
    
    # Mocking successful deployment for MVP
    fake_address = f"0x{os.urandom(20).hex()}"
    fake_tx = f"0x{os.urandom(32).hex()}"
    
    # If MANAGED, try to deploy via Cobo
    if True: # We want to try Cobo for all deployments in this context, or check a flag
        try:
            # Load ABI/Bytecode
            abi_path = os.path.join(BASE_DIR, "artifacts", "SimpleERC1400.json")
            with open(abi_path, "r") as f:
                artifact = json.load(f)
            
            w3 = Web3()
            contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
            
            # Constructor args: name, symbol, partitions, owner
            # partitions needs to be bytes32[]
            partitions_bytes = [w3.to_bytes(text=p).ljust(32, b'\0') for p in req.partitions]
            
            # Use the Cobo wallet address as owner so it can mint tokens
            target_wallet_id = settings.cobo_default_wallet_id
            owner_address = cobo_client.get_wallet_address(target_wallet_id, req.chain_id if req.chain_id != "MATIC_POLYGON" else "MATIC")
            
            # Build constructor transaction to get data
            tx = contract.constructor(
                req.name,
                req.symbol,
                partitions_bytes,
                w3.to_checksum_address(owner_address)
            ).build_transaction({
                'from': '0x0000000000000000000000000000000000000000',
                'gas': 0,
                'gasPrice': 0,
                'chainId': 1,
                'nonce': 0
            })
            bytecode_with_args = tx['data']
            
            # Get a wallet ID (using the first available one for now, or hardcoded)
            # Ideally we pick one from the user's available wallets.
            # For MVP, let's find a funded wallet or use a default.
            
            # Get default wallet from settings
            target_wallet_id = settings.cobo_default_wallet_id
            
            print(f"🚀 Sending Deployment TX to Cobo using wallet {target_wallet_id}...")
            cobo_tx_id = cobo_client.deploy_contract(
                chain_id=req.chain_id,
                wallet_id=target_wallet_id,
                bytecode=bytecode_with_args
            )
            print(f"✅ Cobo Deployment TX ID: {cobo_tx_id}")
            fake_tx = "" # Will be updated later
            cobo_id = cobo_tx_id
            fake_address = "Pending" 
            status = "Pending"
                
        except Exception as e:
            print(f"⚠️ Cobo deployment failed: {e}")
            # Return structured error instead of generic 500
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={
                    "detail": f"Deployment failed: {str(e)}",
                    "error_type": type(e).__name__,
                    "chain_id": req.chain_id
                }
            )

    new_contract = {
        "name": req.name,
        "symbol": req.symbol,
        "chain_id": req.chain_id,
        "contract_address": fake_address,
        "type": "MANAGED",
        "status": status,
        "partitions": req.partitions,
        "owner": "0xD4402D1e46f1B13b3D1E683b2604C93dD91075B9", # Mock owner
        "tx_hash": fake_tx,
        "cobo_id": cobo_id
    }
    save_contract(new_contract)
    return {"status": "success", "address": fake_address, "tx_id": fake_tx}

@app.post("/tokens/register")
def register_token(req: RegisterTokenRequest):
    """Registers a self-custody token in the database."""
    new_contract = {
        "name": req.name,
        "symbol": req.symbol,
        "chain_id": req.chain_id,
        "contract_address": req.contract_address,
        "type": req.type,
        "status": "Deployed",
        "partitions": req.partitions,
        "owner": req.owner,
        "tx_hash": req.tx_hash,
        "cobo_id": None
    }
    save_contract(new_contract)
    return {"status": "success"}

@app.post("/tokens/mint/register")
def register_mint(req: RegisterMintRequest):
    """Registers a self-custody mint in the database."""
    new_mint = {
        "chain_id": req.chain_id,
        "contract_address": req.contract_address,
        "partition": req.partition,
        "to_address": req.to_address,
        "amount": req.amount,
        "tx_id": req.tx_hash,
        "timestamp": 1732720000 # Mock timestamp
    }
    
    # Save mint to DB
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    data = {"contracts": data, "mints": []}
        except Exception:
            data = {"contracts": [], "mints": []}
    else:
        data = {"contracts": [], "mints": []}
        
    if "mints" not in data:
        data["mints"] = []
        
    data["mints"].append(new_mint)
    
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "success"}

# FIX: Renamed from /mint to /tokens/mint to match Frontend
# FIX: Renamed from /mint to /tokens/mint to match Frontend
@app.post("/tokens/mint")
def mint_tokens(req: MintRequest):
    tx_id = f"mock_mint_{os.urandom(4).hex()}"
    
    # 1. Find contract to check type and get wallet_id
    contracts = get_contracts()
    contract = next((c for c in contracts if c["contract_address"].lower() == req.contract_address.lower()), None)
    
    if contract and contract.get("type") == "MANAGED":
        try:
            # Load ABI
            abi_path = os.path.join(BASE_DIR, "artifacts", "SimpleERC1400.json")
            with open(abi_path, "r") as f:
                artifact = json.load(f)
            
            w3 = Web3()
            contract_instance = w3.eth.contract(abi=artifact["abi"])
            
            # Encode Calldata: issueByPartition(bytes32 partition, address tokenHolder, uint256 value, bytes data)
            # Partition needs to be bytes32
            partition_bytes = w3.to_bytes(text=req.partition).ljust(32, b'\0')
            
            tx = contract_instance.functions.issueByPartition(
                partition_bytes,
                w3.to_checksum_address(req.to_address),
                int(req.amount * 10**18), # Assuming 18 decimals
                b'' # data
            ).build_transaction({
                'to': w3.to_checksum_address(req.contract_address), # Required since contract instance has no address
                'from': '0x0000000000000000000000000000000000000000', # Dummy sender for encoding
                'gas': 0,
                'gasPrice': 0,
                'chainId': 1, # Dummy chainId to prevent Web3 from querying provider
                'nonce': 0    # Dummy nonce
            })
            calldata = tx['data']
            
            # Call Cobo
            print(f"🚀 Sending Mint TX to Cobo for {req.contract_address}...")
            cobo_tx_id = cobo_client.create_contract_call(
                chain_id=req.chain_id,
                wallet_id=contract.get("wallet_id", settings.cobo_default_wallet_id), # Use default wallet
                to_address=req.contract_address,
                calldata=calldata,
                amount=0
            )
            tx_id = cobo_tx_id
            print(f"✅ Cobo TX ID: {tx_id}")
            
        except Exception as e:
            print(f"❌ Cobo Mint Failed: {e}")
            # Return structured error instead of silent fallback
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={
                    "detail": f"Mint failed: {str(e)}",
                    "error_type": type(e).__name__,
                    "chain_id": req.chain_id,
                    "contract_address": req.contract_address
                }
            )

    new_mint = {
        "chain_id": req.chain_id,
        "contract_address": req.contract_address,
        "partition": req.partition,
        "to_address": req.to_address,
        "amount": req.amount,
        "tx_id": tx_id,
        "timestamp": 1732720000 # Mock timestamp
    }
    
    # Save mint to DB
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    data = {"contracts": data, "mints": []}
        except Exception:
            data = {"contracts": [], "mints": []}
    else:
        data = {"contracts": [], "mints": []}
        
    if "mints" not in data:
        data["mints"] = []
        
    data["mints"].append(new_mint)
    
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "success", "tx_hash": tx_id}

# FIX: Renamed from /set-document to /tokens/document to match Frontend
@app.post("/tokens/document")
def set_document(req: DocumentRequest):
    return {"status": "success", "tx_hash": "0xMockDocHash"}

@app.get("/tokens/{chain_id}/{address}/holders")
def get_token_holders(chain_id: str, address: str):
    mints = get_mints()
    
    # Filter mints for this token
    token_mints = [
        m for m in mints 
        if m.get("chain_id") == chain_id and m.get("contract_address").lower() == address.lower()
    ]
    
    # Aggregate balances
    balances = {}
    for mint in token_mints:
        key = (mint["to_address"], mint["partition"])
        if key not in balances:
            balances[key] = 0
        balances[key] += mint["amount"]
        
    # Format response
    holders = []
    for (wallet, partition), balance in balances.items():
        if balance > 0:
            holders.append({
                "address": wallet,
                "partition": partition,
                "balance": balance
            })
            
            
    return holders

@app.get("/artifacts")
def get_artifacts():
    """Returns the ABI and Bytecode for the token contract."""
    abi_path = os.path.join(BASE_DIR, "artifacts", "SimpleERC1400.json")
    if not os.path.exists(abi_path):
        raise HTTPException(status_code=404, detail="Artifacts not found")
        
    with open(abi_path, "r") as f:
        return json.load(f)

# --- 6. Local Development Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)