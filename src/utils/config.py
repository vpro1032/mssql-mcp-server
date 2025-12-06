import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MSSQL Connection Settings
    MSSQL_HOST: str = "localhost"
    MSSQL_PORT: int = 1433
    MSSQL_DATABASE: str = "master"
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str
    MSSQL_ENCRYPT: bool = True
    MSSQL_TRUST_SERVER_CERTIFICATE: bool = False
    MSSQL_CONNECTION_TIMEOUT: int = 30
    MSSQL_REQUEST_TIMEOUT: int = 30

    # Connection Pool Settings
    MIN_POOL_SIZE: int = 2
    MAX_POOL_SIZE: int = 10
    IDLE_TIMEOUT: int = 300
    CONNECTION_LIFETIME: int = 1800

    # Security Settings
    MSSQL_ALLOW_WRITE_OPERATIONS: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()
