from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Shifty"
    DEBUG: bool = False
    MODE: str = "development"

    # Database Settings
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30000
    JWT_ALGORITHM: str = "HS256"
    GOOGLE_CLIENT_ID: str
    GOOGLE_TOKEN_TIMEOUT: int = 300  # 5 minutes timeout for Google token verification

    # Security Headers
    SECURITY_HEADERS: bool = True  # Enable security headers by default

    # CORS Settings - include Railway domains and wildcard for development
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "https://localhost:5173",
        "https://*.railway.app",
        "http://*.railway.app",
        "*",  # Allow all origins in development - can be restricted in production
    ]

    # RFID Settings
    RFID_DATABASE_URL: Optional[str] = (
        None  # Optional separate DB for RFID, defaults to DATABASE_URL
    )
    RFID_READER_IP: str = "192.168.1.100"  # CF-H906 WiFi IP address
    RFID_READER_PORT: int = 4001  # Default RFID reader port
    RFID_CONNECTION_TYPE: str = "wifi"  # wifi, bluetooth, or serial
    RFID_READER_ID: str = "CF-H906-001"  # Unique identifier for this reader
    RFID_SIMULATION_MODE: bool = True  # Enable simulation mode for testing
    LOG_LEVEL: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
