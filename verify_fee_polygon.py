import os
from dotenv import load_dotenv
load_dotenv(override=True)

from backend.services.cobo_service import cobo_client
from cobo_waas2.models.contract_call_source import ContractCallSource
from cobo_waas2.models.custodial_web3_contract_call_source import CustodialWeb3ContractCallSource
from cobo_waas2.models.contract_call_source_type import ContractCallSourceType
from cobo_waas2.models.contract_call_destination import ContractCallDestination
from cobo_waas2.models.evm_contract_call_destination import EvmContractCallDestination
from cobo_waas2.models.contract_call_destination_type import ContractCallDestinationType

def verify_polygon_fee():
    print("Verifying Polygon Fee Implementation...")
    cobo_client._initialize_client()
    
    # List of candidates to try
    candidates = ["MATIC"]
    
    wallet_id = "07f7a5de-b138-4f80-a299-9f66450624d5"
    to_address = "0x7d773721f93a04686358d13ab5a03da39cb907dc" # Self
    
    source = ContractCallSource(
        actual_instance=CustodialWeb3ContractCallSource(
            source_type=ContractCallSourceType.WEB3,
            wallet_id=wallet_id,
            address=to_address
        )
    )
    
    destination = ContractCallDestination(
        actual_instance=EvmContractCallDestination(
            destination_type=ContractCallDestinationType.EVM_CONTRACT,
            address=to_address,
            calldata="0x00",
            amount="0"
        )
    )
    
    for chain_id in candidates:
        print(f"\nTesting Chain ID: {chain_id}")
        # Note: estimate_and_get_fee has internal mapping logic, but we want to test RAW first 
        # to find the correct ID, then ensure mapping uses it.
        # Actually, let's just call estimate_and_get_fee but bypass the mapping check by passing it directly?
        # No, estimate_and_get_fee maps MATIC_POLYGON -> POLYGON.
        # Let's try to call the raw estimate logic here to find the valid ID.
        
        from cobo_waas2.models.estimate_fee_params import EstimateFeeParams
        from cobo_waas2.models.estimate_contract_call_fee_params import EstimateContractCallFeeParams
        from cobo_waas2.models.estimate_fee_request_type import EstimateFeeRequestType
        import uuid
        
        try:
            params = EstimateContractCallFeeParams(
                request_id=str(uuid.uuid4()),
                request_type=EstimateFeeRequestType.TRANSFER, # Try TRANSFER
                chain_id=chain_id,
                source=source,
                destination=destination
            )
            req = EstimateFeeParams(actual_instance=params)
            resp = cobo_client.transactions_api.estimate_fee(req)
            print(f"✅ SUCCESS with {chain_id}!")
            print(resp)
            break
        except Exception as e:
            print(f"❌ Failed with {chain_id}: {e}")

if __name__ == "__main__":
    verify_polygon_fee()
