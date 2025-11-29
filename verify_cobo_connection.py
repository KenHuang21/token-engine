import os
from dotenv import load_dotenv

# Force reload env before importing services that use settings
load_dotenv(override=True)

print(f"DEBUG: COBO_API_URL={os.getenv('COBO_API_URL')}")
print(f"DEBUG: COBO_API_PUBLIC_KEY={os.getenv('COBO_API_PUBLIC_KEY')}")
# Don't print full private key for security, just length
pk = os.getenv('COBO_API_PRIVATE_KEY')
print(f"DEBUG: COBO_API_PRIVATE_KEY length={len(pk) if pk else 0}")

from backend.services.cobo_service import cobo_client

def verify():
    print("Verifying Cobo Connection...")
    # Re-initialize to pick up new env vars if they weren't loaded
    cobo_client._initialize_client()
    
    if cobo_client.check_connection():
        print("✅ Connection Successful!")
        # Try to list wallets to be sure
        try:
            wallets = cobo_client.get_wallets(limit=1)
            print(f"✅ Listed {len(wallets)} wallets.")
        except Exception as e:
            print(f"⚠️ Connection okay but list_wallets failed: {e}")
    else:
        print("❌ Connection Failed.")

if __name__ == "__main__":
    verify()
