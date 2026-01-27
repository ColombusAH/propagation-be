from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

import logging
from app.core.config import get_settings
from app.db.prisma import prisma_client
from prisma import Prisma

settings = get_settings()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> AsyncGenerator[Prisma, None]:
    """Get database connection."""
    async with prisma_client.get_db() as db:
        yield db


async def get_current_user(
    db: Prisma = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> dict:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # Try both 'user_id' and 'sub' to be compatible with different payload formats
        user_id = payload.get("user_id") or payload.get("sub")
        
        if user_id is None:
            logger.warning("Token payload is missing both 'user_id' and 'sub'")
            raise credentials_exception
            
        # If user_id is an email (contains @), try to find by email instead of ID
        if isinstance(user_id, str) and "@" in user_id:
             user = await db.user.find_unique(where={"email": user_id})
        else:
             user = await db.user.find_unique(where={"id": user_id})
             
        if user is None:
            logger.warning(f"User not found in DB for identifier: {user_id}")
            raise credentials_exception
            
        return user
    except JWTError as e:
        logger.error(f"JWT Validation error in get_current_user: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user auth: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get current active user."""
    # Logic for active check can go here (e.g., checking is_active flag)
    # For now, we return the user if they were successfully authenticated
    return current_user
