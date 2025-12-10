"""
Rewards Distribution Service for CoboERC20TestVotes Contract

This service handles interactions with the rewards distribution contract:
- Issuer functions: setRewardToken, takeSnapshot, depositRewards
- Investor functions: claim, claimable
- View functions: rewardToken, snapshotBlock, totalSnapshotSupply, etc.
"""

import json
import os
from web3 import Web3
from backend.services.cobo_service import cobo_client

# Load ABI
ABI_PATH = os.path.join(os.path.dirname(__file__), '../artifacts/CoboERC20TestVotesABI.json')
with open(ABI_PATH, 'r') as f:
    abi_data =json.load(f)
    REWARDS_ABI = abi_data['abi']

# ERC20 ABI for approve function
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Chain ID to RPC mapping (using Cobo chain ID conventions)
CHAIN_RPC_URLS = {
    "ETH_SEPOLIA": "https://ethereum-sepolia-rpc.publicnode.com",  # Internal: ETH_SEPOLIA → Cobo: SETH
    "SETH": "https://ethereum-sepolia-rpc.publicnode.com",  # Direct Cobo chain ID
    "ETH": "https://ethereum-rpc.publicnode.com",
    "MATIC_POLYGON": "https://polygon-rpc.com",
    "MATIC": "https://polygon-rpc.com",  # Direct Cobo chain ID
    "BSC_BNB": "https://bsc-dataseed.binance.org",
}

def map_chain_id(chain_id: str) -> str:
    """Map internal chain IDs to Cobo API chain IDs."""
    mapping = {
        "ETH_SEPOLIA": "SETH",
        "MATIC_POLYGON": "MATIC"
    }
    return mapping.get(chain_id, chain_id)

def get_web3(chain_id: str):
    """Get Web3 instance for the given chain."""
    rpc_url = CHAIN_RPC_URLS.get(chain_id)
    if not rpc_url:
        raise ValueError(f"Unsupported chain: {chain_id}")
    return Web3(Web3.HTTPProvider(rpc_url))


def get_rewards_info(contract_address: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Get current rewards configuration and status.
    
    Returns:
        dict: {
            'rewardToken': address,
            'snapshotBlock': int,
            'totalSnapshotSupply': int,
            'totalRewardAmount': int
        }
    """
    try:
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        reward_token = contract.functions.rewardToken().call()
        snapshot_block = contract.functions.snapshotBlock().call()
        total_snapshot_supply = contract.functions.totalSnapshotSupply().call()
        total_reward_amount = contract.functions.totalRewardAmount().call()
        
        return {
            "rewardToken": reward_token,
            "snapshotBlock": snapshot_block,
            "totalSnapshotSupply": str(total_snapshot_supply),
            "totalRewardAmount": str(total_reward_amount),
            "currentBlock": w3.eth.block_number
        }
    except Exception as e:
        raise Exception(f"Failed to get rewards info: {str(e)}")


def get_claimable(contract_address: str, investor_address: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Get claimable amount for an investor.
    
    Args:
        contract_address: The rewards contract address
        investor_address: The investor's wallet address
        chain_id: The blockchain network
        
    Returns:
        dict: {'claimable': str, 'claimed': str}
    """
    try:
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        investor_addr = Web3.to_checksum_address(investor_address)
        claimable_amount = contract.functions.claimable(investor_addr).call()
        claimed_amount = contract.functions.claimed(investor_addr).call()
        
        return {
            "claimable": str(claimable_amount),
            "claimed": str(claimed_amount),
            "investor": investor_address
        }
    except Exception as e:
        raise Exception(f"Failed to get claimable amount: {str(e)}")


def set_reward_token(contract_address: str, reward_token_address: str, wallet_id: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Set the reward token address (Issuer only - requires MANAGER_ROLE).
    
    Args:
        contract_address: The rewards contract address
        reward_token_address: The ERC20 token to use as rewards
        wallet_id: Cobo wallet ID (must have MANAGER_ROLE)
        chain_id: The blockchain network
        
    Returns:
        str: Transaction ID
    """
    try:
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        # Encode function call
        calldata = contract.functions.setRewardToken(
            Web3.to_checksum_address(reward_token_address)
        ).build_transaction({
            'from': '0x0000000000000000000000000000000000000000',  # Dummy for encoding
            'gas': 100000,
            'gasPrice': 0
        })['data']
        
        # Create transaction via Cobo
        tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=contract_address,
            calldata=calldata,
            amount=0
        )
        
        return tx_id
    except Exception as e:
        raise Exception(f"Failed to set reward token: {str(e)}")


def take_snapshot(contract_address: str, wallet_id: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Take a snapshot of token holders (Issuer only - requires MANAGER_ROLE).
    Snapshot is taken 20 blocks before the current block.
    
    Args:
        contract_address: The rewards contract address
        wallet_id: Cobo wallet ID (must have MANAGER_ROLE)
        chain_id: The blockchain network
        
    Returns:
        str: Transaction ID
    """
    try:
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        # Encode function call
        calldata = contract.functions.takeSnapshot().build_transaction({
            'from': '0x0000000000000000000000000000000000000000',
            'gas': 100000,
            'gasPrice': 0
        })['data']
        
        # Create transaction via Cobo
        tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=contract_address,
            calldata=calldata,
            amount=0
        )
        
        return tx_id
    except Exception as e:
        raise Exception(f"Failed to take snapshot: {str(e)}")


def check_allowance(reward_token_address: str, owner_address: str, spender_address: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Check if the rewards contract has allowance to spend reward tokens.
    
    Returns:
        int: Current allowance amount
    """
    try:
        w3 = get_web3(chain_id)
        token_contract = w3.eth.contract(address=Web3.to_checksum_address(reward_token_address), abi=ERC20_ABI)
        
        # Map chain ID for Cobo API calls
        api_chain_id = map_chain_id(chain_id)
        
        allowance = token_contract.functions.allowance(
            Web3.to_checksum_address(owner_address),
            Web3.to_checksum_address(spender_address)
        ).call()
        
        return allowance
    except Exception as e:
        raise Exception(f"Failed to check allowance: {str(e)}")


def approve_reward_token(reward_token_address: str, spender_address: str, amount: int, wallet_id: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Approve the rewards contract to spend reward tokens.
    
    Args:
        reward_token_address: The ERC20 reward token address
        spender_address: The rewards contract address
        amount: Amount to approve
        wallet_id: Cobo wallet ID
        chain_id: The blockchain network
        
    Returns:
        str: Transaction ID
    """
    try:
        w3 = get_web3(chain_id)
        token_contract = w3.eth.contract(address=Web3.to_checksum_address(reward_token_address), abi=ERC20_ABI)
        
        # Encode approve function call
        calldata = token_contract.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount
        ).build_transaction({
            'from': '0x0000000000000000000000000000000000000000',
            'gas': 100000,
            'gasPrice': 0
        })['data']
        
        # Create transaction via Cobo
        tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=reward_token_address,
            calldata=calldata,
            amount=0
        )
        
        return tx_id
    except Exception as e:
        raise Exception(f"Failed to approve reward token: {str(e)}")


def deposit_rewards(contract_address: str, amount: int, wallet_id: str, chain_id: str = "ETH_SEPOLIA", auto_approve: bool = True):
    """
    Deposit rewards to the contract (Issuer only - requires MANAGER_ROLE).
    
    Args:
        contract_address: The rewards contract address
        amount: Amount of reward tokens to deposit
        wallet_id: Cobo wallet ID (must have MANAGER_ROLE)
        chain_id: The blockchain network
        auto_approve: If True, automatically approve before depositing
        
    Returns:
        dict: {'approve_tx_id': str or None, 'deposit_tx_id': str}
    """
    try:
        result = {'approve_tx_id': None, 'deposit_tx_id': None}
        
        if auto_approve:
            # Get rewards info to find reward token address
            info = get_rewards_info(contract_address, chain_id)
            reward_token = info['rewardToken']
            
            if reward_token == '0x0000000000000000000000000000000000000000':
                raise Exception("Reward token not set. Please set reward token first.")
            
            # Get wallet address with correct chain ID mapping
            api_chain_id = map_chain_id(chain_id)
            wallet_address = cobo_client.get_wallet_address(wallet_id, api_chain_id)
            
            # Check current allowance
            current_allowance = check_allowance(reward_token, wallet_address, contract_address, chain_id)
            
            # Approve if needed
            if current_allowance < amount:
                print(f"Approving {amount} tokens (current allowance: {current_allowance})...")
                approve_tx_id = approve_reward_token(reward_token, contract_address, amount, wallet_id, chain_id)
                result['approve_tx_id'] = approve_tx_id
                print(f"Approval transaction created: {approve_tx_id}")
                # Note: In production, you'd wait for approval to confirm before depositing
        
        # Encode depositRewards function call
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        calldata = contract.functions.depositRewards(amount).build_transaction({
            'from': '0x0000000000000000000000000000000000000000',
            'gas': 150000,
            'gasPrice': 0
        })['data']
        
        # Create deposit transaction via Cobo
        deposit_tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=contract_address,
            calldata=calldata,
            amount=0
        )
        
        result['deposit_tx_id'] = deposit_tx_id
        return result
        
    except Exception as e:
        raise Exception(f"Failed to deposit rewards: {str(e)}")


def claim_rewards(contract_address: str, wallet_id: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Claim rewards for the investor.
    
    Args:
        contract_address: The rewards contract address
        wallet_id: Cobo wallet ID of the investor
        chain_id: The blockchain network
        
    Returns:
        str: Transaction ID
    """
    try:
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=REWARDS_ABI)
        
        # Encode claim function call
        calldata = contract.functions.claim().build_transaction({
            'from': '0x0000000000000000000000000000000000000000',
            'gas': 200000,
            'gasPrice': 0
        })['data']
        
        # Create transaction via Cobo
        tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=contract_address,
            calldata=calldata,
            amount=0
        )
        
        return tx_id
    except Exception as e:
        raise Exception(f"Failed to claim rewards: {str(e)}")

def delegate_tokens(token_contract_address: str, delegatee_address: str, wallet_id: str, chain_id: str = "ETH_SEPOLIA"):
    """
    Delegate voting power for ERC20Votes tokens (required for snapshot eligibility).
    
    Args:
        token_contract_address: The ERC20Votes token contract address
        delegatee_address: Address to delegate voting power to (usually investor's own address)
        wallet_id: Cobo wallet ID
        chain_id: The blockchain network
        
    Returns:
        str: Transaction ID
    """
    try:
        # ERC20Votes delegate ABI
        delegate_abi = [{
            "inputs": [{"internalType": "address", "name": "delegatee", "type": "address"}],
            "name": "delegate",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        w3 = get_web3(chain_id)
        contract = w3.eth.contract(address=Web3.to_checksum_address(token_contract_address), abi=delegate_abi)
        
        # Encode delegate function call
        calldata = contract.functions.delegate(
            Web3.to_checksum_address(delegatee_address)
        ).build_transaction({
            'from': '0x0000000000000000000000000000000000000000',
            'gas': 100000,
            'gasPrice': 0
        })['data']
        
        # Create transaction via Cobo
        tx_id = cobo_client.create_contract_call(
            chain_id=chain_id,
            wallet_id=wallet_id,
            to_address=token_contract_address,
            calldata=calldata,
            amount=0
        )
        
        return tx_id
    except Exception as e:
        raise Exception(f"Failed to delegate tokens: {str(e)}")
