from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
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
    GOOGLE_CLIENT_ID: Optional[str] = None  # Optional for deployments without Google OAuth
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
    RFID_READER_IP: str = "169.254.128.161"  # CF-001-548 TCP/IP address
    RFID_READER_PORT: int = 4001  # Default RFID reader port
    RFID_CONNECTION_TYPE: str = "tcp"  # tcp or serial
    RFID_SERIAL_DEVICE: Optional[str] = None  # Serial device path (e.g., /dev/ttyUSB0 or COM3)
    RFID_READER_ID: str = "M-200"  # Unique identifier for this reader
    LOG_LEVEL: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR

    # Payment Settings
    DEFAULT_CURRENCY: str = "ILS"
    DEFAULT_PAYMENT_PROVIDER: str = "TRANZILA"

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Tranzila (טרנזילה)
    TRANZILA_TERMINAL_NAME: Optional[str] = None
    TRANZILA_API_KEY: Optional[str] = None
    TRANZILA_API_ENDPOINT: str = "https://direct.tranzila.com/api"

    # Nexi (נייקס)
    NEXI_TERMINAL_ID: Optional[str] = None
    NEXI_API_KEY: Optional[str] = None
    NEXI_API_ENDPOINT: str = "https://api.nexi.it"
    NEXI_MERCHANT_ID: Optional[str] = None

    # Firebase Cloud Messaging (Push Notifications)
    FCM_SERVER_KEY: Optional[str] = None
    FCM_PROJECT_ID: Optional[str] = None

    # Web Push (VAPID)
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_CLAIMS_SUB: str = "mailto:admin@example.com"

    # Theft Alerts
    ENABLE_THEFT_DETECTION: bool = True
    ALERT_STAKEHOLDER_ROLES: List[str] = [
        "SUPER_ADMIN",
        "NETWORK_MANAGER",
        "STORE_MANAGER",
    ]

    @field_validator("VAPID_PRIVATE_KEY", "VAPID_PUBLIC_KEY", "FCM_SERVER_KEY", mode="before")
    @classmethod
    def trim_keys(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Create settings instance
settings = get_settings()
