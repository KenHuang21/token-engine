import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from cobo_waas2.crypto.local_ed25519_signer import LocalEd25519Signer

def debug_signer():
    print("Debugging LocalEd25519Signer...")
    try:
        signer = LocalEd25519Signer(settings.cobo_api_private_key)
        # Check if get_public_key exists, otherwise try to inspect internals
        if hasattr(signer, 'get_public_key'):
            pub_key = signer.get_public_key()
            print(f"Signer Derived Public Key: {pub_key}")
        else:
            print("Signer does not have get_public_key method.")
            print(f"Dir: {dir(signer)}")
            
        print(f"Env Public Key:            {settings.cobo_api_public_key}")
        
    except Exception as e:
        print(f"Error initializing signer: {e}")

if __name__ == "__main__":
    debug_signer()
