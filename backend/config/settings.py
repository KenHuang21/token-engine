from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    cobo_api_private_key: str = Field(..., description="Cobo API Ed25519 Private Key")
    cobo_api_public_key: str = Field(..., description="Cobo API Public Key")
    chain_id: str = Field("ETH_SEPOLIA", description="Default Chain ID")
    cobo_api_url: str = Field("https://api.cobo.com/v2", description="Cobo API Base URL")
    
    # Allow loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
