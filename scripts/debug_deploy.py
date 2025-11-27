import sys
import os
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.contract_service import deploy_erc1400

try:
    print("Attempting deployment...")
    result = deploy_erc1400(
        chain_id="BSC_BNB",
        name="Debug Token",
        symbol="DBG",
        partitions=["Class A"],
        supply=0
    )
    print("Success:", result)
except Exception:
    traceback.print_exc()
