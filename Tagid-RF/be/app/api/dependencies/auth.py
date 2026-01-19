import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import (  # Using standard security classes
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from prisma.models import User  # Import User model for type hint

from app.core.security import verify_access_token
from app.crud.user import get_user_by_id
from app.db.dependencies import get_db
from prisma import Prisma

logger = logging.getLogger(__name__)

# JWT bearer token extractor
security = HTTPBearer(auto_error=False)


async def get_current_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Prisma = Depends(get_db),
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
    logger.info(f"Verifying token. Length: {len(token)}")

    # Verify token
    payload = verify_access_token(token)
    if payload is None:
        logger.warning("Token verification FAILED (returned None)")
        raise credentials_exception

    logger.debug(f"Token payload: {payload}")

    # Extract user_id from payload
    user_id = payload.get("user_id")
    if user_id is None:
        logger.warning("'user_id' not found in token payload")
        raise credentials_exception

    # Get user from database
    logger.debug(f"Attempting to fetch user from DB with ID: {user_id}")
    try:
        user = await get_user_by_id(db, user_id=user_id)
    except Exception as db_err:
        logger.error(f"Error fetching user {user_id} from DB: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error during authentication",
        )

    if user is None:
        logger.warning(f"User with ID {user_id} from token NOT FOUND in database")
        raise credentials_exception

    logger.info(f"Authenticated user: {user.id} ({user.email})")
    return user
