import os
from dotenv import load_dotenv
load_dotenv(override=True)

from backend.services.cobo_service import cobo_client

def find_polygon_token():
    print("Searching for Polygon/MATIC Token ID...")
    cobo_client._initialize_client()
    
    try:
        # Fetch a batch of tokens
        tokens = cobo_client.wallets_api.list_supported_tokens(limit=50).data
        
        # We might need to fetch more if not in first 50, but let's check first batch and structure
        print(f"Fetched {len(tokens)} tokens.")
        
        found = False
        for t in tokens:
            # Check for MATIC or Polygon in symbol or name
            if "MATIC" in t.symbol.upper() or "POLYGON" in t.name.upper():
                print(f"Found: Symbol={t.symbol}, ID={t.token_id}, ChainID={t.chain_id}, Name={t.name}")
                found = True
                
        if not found:
            print("Not found in first 50. Trying specific query if possible (SDK doesn't support search).")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    find_polygon_token()
