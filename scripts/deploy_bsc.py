import sys
import os
import json
import time
from solcx import compile_standard, install_solc
from web3 import Web3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cobo_service import cobo_client
from src.config.settings import settings
from cobo_waas2.models import (
    ContractCallParams,
    ContractCallSource,
    CustodialWeb3ContractCallSource,
    ContractCallSourceType,
    ContractCallDestination,
    ContractCallDestinationType,
    EvmContractCallDestination
)

# Configuration
CHAIN_ID = "BSC_BNB"
GAS_LIMIT = 3000000
PARTITION_CLASS_A = "0x436c617373410000000000000000000000000000000000000000000000000000"

def compile_contract():
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
    
    return compiled_sol

def get_contract_data(compiled_sol):
    contract = compiled_sol['contracts']['SimpleERC1400.sol']['SimpleERC1400']
    return contract['abi'], contract['evm']['bytecode']['object']

def find_funded_wallet():
    print(f"Searching for funded {CHAIN_ID} wallets...")
    # List wallets. Note: list_wallets returns WalletInfo. 
    # We need to check balances. This might be slow if we check many.
    # For efficiency, we'll list wallets and then check balance for the first few.
    
    wallets = cobo_client.list_web3_wallets()
    
    for w in wallets:
        wallet_id = w['id']
        address = cobo_client.get_wallet_address(wallet_id, chain_id=CHAIN_ID)
        
        if not address:
            continue
            
        # Check balance (using Cobo API or Web3 if we had a provider, but Cobo API is safer)
        # Cobo SDK has list_token_balances
        try:
            balances = cobo_client.wallets_api.list_token_balances(
                wallet_id=wallet_id,
                chain_ids=CHAIN_ID,
                token_ids=f"{CHAIN_ID}_BNB" # Assuming standard token ID format
            )
            
            if balances.data:
                balance = float(balances.data[0].balance)
                if balance > 0:
                    print(f"✅ Found funded wallet: {w['name']} ({address}) - Balance: {balance} BNB")
                    return wallet_id, address
        except Exception as e:
            # print(f"Error checking balance for {wallet_id}: {e}")
            pass
            
    print(f"❌ No funded {CHAIN_ID} wallet found. Please send 0.01 BNB to one of your wallets.")
    sys.exit(1)

def deploy(wallet_id=None, wallet_address=None):
    if not wallet_id or not wallet_address:
        wallet_id, wallet_address = find_funded_wallet()
    
    # Ensure checksum address
    wallet_address = Web3.to_checksum_address(wallet_address)
    
    print(f"Using Wallet: {wallet_id}")
    print(f"Address: {wallet_address}")
    
    compiled_sol = compile_contract()
    abi, bytecode = get_contract_data(compiled_sol)
    
    # Encode Constructor Args
    w3 = Web3()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Constructor(name, symbol, partitions, owner)
    constructor_args = contract.constructor(
        "Cobo Security Token",
        "CST",
        [PARTITION_CLASS_A],
        wallet_address # Owner is the deployer
    ).data_in_transaction
    
    print("🚀 Deploying to BNB Chain...")
    
    try:
        source = ContractCallSource(
            discriminator='CustodialWeb3ContractCallSource',
            actual_instance=CustodialWeb3ContractCallSource(
                source_type=ContractCallSourceType.WEB3,
                wallet_id=wallet_id,
                address=wallet_address
            )
        )
        
        destination = ContractCallDestination(
            discriminator='EvmContractCallDestination',
            actual_instance=EvmContractCallDestination(
                destination_type=ContractCallDestinationType.EVM_CONTRACT,
                address="0x0000000000000000000000000000000000000000", 
                value="0",
                calldata=constructor_args
            )
        )
        
        params = ContractCallParams(
            request_id=f"deploy_bsc_{int(time.time())}",
            chain_id=CHAIN_ID,
            source=source,
            destination=destination,
            description="Deploy SimpleERC1400",
            gas_limit=GAS_LIMIT
        )
        
        transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
        print(f"Transaction Submitted! ID: {transaction.transaction_id}")
        
        # Poll for completion to get address
        print("Waiting for confirmation...")
        for _ in range(30):
            time.sleep(2)
            tx_info = cobo_client.transactions_api.get_transaction_by_id(transaction.transaction_id)
            if tx_info.status == 'Success' or (tx_info.timeline and tx_info.timeline[-1].status == 'Success'): # Adjust based on actual status enum
                 # Cobo API might not return contract address directly in basic info.
                 # We might need to look at 'confirmed' status and get hash.
                 # For now, we'll save the Tx Hash.
                 if tx_info.transaction_hash:
                     print(f"✅ Success! View on BscScan: https://bscscan.com/tx/{tx_info.transaction_hash}")
                     
                     # Save deployment info
                     deployment_info = {
                         "chain": CHAIN_ID,
                         "wallet_id": wallet_id,
                         "owner": wallet_address,
                         "tx_id": transaction.transaction_id,
                         "tx_hash": tx_info.transaction_hash,
                         "abi": abi
                     }
                     
                     with open('bsc_deployment.json', 'w') as f:
                         json.dump(deployment_info, f, indent=2)
                         
                     return
            elif tx_info.status == 'Failed':
                print(f"❌ Transaction Failed: {tx_info.failed_reason}")
                return
                
        print("Transaction still pending. Check Cobo Dashboard.")

    except Exception as e:
        print(f"Deployment failed: {e}")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Deploy SimpleERC1400 to BSC')
    parser.add_argument('--wallet-id', type=str, help='Cobo Wallet ID')
    parser.add_argument('--wallet-address', type=str, help='Wallet Address')
    args = parser.parse_args()
    
    deploy(args.wallet_id, args.wallet_address)
