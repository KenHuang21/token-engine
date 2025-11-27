import json
from web3 import Web3

TX_HASH = "0x02eac326157af5b5be35156142668ffd88b1dfa40f1237ff5a078162c11123a6"
BSC_RPC = "https://bsc-dataseed.binance.org/"

def get_address():
    print(f"Connecting to BSC RPC: {BSC_RPC}")
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC RPC")
        return

    print(f"Fetching receipt for {TX_HASH}...")
    try:
        receipt = w3.eth.get_transaction_receipt(TX_HASH)
        contract_address = receipt['contractAddress']
        print(f"✅ Contract Address Found: {contract_address}")
        
        # Update JSON
        try:
            with open('bsc_deployment.json', 'r') as f:
                info = json.load(f)
            
            info['contract_address'] = contract_address
            
            with open('bsc_deployment.json', 'w') as f:
                json.dump(info, f, indent=2)
            print("Updated bsc_deployment.json")
            
        except FileNotFoundError:
            print("bsc_deployment.json not found, printing address only.")

    except Exception as e:
        print(f"Error fetching receipt: {e}")

if __name__ == "__main__":
    get_address()
