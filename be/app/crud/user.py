from prisma import Prisma
from prisma.models import User
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def get_user_by_email(db: Prisma, email: str) -> Optional[User]:
    """Fetches a user from the database by their email address."""
    try:
        logger.debug(f"Attempting to find user by email: {email}")
        user = await db.user.find_unique(where={'email': email})
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
            where={'id': user_id,},
            data={'subId': google_sub_id, 'verifiedBy': 'google'}
        )
        if updated_user:
            logger.info(f"Successfully updated subId for user {user_id}.")
        else:
             # This case might be less likely with find_unique first, but good practice
             logger.warning(f"Attempted to update subId for non-existent user ID: {user_id}")
        return updated_user
    except Exception as e:
        logger.error(f"Database error while updating subId for user {user_id}: {e}", exc_info=True)
        raise 