"""API endpoints for user authentication, including Google OAuth."""

from fastapi import APIRouter, Depends, HTTPException, status, Body
import logging
from pydantic import BaseModel

# Import necessary Google libraries and verification logic
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests # Alias to avoid name clash

# Get Google Client ID from settings
from app.core.config import get_settings
# TODO: Potentially import JWT creation/user handling dependencies here
# from app.core.security import create_access_token
# from app.db.session import get_db
# from sqlalchemy.orm import Session
# from app.crud.user import get_or_create_user_by_google_id

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


@router.get('/me')
async def get_me():
    """Placeholder endpoint to get the current user (currently returns null)."""
    logger.info("Getting me")
    # TODO: Implement logic to return the currently authenticated user based on session/token
    return None

@router.post("/google", status_code=status.HTTP_200_OK)
async def login_with_google(request: GoogleLoginRequest):
    """
    Handles user login via Google OAuth.

    Receives a Google ID token from the frontend, verifies it against
    Google's public keys, and checks the audience (client ID).

    If the token is valid, it extracts user information.

    **TODO:**
    1.  Implement logic to find an existing user in the database matching the
        Google ID (`sub`) or email, or create a new user if one doesn't exist.
    2.  Generate an application-specific session token (e.g., JWT) for the
        authenticated user.
    3.  Return the session token and potentially user information to the frontend.

    Args:
        request: The request body containing the Google ID token.

    Raises:
        HTTPException: 401 if the token is invalid or verification fails.
        HTTPException: 500 if GOOGLE_CLIENT_ID is not configured or other internal errors occur.
        HTTPException: 400 if required info (email, sub) is missing from the token.

    Returns:
        Currently returns mock user data upon successful token verification.
        Should eventually return a session token and user data.
    """
    logger.info("Received Google login request")
    google_id_token = request.token
    logger.debug(f"Received Google ID token: {google_id_token[:10]}...") # Log only prefix for security
    
    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication is not configured correctly.",
        )

    try:
        # Verify the token using Google's library
        request_session = google_requests.Request()
        idinfo = id_token.verify_oauth2_token(
            google_id_token, request_session, GOOGLE_CLIENT_ID
        )
        logger.info(f"Google token verified successfully for email: {idinfo.get('email')}")

        # Extract user info from idinfo
        user_email = idinfo.get('email')
        user_name = idinfo.get('name')
        google_id = idinfo.get('sub') # 'sub' is the unique Google ID

        if not user_email or not google_id:
            logger.error("Email or Google ID (sub) not found in verified token.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract required user information from Google token."
            )

        # --- TODO: Implement Database User Lookup/Creation --- 
        # user = get_or_create_user_by_google_info(db, google_id, user_email, user_name)
        # if not user:
        #     raise HTTPException(status_code=500, detail="Server error processing user data.")
        logger.warning("DB user lookup/creation not implemented yet.")
        # --- End DB User TODO ---

        # --- TODO: Implement Session/JWT Token Generation --- 
        # access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        # return {"access_token": access_token, "token_type": "bearer", "user": user.to_dict()} # Example response
        logger.warning("Session/JWT token generation not implemented yet.")
        # --- End Session/JWT TODO ---
        
        # Return verified user info (placeholder until DB/JWT is done)
        return {
            "id": google_id, 
            "name": user_name,
            "email": user_email,
            "role": "user", # Placeholder role
            "message": "Token verified, user/session logic pending"
        }

    except ValueError as e:
        # ValueError is raised by verify_oauth2_token on various validation failures
        logger.error(f"Google token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {e}", # Include reason if possible
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during Google login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )
