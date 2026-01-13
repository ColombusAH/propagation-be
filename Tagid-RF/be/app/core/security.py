import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

<<<<<<< HEAD:Tagid-RF/be/app/core/security.py
=======
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

>>>>>>> origin/main:be/app/core/security.py

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
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hashes a plain password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

<<<<<<< HEAD:Tagid-RF/be/app/core/security.py
=======
def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)
>>>>>>> origin/main:be/app/core/security.py

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies a JWT access token and returns its payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Token decoded successfully.")
        # TODO: Add more validation here if needed (e.g., check token type, specific claims)
        return payload
    except JWTError as e:
        logger.error(f"Could not validate credentials: {e}")
        return None  # Or raise a specific exception
    except Exception as e:
        logger.error(f"An unexpected error occurred during token verification: {e}")
        return None  # Or raise a specific exception
