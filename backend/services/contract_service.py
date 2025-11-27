import json
import time
import os
from web3 import Web3
from backend.services.cobo_service import cobo_client
from cobo_waas2.models import (
    ContractCallParams,
    ContractCallSource,
    CustodialWeb3ContractCallSource,
    ContractCallSourceType,
    ContractCallDestination,
    ContractCallDestinationType,
    EvmContractCallDestination
)

# Use absolute path for Vercel
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATH = os.path.join(BASE_DIR, 'artifacts/SimpleERC1400.json')
GAS_LIMIT = 3000000

def get_artifact():
    if not os.path.exists(ARTIFACT_PATH):
        raise Exception("Artifact not found. Run scripts/compile_artifacts.py first.")
    with open(ARTIFACT_PATH, 'r') as f:
        return json.load(f)

def deploy_erc1400(chain_id: str, name: str, symbol: str, partitions: list[str], supply: int = 0):
    # 1. Get Wallet
    wallet = cobo_client.get_best_wallet(chain_id)
    wallet_id = wallet['wallet_id']
    owner = Web3.to_checksum_address(wallet['address'])

    # 2. Get Artifacts
    artifact = get_artifact()
    abi = artifact['abi']
    bytecode = artifact['bytecode']

    # 3. Encode Constructor
    w3 = Web3()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Convert partitions to bytes32
    partitions_bytes = []
    for p in partitions:
        if p.startswith("0x"):
            partitions_bytes.append(p)
        else:
            # Pad string to bytes32
            partitions_bytes.append(Web3.to_hex(text=p).ljust(66, '0'))

    constructor_args = contract.constructor(
        name,
        symbol,
        partitions_bytes,
        owner
    ).data_in_transaction
    
    # 4. Submit Transaction
    source = ContractCallSource(
        discriminator='CustodialWeb3ContractCallSource',
        actual_instance=CustodialWeb3ContractCallSource(
            source_type=ContractCallSourceType.WEB3,
            wallet_id=wallet_id,
            address=owner
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
        request_id=f"deploy_{int(time.time())}",
        chain_id=chain_id,
        source=source,
        destination=destination,
        description=f"Deploy {name}",
        gas_limit=GAS_LIMIT
    )
    
    transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
    
    return {
        "tx_id": transaction.transaction_id,
        "wallet_id": wallet_id,
        "owner": owner,
        "status": "Submitted"
    }

def mint_by_partition(chain_id: str, contract_address: str, partition: str, to_address: str, amount: int):
    # 1. Get Wallet (Must be owner)
    wallet = cobo_client.get_best_wallet(chain_id)
    wallet_id = wallet['wallet_id']
    owner = wallet['address']
    
    # 2. Get ABI
    artifact = get_artifact()
    abi = artifact['abi']
    
    # 3. Encode Call
    w3 = Web3()
    checksum_contract = Web3.to_checksum_address(contract_address)
    checksum_to = Web3.to_checksum_address(to_address)
    contract = w3.eth.contract(address=checksum_contract, abi=abi)
    
    # Ensure partition is bytes32
    if not partition.startswith("0x"):
        partition_bytes = Web3.to_hex(text=partition).ljust(66, '0')
    else:
        partition_bytes = partition

    calldata = contract.functions.issueByPartition(
        partition_bytes,
        checksum_to,
        amount,
        b""
    )._encode_transaction_data()
    
    # 4. Submit
    source = ContractCallSource(
        discriminator='CustodialWeb3ContractCallSource',
        actual_instance=CustodialWeb3ContractCallSource(
            source_type=ContractCallSourceType.WEB3,
            wallet_id=wallet_id,
            address=owner
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
        request_id=f"mint_{int(time.time())}",
        chain_id=chain_id,
        source=source,
        destination=destination,
        description=f"Mint {amount} to {to_address}",
        gas_limit=GAS_LIMIT
    )
    
    transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
    return {"tx_id": transaction.transaction_id, "status": "Submitted"}

def set_document(chain_id: str, contract_address: str, name: str, uri: str, doc_hash: str):
    # Note: SimpleERC1400 might not have setDocument implemented in the flat file yet.
    # If not, we'll skip or mock it. The requirement asked to "Refactor document logic".
    # Assuming the contract supports ERC1643 or similar if we added it.
    # For now, let's assume we just log it or call a generic method if it existed.
    # Since we used a simple implementation, let's check if we have setDocument.
    # We don't in the current SimpleERC1400.sol.
    # We will mock this for the MVP backend logic or add it to contract if needed.
    # Given the constraint "Refactor document logic", I will implement the backend stub
    # but note that the contract needs update.
    return {"status": "Not Implemented in Contract", "tx_id": "mock_tx_id"}
