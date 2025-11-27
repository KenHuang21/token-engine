import json
import os
import sys
from solcx import compile_standard, install_solc

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def compile_and_export():
    print("Compiling SimpleERC1400.sol...")
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
    
    artifact = {
        "abi": contract['abi'],
        "bytecode": contract['evm']['bytecode']['object']
    }
    
    output_path = 'backend/artifacts/SimpleERC1400.json'
    with open(output_path, 'w') as f:
        json.dump(artifact, f, indent=2)
        
    print(f"✅ Exported artifact to {output_path}")

if __name__ == "__main__":
    compile_and_export()
