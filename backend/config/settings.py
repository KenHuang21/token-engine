from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    cobo_api_private_key: Optional[str] = Field(None, description="Cobo API Ed25519 Private Key")
    cobo_api_public_key: Optional[str] = Field(None, description="Cobo API Public Key")
    chain_id: str = Field("ETH_SEPOLIA", description="Default Chain ID")
    cobo_api_url: str = Field("https://api.cobo.com/v2", description="Cobo API Base URL")
    cobo_default_wallet_id: str = Field("07f7a5de-b138-4f80-a299-9f66450624d5", description="Default Cobo Wallet ID")
    
    # Allow loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
