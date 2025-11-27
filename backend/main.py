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
# This allows your Vercel Frontend to talk to this Render Backend
origins = [
    "http://localhost:5173",             # Local Vite
    "http://127.0.0.1:5173",             # Local Vite (Alternative)
    "https://token-engine.vercel.app",   # Your Production Vercel App
    "https://token-engine-git-main-kenhuang21s-projects.vercel.app" # Vercel Preview URLs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Temporarily allow all for MVP debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Database Mock (File Persistence) ---
# In production, replace this with PostgreSQL
DB_FILE = "db_contracts.json"

def get_contracts():
    """Reads the list of deployed tokens from the JSON file."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_contract(contract_data):
    """Appends a new token to the JSON file."""
    contracts = get_contracts()
    contracts.append(contract_data)
    with open(DB_FILE, "w") as f:
        json.dump(contracts, f, indent=2)

# --- 4. Pydantic Models (Input Validation) ---
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

# --- 5. API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Tokenization Engine API is Live 🚀"}

@app.get("/contracts")
def list_contracts():
    """Returns the list of all deployed tokens for the Dashboard."""
    return get_contracts()

@app.post("/deploy")
def deploy_token(req: DeployRequest):
    """
    Simulates deployment for the MVP. 
    In the next step, we will uncomment the real Cobo logic here.
    """
    print(f"🚀 Deploying {req.name} ({req.symbol}) on {req.chain}...")
    
    # --- TODO: Insert Real Cobo Deployment Logic Here ---
    # tx_hash = cobo_service.deploy(...)
    
    # Mock Response
    fake_address = f"0x{os.urandom(20).hex()}"
    fake_tx = f"0x{os.urandom(32).hex()}"
    
    new_contract = {
        "name": req.name,
        "symbol": req.symbol,
        "chain": req.chain,
        "address": fake_address,
        "type": "MANAGED", # vs BYOW
        "status": "Active",
        "partitions": req.partitions
    }
    
    # Save to DB so it shows up in the UI
    save_contract(new_contract)
    
    return {
        "status": "success",
        "address": fake_address,
        "tx_hash": fake_tx
    }

@app.post("/mint")
def mint_tokens(req: MintRequest):
    print(f"💰 Minting {req.amount} tokens to {req.receiver} (Partition: {req.partition})")
    return {"status": "success", "tx_hash": "0xMockMintHash123"}

@app.post("/set-document")
def set_document(req: DocumentRequest):
    print(f"📄 Attaching Document: {req.doc_name} (Hash: {req.doc_hash})")
    return {"status": "success", "tx_hash": "0xMockDocHash123"}

# --- 6. Local Development Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
