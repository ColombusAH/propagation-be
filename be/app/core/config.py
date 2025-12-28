from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List

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
        "*"  # Allow all origins in development - can be restricted in production
    ]
    
    # RFID Settings
    RFID_DATABASE_URL: Optional[str] = None  # Optional separate DB for RFID, defaults to DATABASE_URL
    RFID_READER_IP: str = "169.254.128.161"  # CF-001-548 TCP/IP address
    RFID_READER_PORT: int = 4001  # Default RFID reader port
    RFID_CONNECTION_TYPE: str = "tcp"  # tcp or serial
    RFID_SERIAL_DEVICE: Optional[str] = None  # Serial device path (e.g., /dev/ttyUSB0 or COM3)
    RFID_READER_ID: str = "M-200"  # Unique identifier for this reader
    LOG_LEVEL: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 