import time
import json
from web3 import Web3
from solcx import compile_standard, install_solc
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

# Hardcoded for MVP
GAS_LIMIT = 3000000

def compile_contract():
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
    return contract['abi'], contract['evm']['bytecode']['object']

def deploy_token_via_cobo(chain_id: str, name: str, symbol: str, partitions: list[str]):
    # 1. Find Wallet
    # In MVP, we might just pick the first funded one or use a specific one if configured.
    # For now, let's reuse the logic to find a funded wallet or use a default one.
    # To keep it simple and fast, let's assume the user has configured a wallet ID in env or we pick the first one.
    
    # Let's try to find one.
    wallets = cobo_client.list_web3_wallets()
    if not wallets:
        raise Exception("No Web3 wallets found")
        
    wallet_id = wallets[0]['id'] # Default to first
    wallet_address = cobo_client.get_wallet_address(wallet_id, chain_id=chain_id)
    
    if not wallet_address:
         raise Exception(f"No address found for wallet {wallet_id} on chain {chain_id}")

    # 2. Compile
    abi, bytecode = compile_contract()
    
    # 3. Encode Constructor
    w3 = Web3()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Convert partitions to bytes32
    # Assuming input is list of hex strings or strings
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
        wallet_address # Owner
    ).data_in_transaction
    
    # 4. Submit Transaction
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
        request_id=f"deploy_{int(time.time())}",
        chain_id=chain_id,
        source=source,
        destination=destination,
        description=f"Deploy {name} ({symbol})",
        gas_limit=GAS_LIMIT
    )
    
    transaction = cobo_client.transactions_api.create_contract_call_transaction(params)
    
    return {
        "tx_id": transaction.transaction_id,
        "wallet_id": wallet_id,
        "owner": wallet_address,
        "chain_id": chain_id,
        "status": "Submitted"
    }
