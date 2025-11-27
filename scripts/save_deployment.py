import json
import sys
import os
from solcx import compile_standard, install_solc

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

CHAIN_ID = "BSC_BNB"
WALLET_ID = "e4288c49-bbf3-47f6-97e5-1bcf0060e53e"
OWNER = "0xD4402D1e46f1B13b3D1E683b2604C93dD91075B9"
TX_ID = "492076fc-d60d-4eab-8edb-d675f4d6bab9"
TX_HASH = "0x02eac326157af5b5be35156142668ffd88b1dfa40f1237ff5a078162c11123a6"

def save_deployment():
    print("Compiling SimpleERC1400.sol to get ABI...")
    install_solc('0.8.20')
    
    with open('contracts/SimpleERC1400.sol', 'r') as f:
        source = f.read()

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            "SimpleERC1400.sol": {"content": source}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    }, solc_version='0.8.20')
    
    contract = compiled_sol['contracts']['SimpleERC1400.sol']['SimpleERC1400']
    abi = contract['abi']
    
    info = {
        "chain": CHAIN_ID,
        "wallet_id": WALLET_ID,
        "owner": OWNER,
        "tx_id": TX_ID,
        "tx_hash": TX_HASH,
        "abi": abi
    }
    
    with open('bsc_deployment.json', 'w') as f:
        json.dump(info, f, indent=2)
        
    print("✅ Saved deployment info to bsc_deployment.json")

if __name__ == "__main__":
    save_deployment()
