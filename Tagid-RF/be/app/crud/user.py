import logging
from typing import Optional
from datetime import datetime

from prisma.models import User

from prisma import Prisma

logger = logging.getLogger(__name__)


async def get_user_by_email(db: Prisma, email: str) -> Optional[User]:
    """Fetches a user from the database by their email address."""
    try:
        logger.debug(f"Attempting to find user by email: {email}")
        user = await db.user.find_unique(where={"email": email})
        if user:
            logger.debug(f"User found with email {email}: ID {user.id}")
        else:
            logger.debug(f"No user found with email: {email}")
        return user
    except Exception as e:
        logger.error(f"Database error while fetching user by email {email}: {e}", exc_info=True)
        # Re-raise or handle appropriately depending on desired error propagation
        raise


async def update_user_google_info(db: Prisma, user_id: str, google_sub_id: str) -> Optional[User]:
    """Updates the subId (Google ID) for a given user."""
    try:
        logger.debug(f"Attempting to update subId for user {user_id} to {google_sub_id}")
        updated_user = await db.user.update(
            where={
                "id": user_id,
            },
            data={"subId": google_sub_id, "verifiedBy": "google"},
        )
        if updated_user:
            logger.info(f"Successfully updated subId for user {user_id}.")
        else:
            # This case might be less likely with find_unique first, but good practice
            logger.warning(f"Attempted to update subId for non-existent user ID: {user_id}")
        return updated_user
    except Exception as e:
        logger.error(
            f"Database error while updating subId for user {user_id}: {e}",
            exc_info=True,
        )
        raise


async def get_user_by_id(db: Prisma, user_id: str) -> Optional[User]:
    """Fetches a user from the database by their unique ID."""
    try:
        logger.debug(f"Attempting to find user by ID: {user_id}")
        user = await db.user.find_unique(where={"id": user_id})
        if user:
            logger.debug(f"User found with ID {user_id}")
        else:
            logger.debug(f"No user found with ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Database error while fetching user by ID {user_id}: {e}", exc_info=True)
        raise


async def create_user(
    db: Prisma,
    email: str,
    password: str,
    name: str,
    phone: str,
    address: str,
    business_id: str,
    role: str = "CUSTOMER",
    verification_code: Optional[str] = None,
    verification_expires_at: Optional[datetime] = None,
    is_verified: bool = False,
) -> User:
    """Creates a new user with hashed password."""
    from app.core.security import get_password_hash

    try:
        logger.debug(f"Creating new user with email: {email}")
        hashed_password = get_password_hash(password)

        new_user = await db.user.create(
            data={
                "email": email,
                "password": hashed_password,
                "name": name,
                "phone": phone,
                "address": address,
                "businessId": business_id,
                "role": role,
                "verifiedBy": "email" if is_verified else None,
                "isVerified": is_verified,
                "verificationCode": verification_code,
                "verificationExpiresAt": verification_expires_at,
            }
        )
        logger.info(f"Successfully created user {new_user.id} with email {email}")
        return new_user
    except Exception as e:
        logger.error(f"Database error while creating user {email}: {e}", exc_info=True)
        raise


async def authenticate_user(db: Prisma, email: str, password: str) -> Optional[User]:
    """Authenticates a user by email and password."""
    from app.core.security import verify_password

    try:
        logger.debug(f"Attempting to authenticate user: {email}")
        user = await get_user_by_email(db, email)

        if not user:
            logger.debug(f"Authentication failed: user {email} not found")
            return None

        if not user.password:
            logger.debug(f"Authentication failed: user {email} has no password (OAuth only)")
            return None

        if not verify_password(password, user.password):
            logger.debug(f"Authentication failed: invalid password for {email}")
            return None

        logger.info(f"Successfully authenticated user {email}")
        return user
    except Exception as e:
        logger.error(f"Error during authentication for {email}: {e}", exc_info=True)
        raise
