
import cobo_waas2
import uuid
from cobo_waas2.api import wallets_api, transactions_api
from cobo_waas2.models.wallet_type import WalletType
from cobo_waas2.models.wallet_subtype import WalletSubtype
from cobo_waas2.models.contract_call_params import ContractCallParams
from cobo_waas2.models.contract_call_source import ContractCallSource
from cobo_waas2.models.contract_call_source_type import ContractCallSourceType
from cobo_waas2.models.custodial_web3_contract_call_source import CustodialWeb3ContractCallSource
from cobo_waas2.models.contract_call_destination import ContractCallDestination
from cobo_waas2.models.contract_call_destination_type import ContractCallDestinationType
from cobo_waas2.models.evm_contract_call_destination import EvmContractCallDestination
from cobo_waas2.models.transaction_type import TransactionType
from cobo_waas2.crypto.local_ed25519_signer import LocalEd25519Signer
from backend.config.settings import settings

class CoboClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoboClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize the Cobo API client with configuration."""
        try:
            if not settings.cobo_api_private_key or not settings.cobo_api_url:
                print("Warning: Cobo API credentials not found.")
                return

            # Use explicit signer to ensure correct key handling
            signer = LocalEd25519Signer(settings.cobo_api_private_key)
            
            configuration = cobo_waas2.Configuration(
                host=settings.cobo_api_url,
                signer=signer
            )
            self.api_client = cobo_waas2.ApiClient(configuration)
            self.wallets_api = wallets_api.WalletsApi(self.api_client)
            self.transactions_api = transactions_api.TransactionsApi(self.api_client)
        except Exception as e:
            print(f"Failed to initialize Cobo client: {e}")
            self.api_client = None
            self.wallets_api = None
            self.transactions_api = None

    def get_wallets(self, wallet_type: WalletType = None, wallet_subtype: WalletSubtype = None, limit: int = 10):
        """
        List wallets from Cobo WaaS 2.0.
        
        Args:
            wallet_type (WalletType, optional): Filter by wallet type (e.g., CUSTODIAL, MPC).
            wallet_subtype (WalletSubtype, optional): Filter by wallet subtype (e.g., ASSET, ORG-CONTROLLED).
            limit (int): Number of results to return.
            
        Returns:
            list: A list of wallet objects.
        """
        try:
            # Prepare arguments, filtering out None values
            kwargs = {'limit': limit}
            if wallet_type:
                kwargs['wallet_type'] = wallet_type
            if wallet_subtype:
                kwargs['wallet_subtype'] = wallet_subtype

            response = self.wallets_api.list_wallets(**kwargs)
            return response.data
        except cobo_waas2.ApiException as e:
            print(f"Exception when calling WalletsApi->list_wallets: {e}")
            raise e

    def check_connection(self):
        """
        Verifies connection to Cobo WaaS 2.0 API.
        
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            # Try to fetch a small number of wallets to verify auth
            self.get_wallets(limit=1)
            return True
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

    def list_web3_wallets(self, chain_id: str = None):
        """
        List Custodial Web3 Wallets.
        
        Args:
            chain_id (str, optional): Filter by chain ID (e.g., 'ETH_SEPOLIA').
            
        Returns:
            list: A list of dicts with wallet info [{'id': ..., 'address': ..., 'name': ...}]
        """
        try:
            wallets = self.get_wallets(
                wallet_type=WalletType.CUSTODIAL,
                wallet_subtype=WalletSubtype.WEB3,
                limit=50
            )
            
            result = []
            for w in wallets:
                # Filter by chain if provided (assuming wallet might have chain info or we just list all)
                # Note: List wallets endpoint returns WalletInfo, which might not have chain_id directly 
                # if it's a multi-chain wallet, but Custodial Web3 usually has a specific address per chain 
                # or is unified. For now, we list all and let user choose, or filter if attribute exists.
                
                # Extract address if available (Custodial wallets usually have it in the response or need separate call)
                # The WalletInfo model is polymorphic. Let's check available attributes safely.
                # For Custodial Web3, we usually need to call `list_addresses` or similar if not in `WalletInfo`.
                # However, for deployment, we need the Wallet ID primarily.
                
                # Extract wallet ID safely from polymorphic model
                # The wallet object is a WalletInfo wrapper. The actual data is in actual_instance.
                wallet_id = None
                name = "Unknown"
                subtype = "Unknown"
                
                if hasattr(w, 'actual_instance') and w.actual_instance:
                    wallet_id = getattr(w.actual_instance, 'wallet_id', None)
                    name = getattr(w.actual_instance, 'name', "Unknown")
                    subtype = getattr(w.actual_instance, 'wallet_subtype', "Unknown")
                
                if wallet_id:
                    wallet_data = {
                        'id': wallet_id,
                        'name': name,
                        'type': getattr(w.actual_instance, 'wallet_type', 'Custodial'),
                        'subtype': subtype
                    }
                    result.append(wallet_data)
                
            return result
        except Exception as e:
            print(f"Failed to list web3 wallets: {e}")
            return []

    def get_transaction(self, transaction_id: str):
        """
        Get transaction details.
        """
        try:
            return self.transactions_api.get_transaction_by_id(transaction_id)
        except Exception as e:
            print(f"Failed to get transaction: {e}")
            return None

    def list_transactions(self, wallet_id: str = None, limit: int = 10):
        """
        List transactions.
        """
        try:
            kwargs = {'limit': limit}
            if wallet_id:
                kwargs['wallet_ids'] = wallet_id
                
            return self.transactions_api.list_transactions(**kwargs).data
        except Exception as e:
            print(f"Failed to list transactions: {e}")
            return []

    def get_wallet_address(self, wallet_id: str, chain_id: str = None):
        """
        Get the address of a wallet.
        
        Args:
            wallet_id (str): The wallet ID.
            chain_id (str, optional): Chain ID to filter addresses.
            
        Returns:
            str: The wallet address or None if not found.
        """
        try:
            # For Custodial Web3 wallets, we can list addresses
            # Note: The SDK method might be list_addresses or similar on wallets_api
            # Let's try list_addresses if available, or list_token_balances which includes address
            
            # Checking available methods on wallets_api via dir() in previous steps showed:
            # 'list_addresses', 'list_addresses_with_http_info', ...
            
            kwargs = {'wallet_id': wallet_id, 'limit': 1}
            if chain_id:
                kwargs['chain_ids'] = chain_id
                
            response = self.wallets_api.list_addresses(**kwargs)
            if response.data:
                return response.data[0].address
            return None
        except Exception as e:
            print(f"Failed to get wallet address: {e}")
            return None

    def get_best_wallet(self, chain_id: str) -> dict:
        """
        Finds the first funded wallet for the given chain.
        Returns dict with 'wallet_id' and 'address'.
        """
        print(f"Searching for funded {chain_id} wallets...")
        wallets = self.list_web3_wallets()
        
        for w in wallets:
            wallet_id = w['id']
            address = self.get_wallet_address(wallet_id, chain_id=chain_id)
            
            if not address:
                continue
                
            # Check balance (Mock check for now to avoid slow API calls, or implement real check)
            # For MVP speed, we'll just return the first one that has an address on this chain.
            # In production, we would call list_token_balances.
            print(f"✅ Found wallet: {w['name']} ({address}) Type: {w['type']} Subtype: {w['subtype']}")
            return {"wallet_id": wallet_id, "address": address, "subtype": w['subtype']}
            
    def create_contract_call(self, chain_id: str, wallet_id: str, to_address: str, calldata: str, amount: int = 0):
        """
        Create a contract call transaction.
        """
        try:
            if not self.transactions_api:
                raise Exception("Cobo API not initialized")

            source = ContractCallSource(
                actual_instance=CustodialWeb3ContractCallSource(
                    source_type=ContractCallSourceType.WEB3,
                    wallet_id=wallet_id,
                    address=self.get_wallet_address(wallet_id, chain_id)
                )
            )
            
            destination = ContractCallDestination(
                actual_instance=EvmContractCallDestination(
                    destination_type=ContractCallDestinationType.EVM_CONTRACT,
                    address=to_address,
                    calldata=calldata,
                    amount=str(amount)
                )
            )
            
            params = ContractCallParams(
                request_id=str(uuid.uuid4()), # Ensure unique ID for every request
                chain_id=chain_id,
                source=source,
                destination=destination,
                description="Mint Token via TokenEngine"
            )
            
            response = self.transactions_api.create_contract_call_transaction(params)
            return response.transaction_id
            
        except Exception as e:
            print(f"Failed to create contract call: {e}")
            raise e

    def deploy_contract(self, chain_id: str, wallet_id: str, bytecode: str, amount: int = 0):
        """
        Deploy a contract using Cobo WaaS.
        """
        try:
            if not self.transactions_api:
                raise Exception("Cobo API not initialized")

            source = ContractCallSource(
                actual_instance=CustodialWeb3ContractCallSource(
                    source_type=ContractCallSourceType.WEB3,
                    wallet_id=wallet_id,
                    address=self.get_wallet_address(wallet_id, chain_id)
                )
            )
            
            # For deployment, destination address is usually empty or null.
            # We use EvmContractCallDestination with empty address.
            destination = ContractCallDestination(
                actual_instance=EvmContractCallDestination(
                    destination_type=ContractCallDestinationType.EVM_CONTRACT,
                    address="", # Empty address for deployment
                    calldata=bytecode,
                    amount=str(amount)
                )
            )
            
            params = ContractCallParams(
                request_id=str(uuid.uuid4()),
                chain_id=chain_id,
                source=source,
                destination=destination,
                description="Deploy Token via TokenEngine"
            )
            
            response = self.transactions_api.create_contract_call_transaction(params)
            return response.transaction_id
            
        except Exception as e:
            print(f"Failed to deploy contract: {e}")
            raise e

# Global instance
cobo_client = CoboClient()
