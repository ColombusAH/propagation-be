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
        "https://*.railway.app",
        "http://*.railway.app",
        "*"  # Allow all origins in development - can be restricted in production
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 