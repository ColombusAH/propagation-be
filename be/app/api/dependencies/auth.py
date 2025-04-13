from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Using standard security classes
from typing import Optional
import logging

from app.core.security import verify_access_token
from app.crud.user import get_user_by_id
from app.db.dependencies import get_db
from prisma import Prisma
from prisma.models import User # Import User model for type hint

logger = logging.getLogger(__name__)

# JWT bearer token extractor
security = HTTPBearer(auto_error=False)

async def get_current_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security), 
    db: Prisma = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.

    1. Extracts token from Authorization header.
    2. Verifies the JWT token.
    3. Retrieves the user from the database based on the token's payload.
    4. Returns the User object or raises HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if Authorization header is present
    if authorization is None:
        logger.warning("No Authorization header found in request")
        raise credentials_exception
    
    token = authorization.credentials
    logger.info(f"Verifying token from Authorization header, length: {len(token)}")
    
    # Verify token
    payload = verify_access_token(token)
    if payload is None:
        logger.warning("Token verification failed")
        raise credentials_exception

    # Extract user_id from payload
    user_id = payload.get("user_id")
    if user_id is None:
        logger.warning("'user_id' not found in token payload")
        raise credentials_exception

    # Get user from database
    logger.debug(f"Attempting to fetch user from DB with ID: {user_id}")
    user = await get_user_by_id(db, user_id=user_id)
    if user is None:
        logger.warning(f"User with ID {user_id} from token not found in database")
        raise credentials_exception
    
    logger.info(f"Authenticated user retrieved: {user.id} ({user.email})")
    return user 