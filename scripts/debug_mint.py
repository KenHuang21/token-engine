import sys
import os
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.contract_service import mint_by_partition

# Mock data
CHAIN_ID = "BSC_BNB"
CONTRACT_ADDRESS = "0xd4402d1e46f1b13b3d1e683b2604c93dd91075b9" # Using wallet as mock contract for now to test encoding
PARTITION = "Class A"
TO_ADDRESS = "0xd4402d1e46f1b13b3d1e683b2604c93dd91075b9"
AMOUNT = 100

try:
    print("Attempting minting...")
    result = mint_by_partition(
        chain_id=CHAIN_ID,
        contract_address=CONTRACT_ADDRESS,
        partition=PARTITION,
        to_address=TO_ADDRESS,
        amount=AMOUNT
    )
    print("Success:", result)
except Exception:
    traceback.print_exc()
