import sys
import os
import cobo_waas2
from cobo_waas2.api import wallets_api
from cobo_waas2.crypto.local_ed25519_signer import LocalEd25519Signer

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings

def test_sandbox():
    print("Testing Cobo Sandbox Connection...")
    
    sandbox_url = "https://api.sandbox.cobo.com/v2"
    
    signer = LocalEd25519Signer(settings.cobo_api_private_key)
    configuration = cobo_waas2.Configuration(
        host=sandbox_url,
        signer=signer
    )
    api_client = cobo_waas2.ApiClient(configuration)
    api_instance = wallets_api.WalletsApi(api_client)
    
    try:
        # Try to fetch wallets
        api_instance.list_wallets(limit=1)
        print("SUCCESS: Connected to Cobo Sandbox!")
    except Exception as e:
        print(f"Sandbox connection failed: {e}")

if __name__ == "__main__":
    test_sandbox()
