import sys
import os
import json
import time
from web3 import Web3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cobo_service import cobo_client
from cobo_waas2.models import (
    ContractCallParams,
    ContractCallSource,
    CustodialWeb3ContractCallSource,
    ContractCallSourceType,
    ContractCallDestination,
    ContractCallDestinationType,
    EvmContractCallDestination
)

CHAIN_ID = "BSC_BNB"
PARTITION_CLASS_A = "0x436c617373410000000000000000000000000000000000000000000000000000"
MINT_AMOUNT = 888

def mint():
    if not os.path.exists('bsc_deployment.json'):
        print("❌ Deployment file not found. Run deploy_bsc.py first.")
        return

    with open('bsc_deployment.json', 'r') as f:
        info = json.load(f)

    # We need the contract address. 
    # Since deploy script might not have extracted it (Cobo API doesn't always return it easily in Tx info),
    # we might need to ask user or fetch receipt. 
    # For this script, let's assume we can get it or user inputs it.
    # Actually, let's try to fetch receipt from Web3 if we had a node, but we don't.
    # We will ask user to input contract address if not in JSON (which it isn't yet).
    
    contract_address = info.get('contract_address')
    if not contract_address:
        contract_address = input("Enter deployed Contract Address: ").strip()
        # Update JSON
        info['contract_address'] = contract_address
        with open('bsc_deployment.json', 'w') as f:
            json.dump(info, f, indent=2)

    print(f"Minting {MINT_AMOUNT} tokens to {info['owner']}...")

    w3 = Web3()
    contract = w3.eth.contract(address=contract_address, abi=info['abi'])
    
    # issueByPartition(partition, tokenHolder, value, data)
    calldata = contract.functions.issueByPartition(
        PARTITION_CLASS_A,
        info['owner'],
        MINT_AMOUNT,
        b""
    )._encode_transaction_data()
    
    try:
        source = ContractCallSource(
            discriminator='CustodialWeb3ContractCallSource',
            actual_instance=CustodialWeb3ContractCallSource(
                source_type=ContractCallSourceType.WEB3,
                wallet_id=info['wallet_id'],
                address=info['owner']
            )
        )
        
        destination = ContractCallDestination(
            discriminator='EvmContractCallDestination',
            actual_instance=EvmContractCallDestination(
                destination_type=ContractCallDestinationType.EVM_CONTRACT,
                address=contract_address,
                value="0",
                calldata=calldata
            )
        )
        
        params = ContractCallParams(
            request_id=f"mint_bsc_{int(time.time())}",
            chain_id=CHAIN_ID,
            source=source,
            destination=destination,
            description="Mint ERC1400 Tokens"
        )
        
        transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
        print(f"Transaction Submitted! ID: {transaction.transaction_id}")
        
        # Poll
        print("Waiting for confirmation...")
        for _ in range(30):
            time.sleep(2)
            tx_info = cobo_client.transactions_api.get_transaction_by_id(transaction.transaction_id)
            if tx_info.transaction_hash:
                 print(f"✅ Success! View on BscScan: https://bscscan.com/tx/{tx_info.transaction_hash}")
                 return
                 
    except Exception as e:
        print(f"Minting failed: {e}")

if __name__ == "__main__":
    mint()
