from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://claims_user:claims_pass@localhost:5432/claims_guardian"

    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # App Config
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True

    # API Config
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
