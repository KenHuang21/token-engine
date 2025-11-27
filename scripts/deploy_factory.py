import sys
import os
import argparse
import time
from tabulate import tabulate
from solcx import compile_standard, install_solc

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

def compile_contracts():
    print("Compiling contracts...")
    install_solc('0.8.0')
    
    with open('contracts/StandardToken.sol', 'r') as f:
        standard_token_source = f.read()
    with open('contracts/TokenFactory.sol', 'r') as f:
        token_factory_source = f.read()

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            "StandardToken.sol": {"content": standard_token_source},
            "TokenFactory.sol": {"content": token_factory_source}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    }, solc_version='0.8.0')
    
    return compiled_sol

def get_bytecode(compiled_sol, contract_name):
    return compiled_sol['contracts'][f'{contract_name}.sol'][contract_name]['evm']['bytecode']['object']

def select_wallet():
    print("\nFetching Web3 Wallets...")
    wallets = cobo_client.list_web3_wallets()
    
    if not wallets:
        print("No Web3 wallets found.")
        sys.exit(1)
        
    table_data = []
    for idx, w in enumerate(wallets):
        table_data.append([idx, w['name'], w['id'], w['subtype']])
        
    print(tabulate(table_data, headers=["Index", "Name", "ID", "Subtype"], tablefmt="grid"))
    
    while True:
        try:
            choice = int(input("\nSelect wallet index to use: "))
            if 0 <= choice < len(wallets):
                return wallets[choice]['id']
            print("Invalid index.")
        except ValueError:
            print("Please enter a number.")

def deploy_factory(wallet_id, wallet_address=None):
    compiled_sol = compile_contracts()
    bytecode = get_bytecode(compiled_sol, 'TokenFactory')
    
    print(f"\nDeploying TokenFactory using Wallet ID: {wallet_id}")
    print(f"Chain ID: {settings.chain_id}")
    
    # Fetch wallet address if not provided
    if not wallet_address:
        print("Fetching wallet address...")
        wallet_address = cobo_client.get_wallet_address(wallet_id, chain_id=settings.chain_id)
        
    if not wallet_address:
        print(f"⚠️ Could not automatically find address for wallet {wallet_id} on chain {settings.chain_id}")
        wallet_address = input("Please enter the wallet address manually: ").strip()
        if not wallet_address:
            print("❌ No address provided. Aborting.")
            return

    print(f"Using Wallet Address: {wallet_address}")

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
                calldata=bytecode
            )
        )
        
        params = ContractCallParams(
            request_id=f"deploy_factory_{int(time.time())}",
            chain_id=settings.chain_id,
            source=source,
            destination=destination,
            description="Deploy TokenFactory"
        )
        
        print("Transaction Payload Prepared:")
        print(params)
        
        confirm = input("\nConfirm deployment? (y/n): ")
        if confirm.lower() == 'y':
            transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
            print(f"🚀 Transaction Sent! ID: {transaction.transaction_id}")
            # print("🚀 [MOCK] Transaction Sent! (Uncomment code to enable real sending)")
        else:
            print("Deployment cancelled.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy TokenFactory Contract')
    parser.add_argument('--wallet-id', type=str, help='Cobo Wallet ID to use for deployment')
    parser.add_argument('--wallet-address', type=str, help='Specific wallet address to use')
    
    args = parser.parse_args()
    
    wallet_id = args.wallet_id
    if not wallet_id:
        wallet_id = select_wallet()
        
    deploy_factory(wallet_id, args.wallet_address)
