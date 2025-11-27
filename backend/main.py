import uvicorn
import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
DB_FILE = "db_contracts.json"

def get_contracts():
    """Safe read of the DB file."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_contract(contract_data):
    """Safe write to the DB file."""
    contracts = get_contracts()
    contracts.append(contract_data)
    with open(DB_FILE, "w") as f:
        json.dump(contracts, f, indent=2)

# --- 4. Pydantic Models ---
class DeployRequest(BaseModel):
    chain: str = "BSC"
    name: str
    symbol: str
    partitions: List[str]
    initial_supply: int

class MintRequest(BaseModel):
    chain: str
    contract_address: str
    partition: str
    receiver: str
    amount: float

class DocumentRequest(BaseModel):
    chain: str
    contract_address: str
    doc_name: str
    doc_uri: str
    doc_hash: str

# --- 5. API Endpoints (ALIGNED WITH FRONTEND) ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is Live"}

# FIX: Renamed from /contracts to /tokens to match Frontend
@app.get("/tokens")
def list_tokens():
    return get_contracts()

# FIX: Renamed from /deploy to /tokens/deploy to match Frontend
@app.post("/tokens/deploy")
def deploy_token(req: DeployRequest):
    print(f"🚀 Deploying {req.name}...")
    
    # Mocking successful deployment for MVP
    fake_address = f"0x{os.urandom(20).hex()}"
    fake_tx = f"0x{os.urandom(32).hex()}"
    
    new_contract = {
        "name": req.name,
        "symbol": req.symbol,
        "chain": req.chain,
        "address": fake_address,
        "type": "MANAGED",
        "status": "Active",
        "partitions": req.partitions
    }
    save_contract(new_contract)
    return {"status": "success", "address": fake_address, "tx_hash": fake_tx}

# FIX: Renamed from /mint to /tokens/mint to match Frontend
@app.post("/tokens/mint")
def mint_tokens(req: MintRequest):
    return {"status": "success", "tx_hash": "0xMockMintHash"}

# FIX: Renamed from /set-document to /tokens/document to match Frontend
@app.post("/tokens/document")
def set_document(req: DocumentRequest):
    return {"status": "success", "tx_hash": "0xMockDocHash"}

# --- 6. Local Development Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)