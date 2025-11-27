import sys
import os
from tabulate import tabulate

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cobo_service import cobo_client
from cobo_waas2.models import WalletType, WalletSubtype

WALLET_ID = "e4288c49-bbf3-47f6-97e5-1bcf0060e53e"

def check_chains():
    print("--- Checking Globally Enabled Chains for Custodial Web3 Wallets ---")
    try:
        chains = cobo_client.wallets_api.list_enabled_chains(
            wallet_type=WalletType.CUSTODIAL,
            wallet_subtype=WalletSubtype.WEB3,
            limit=50
        )
        
        chain_data = []
        for c in chains.data:
            chain_data.append([c.chain_id, c.display_name])
            
        print(tabulate(chain_data, headers=["Chain ID", "Display Name"], tablefmt="grid"))
        
        # Check if BSC is in the list
        bsc_enabled = any(c.chain_id == 'BSC' for c in chains.data)
        print(f"\nIs BSC enabled globally for this wallet type? {'✅ YES' if bsc_enabled else '❌ NO'}")
        
    except Exception as e:
        print(f"Error listing enabled chains: {e}")

    print(f"\n--- Checking Enabled Chains for Wallet {WALLET_ID} ---")
    try:
        # We infer enabled chains by listing addresses
        addresses = cobo_client.wallets_api.list_addresses(
            wallet_id=WALLET_ID,
            limit=50
        )
        
        addr_data = []
        for a in addresses.data:
            addr_data.append([a.chain_id, a.address])
            
        if not addr_data:
            print("No addresses found (Wallet might be empty or new).")
        else:
            print(tabulate(addr_data, headers=["Chain ID", "Address"], tablefmt="grid"))
            
        # Check if BSC is in the list
        wallet_has_bsc = any(a.chain_id == 'BSC' for a in addresses.data)
        print(f"\nDoes this wallet have a BSC address? {'✅ YES' if wallet_has_bsc else '❌ NO'}")

    except Exception as e:
        print(f"Error listing addresses: {e}")

if __name__ == "__main__":
    check_chains()
