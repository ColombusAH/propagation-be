from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug("Access token created successfully.")
        return encoded_jwt
    except JWTError as e:
        logger.error(f"Error encoding JWT: {e}", exc_info=True)
        # Handle error appropriately, maybe raise a specific exception
        raise ValueError("Could not create access token") from e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hashes a plain password."""
#     return pwd_context.hash(password)

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies a JWT access token and returns its payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Token decoded successfully.")
        # TODO: Add more validation here if needed (e.g., check token type, specific claims)
        return payload
    except JWTError as e:
        logger.error(f"Could not validate credentials: {e}")
        return None # Or raise a specific exception
    except Exception as e:
        logger.error(f"An unexpected error occurred during token verification: {e}")
        return None # Or raise a specific exception 