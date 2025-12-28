"""API endpoints for user authentication, including Google OAuth."""

from fastapi import APIRouter, Depends, HTTPException, status
import logging
from pydantic import BaseModel
from typing import Dict, Any # For type hints

# Import necessary Google libraries and verification logic
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests # Alias to avoid name clash

# Import Prisma client and dependency
from prisma import Prisma
from prisma.errors import TableNotFoundError

# Get Google Client ID and JWT settings from config
from app.core.config import get_settings
# Import security functions (JWT)
from app.core.security import create_access_token
# Import database dependency
from app.db.dependencies import get_db
# Import user CRUD operations
from app.crud.user import get_user_by_email, update_user_google_info
# Import User model for type hints
from prisma.models import User
# Import auth dependency
from app.api.dependencies.auth import get_current_user

settings = get_settings()
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID

logger = logging.getLogger(__name__)

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    """Request model for the Google login endpoint."""
    token: str

@router.get("/")
async def auth_root():
    """Root endpoint for the auth module."""
    return {"message": "Auth endpoint"} 


@router.get('/me', response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the details of the currently authenticated user."""
    logger.info(f"Returning authenticated user details for {current_user.email}")
    # The get_current_user dependency handles authentication and fetching.
    # We just need to return the user object provided by the dependency.
    return current_user

@router.post("/google", status_code=status.HTTP_200_OK)
async def login_with_google(
    request: GoogleLoginRequest,
    db: Prisma = Depends(get_db) # DB dependency
) -> Dict[str, Any]:
    """
    Handles user login via Google OAuth.

    Receives a Google ID token, verifies it, finds the corresponding user
    in the database (must exist), updates their Google ID (`subId`),
    generates a JWT, and returns it in the response.

    Args:
        request: The request body containing the Google ID token.
        db: Prisma database client dependency.

    Raises:
        HTTPException: 401 if the token is invalid, user doesn't exist, or verification fails.
        HTTPException: 500 if GOOGLE_CLIENT_ID is not configured or other internal errors occur.
        HTTPException: 400 if required info (email, sub) is missing from the Google token.
        HTTPException: 503 if database connection fails.

    Returns:
        A dictionary containing the JWT token and user information.
    """
    logger.info("Received Google login request")
    google_id_token = request.token
    logger.debug(f"Received Google ID token: {google_id_token[:10]}...") # Log only prefix

    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication is not configured correctly.",
        )

    try:
        # 1. Verify the Google token
        request_session = google_requests.Request()
        idinfo = id_token.verify_oauth2_token(
            google_id_token, 
            request_session, 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=settings.GOOGLE_TOKEN_TIMEOUT  # Add clock skew tolerance
        )
        logger.info(f"Google token verified successfully for email: {idinfo.get('email')}")

        # Extract required user info
        user_email = idinfo.get('email')
        google_sub_id = idinfo.get('sub') # 'sub' is the unique Google ID

        if not user_email or not google_sub_id:
            logger.error("Email or Google ID (sub) not found in verified token.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract required user information from Google token."
            )

        # 2. Check if user exists in DB
        logger.debug(f"Checking database for user with email: {user_email}")
        db_user = await get_user_by_email(db, user_email)

        if not db_user:
            logger.warning(f"Login attempt failed: User with email {user_email} not found in database.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, # Use 401 as user is authenticated by Google but not authorized here
                detail="User not found or not registered in the system. Please contact your administrator.",
            )
        logger.info(f"User found: {db_user.id} ({db_user.email})")

        # 3. Update user's subId if necessary
        if db_user.subId != google_sub_id:
            logger.info(f"Updating subId for user {db_user.id} from {db_user.subId} to {google_sub_id}")
            try:
                await update_user_google_info(db, user_id=db_user.id, google_sub_id=google_sub_id)
            except Exception as db_update_error:
                logger.error(f"Failed to update subId for user {db_user.id}: {db_update_error}", exc_info=True)
                # Decide if this is fatal; for now, we'll raise 500
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user information in database."
                )

        # 4. Generate JWT
        jwt_payload = {
            "sub": db_user.email, # Standard subject claim
            "user_id": db_user.id,
            "role": str(db_user.role), # Ensure role is string (enum -> str)
            "business_id": db_user.businessId
            # Add other relevant non-sensitive claims if needed (e.g., name)
        }
        access_token = create_access_token(data=jwt_payload)
        logger.info(f"JWT created for user {db_user.id}")

        # Return token directly in response instead of setting cookie
        return {
            "message": "Login successful",
            "user_id": db_user.id, 
            "role": db_user.role,
            "token": access_token  # Return JWT token directly
        }

    except ValueError as e:
        # Catches id_token.verify_oauth2_token errors
        logger.error(f"Google token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {e}",
        )
    except TableNotFoundError as e:
        # Handle missing database tables
        logger.error(f"Database tables not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized. Please run migrations: python scripts/db.py deploy",
        )
    except HTTPException as http_exc:
         # Re-raise HTTPExceptions directly (like 401 user not found)
         raise http_exc
    except Exception as e:
        # Catches other unexpected errors (DB connection, JWT creation issues, etc.)
        logger.error(f"An unexpected error occurred during Google login: {e}", exc_info=True)
        # Check if it's a DB connection issue hinted by dependencies.py
        if "Database connection not available" in str(e) or "Could not retrieve database connection" in str(e):
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                 detail="Database service unavailable."
             )
        # Check for table not found in error message
        if "does not exist" in str(e) or "TableNotFoundError" in str(type(e).__name__):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not initialized. Please run migrations: python scripts/db.py deploy",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred during login.",
        )
