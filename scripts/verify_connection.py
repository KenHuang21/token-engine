import sys
import os

# Add the project root to the python path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cobo_service import cobo_client
from src.config.settings import settings
from cobo_waas2.models.wallet_type import WalletType

def verify_connection():
    print("="*60)
    print("Cobo WaaS 2.0 Connection Verification")
    print("="*60)
    
    print(f"Environment: {settings.cobo_api_url}")
    print(f"Public Key:  {settings.cobo_api_public_key[:10]}...{settings.cobo_api_public_key[-10:]}")
    print("-" * 60)

    try:
        # Initialize client (uses settings automatically)
        cobo_client._initialize_client()
        
        wallets = cobo_client.get_wallets(limit=5)
        print(f"✅ SUCCESS: Connected! Found {len(wallets)} wallets.")
        for wallet in wallets:
            print(f" - {wallet}")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_connection()
