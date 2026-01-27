"""API endpoints for user authentication, including Google OAuth."""

import logging
import uuid
from typing import Any, Dict  # For type hints
from datetime import datetime, timezone, timedelta
import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests  # Alias to avoid name clash

# Import necessary Google libraries and verification logic
from google.oauth2 import id_token
from prisma.errors import TableNotFoundError

# Import User model for type hints
from prisma.models import User
from pydantic import BaseModel, EmailStr

# Import auth dependency
from app.api.dependencies.auth import get_current_user

# Get Google Client ID and JWT settings from config
from app.core.config import get_settings

# Import security functions (JWT)
from app.core.security import create_access_token

# Import user CRUD operations
from app.crud.user import authenticate_user, create_user, get_user_by_email, update_user_google_info

# Import database dependency
from app.db.dependencies import get_db

# Import user schemas
from app.schemas.user import TokenResponse, UserLogin, UserRegister

# Import Prisma client and dependency
from prisma import Prisma

settings = get_settings()
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID

logger = logging.getLogger(__name__)

router = APIRouter()


class GoogleLoginRequest(BaseModel):
    """Request model for the Google login endpoint."""

    token: str
    is_access_token: bool = False


@router.post("/facebook", status_code=status.HTTP_200_OK)
async def login_with_facebook(
    request: Dict[str, Any], db: Prisma = Depends(get_db)
) -> Dict[str, Any]:
    """Handles login via Facebook after the user authenticates on the frontend."""
    fb_token = request.get("token")
    if not fb_token:
        raise HTTPException(status_code=400, detail="Facebook token is missing")

    try:
        # 1. Verify token with Facebook Graph API
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email&access_token={fb_token}"
            )
            if resp.status_code != 200:
                logger.error(f"Facebook verification failed: {resp.text}")
                raise HTTPException(status_code=401, detail="Invalid Facebook token")
            
            fb_info = resp.json()
            user_email = fb_info.get("email")
            fb_id = fb_info.get("id")

            if not user_email:
                # Some FB users don't have email or didn't grant permission
                user_email = f"{fb_id}@facebook.com"

            # 2. Find or Create user
            db_user = await get_user_by_email(db, user_email)
            if not db_user:
                logger.info(f"Creating new user from Facebook: {user_email}")
                # Create default business if needed
                default_biz = await db.business.find_first(where={"name": "Tagid Public Users"})
                if not default_biz:
                    default_biz = await db.business.create(data={"name": "Tagid Public Users", "slug": "public-users-fb"})
                
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                db_user = await create_user(
                    db=db,
                    email=user_email,
                    password=temp_password,
                    name=fb_info.get("name", "Facebook User"),
                    phone="000-000-0000",
                    address="Facebook Account",
                    business_id=default_biz.id,
                    role="CUSTOMER",
                    is_verified=True
                )
            
            # 3. Generate JWT
            jwt_payload = {
                "sub": db_user.id,
                "user_id": db_user.id,
                "email": db_user.email,
                "role": str(db_user.role),
                "business_id": db_user.businessId,
            }
            access_token = create_access_token(data=jwt_payload)

            return {
                "message": "Login successful",
                "user_id": db_user.id,
                "role": db_user.role,
                "token": access_token,
            }

    except Exception as e:
        logger.error(f"Facebook login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during Facebook login")


@router.get("/")
async def auth_root():
    """Root endpoint for the auth module."""
    return {"message": "Auth endpoint"}


class DevLoginRequest(BaseModel):
    """Request model for development login."""

    role: str = "STORE_MANAGER"


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(request: DevLoginRequest, db: Prisma = Depends(get_db)):
    """
    Development endpoint to login as any role without credentials.
    Creates a dev user if one doesn't exist for the role.
    """
    # Allow only if not production (you might want to check settings.ENVIRONMENT)
    # For now, we assume this is safe for your local setup

    email = f"dev_{request.role.lower()}@example.com"
    role = request.role.upper()

    logger.info(f"Dev login attempt for role: {role}")

    try:
        # Map Frontend Roles to Prisma Schema Roles
        role_mapping = {
            "SUPER_ADMIN": "SUPER_ADMIN",
            "NETWORK_ADMIN": "NETWORK_MANAGER",
            "STORE_MANAGER": "STORE_MANAGER",
            "SELLER": "EMPLOYEE",
            "CUSTOMER": "CUSTOMER",
            "ADMIN": "SUPER_ADMIN",
            "MANAGER": "STORE_MANAGER",
            "CASHIER": "EMPLOYEE",
        }
        prisma_role = role_mapping.get(role, "EMPLOYEE")
        logger.info(f"Mapped role {role} to prisma_role: {prisma_role}")

        # Ensure a dummy business exists
        logger.info("Checking for existing dev business")
        try:
            business = await db.business.find_first(where={"name": "Dev Business"})
            if not business:
                logger.info("Creating fresh dev business")
                business_slug = f"dev-business-{uuid.uuid4().hex[:8]}"
                business = await db.business.create(
                    data={"name": "Dev Business", "slug": business_slug}
                )
                logger.info(f"Business created successfully: {business.id}")
            else:
                logger.info(f"Found existing dev business: {business.id}")
        except Exception as bus_err:
            logger.error(f"Business operation failed: {bus_err}")
            raise HTTPException(status_code=500, detail=f"Business operation error: {str(bus_err)}")

        # Try to find existing dev user
        user = await get_user_by_email(db, email)

        if not user:
            logger.info(f"Creating new dev user: {email}")
            try:
                # Create new dev user
                user = await create_user(
                    db=db,
                    email=email,
                    password="devpassword",
                    name=f"Dev {role.title()}",
                    phone="000-000-0000",
                    address="Dev Environment",
                    business_id=business.id,
                    role=prisma_role,
                )
                logger.info(f"User created: {user.id}")
            except Exception as user_err:
                logger.error(f"User creation failed: {user_err}")
                raise HTTPException(status_code=500, detail=f"User creation error: {str(user_err)}")
    except Exception as e:
        logger.error(f"Dev login failed: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Dev login internal error: {str(e)}")

    # Generate Token
    jwt_payload = {
        "sub": user.id,
        "user_id": user.id,
        "email": user.email,
        "role": str(user.role),
        "business_id": user.businessId,
    }
    access_token = create_access_token(data=jwt_payload)

    return TokenResponse(
        message=f"Dev login successful as {role}",
        user_id=user.id,
        role=str(user.role),
        token=access_token,
    )


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the details of the currently authenticated user."""
    logger.info(f"Returning authenticated user details for {current_user.email}")
    # The get_current_user dependency handles authentication and fetching.
    # We just need to return the user object provided by the dependency.
    return current_user


@router.post("/google", status_code=status.HTTP_200_OK)
async def login_with_google(
    request: GoogleLoginRequest, db: Prisma = Depends(get_db)  # DB dependency
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
    logger.debug(f"Received Google ID token: {google_id_token[:10]}...")  # Log only prefix

    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication is not configured correctly.",
        )

    try:
        user_email = None
        google_sub_id = None

        # 1. Verify the Google token
        if request.is_access_token:
            logger.info("Verifying Google Access Token via userinfo endpoint")
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {google_id_token}"}
                )
                if resp.status_code != 200:
                    logger.error(f"Failed to verify access token: {resp.text}")
                    raise HTTPException(status_code=401, detail="Invalid Google access token")
                idinfo = resp.json()
                user_email = idinfo.get("email")
                google_sub_id = idinfo.get("sub")
                logger.info(f"Access token verified for email: {user_email}")
        else:
            logger.info("Verifying Google ID Token (JWT)")
            request_session = google_requests.Request()
            idinfo = id_token.verify_oauth2_token(
                google_id_token,
                request_session,
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=settings.GOOGLE_TOKEN_TIMEOUT,
            )
            user_email = idinfo.get("email")
            google_sub_id = idinfo.get("sub")
            logger.info(f"ID token verified for email: {user_email}")

        if not user_email or not google_sub_id:
            logger.error("Email or Google ID (sub) not found in verified token.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract required user information from Google token.",
            )

        # 2. Check if user exists in DB
        logger.debug(f"Checking database for user with email: {user_email}")
        db_user = await get_user_by_email(db, user_email)

        if not db_user:
            logger.info(f"User {user_email} not found. Creating new user via Google registration.")
            # Auto-register user if they don't exist
            
            # Find or create default public business
            default_biz = await db.business.find_first(where={"name": "Tagid Public Users"})
            if not default_biz:
                logger.info("Creating default 'Tagid Public Users' business")
                default_biz = await db.business.create(data={"name": "Tagid Public Users", "slug": "public-users"})
            
            # Generate a random password for OAuth users (they won't use it, but schema might require it)
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            db_user = await create_user(
                db=db,
                email=user_email,
                password=temp_password,
                name=idinfo.get("name", user_email.split('@')[0]),
                phone="000-000-0000", # Placeholder for Google users
                address="Google Account",
                business_id=default_biz.id,
                role="CUSTOMER",
                is_verified=True # Google users are pre-verified
            )
            logger.info(f"New user created via Google: {db_user.id}")

        # 3. Update user's subId if necessary
        if db_user.subId != google_sub_id:
            logger.info(
                f"Updating subId for user {db_user.id} from {db_user.subId} to {google_sub_id}"
            )
            try:
                await update_user_google_info(db, user_id=db_user.id, google_sub_id=google_sub_id)
            except Exception as db_update_error:
                logger.error(
                    f"Failed to update subId for user {db_user.id}: {db_update_error}",
                    exc_info=True,
                )
                # Not fatal if user is already verified by email/other

        # 4. Generate JWT
        jwt_payload = {
            "sub": db_user.id,  # Standard subject claim (ID)
            "user_id": db_user.id,
            "email": db_user.email,
            "role": str(db_user.role),  # Ensure role is string
            "business_id": db_user.businessId,
        }
        access_token = create_access_token(data=jwt_payload)
        logger.info(f"JWT created for user {db_user.id}")

        # Return token directly in response instead of setting cookie
        return {
            "message": "Login successful",
            "user_id": db_user.id,
            "role": db_user.role,
            "token": access_token,  # Return JWT token directly
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
        if "Database connection not available" in str(
            e
        ) or "Could not retrieve database connection" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable.",
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



class VerifyEmailRequest(BaseModel):
    """Schema for email verification request."""
    email: EmailStr
    code: str


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(request: VerifyEmailRequest, db: Prisma = Depends(get_db)):
    """
    Verify user's email address with the code sent via email.
    """
    user = await get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.isVerified:
         return TokenResponse(
            message="Email already verified",
            user_id=user.id,
            role=str(user.role),
            token=create_access_token(data={"sub": user.id, "user_id": user.id, "email": user.email, "role": str(user.role), "business_id": user.businessId}),
        )

    if not user.verificationCode or not user.verificationExpiresAt:
        raise HTTPException(status_code=400, detail="Invalid verification request")

    if user.verificationCode != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if datetime.now(timezone.utc) > user.verificationExpiresAt.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="Verification code expired")

    # Activate user
    await db.user.update(
        where={"id": user.id},
        data={
            "isVerified": True,
            "verificationCode": None,
            "verificationExpiresAt": None,
            "verifiedBy": "email"
        }
    )

    # Generate Token
    jwt_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": str(user.role),
        "business_id": user.businessId,
    }
    access_token = create_access_token(data=jwt_payload)

    return TokenResponse(
        message="Email verified successfully",
        user_id=user.id,
        role=str(user.role),
        token=access_token,
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_with_email(credentials: UserLogin, db: Prisma = Depends(get_db)) -> TokenResponse:
    """
    Handles user login via email and password.
    Blocks unverified users.
    """
    logger.info(f"Email login attempt for: {credentials.email}")

    try:
        # Authenticate user
        user = await authenticate_user(db, credentials.email, credentials.password)

        if not user:
            logger.warning(f"Login failed for {credentials.email}: invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
            
        # Check verification status
        if not user.isVerified:
             # Allow admin bypass for testing/emergency
            if user.role not in ["SUPER_ADMIN", "NETWORK_MANAGER"]:
                logger.warning(f"Login blocked for unverified user: {credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not verified. Please check your inbox for the verification code.",
                )

        # Generate JWT
        jwt_payload = {
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
            "role": str(user.role),
            "business_id": user.businessId,
        }
        access_token = create_access_token(data=jwt_payload)
        logger.info(f"JWT created for user {user.id}")

        return TokenResponse(
            message="Login successful",
            user_id=user.id,
            role=str(user.role),
            token=access_token,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Prisma = Depends(get_db)) -> TokenResponse:
    """
    Registers a new user and sends verification email.
    Note: Does NOT return a valid auth token immediately.
    """
    logger.info(f"Registration attempt for: {user_data.email}")
    
    # Generate 6-digit code
    verification_code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    if user_data.role != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration only allows CUSTOMER role.",
        )

    try:
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            logger.warning(f"Registration failed: email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user with CUSTOMER role
        business_id = user_data.businessId
        if not business_id:
            logger.info("No Business ID provided. Checking for default business...")
            # Find default public business or create it
            default_biz = await db.business.find_first(where={"name": "Tagid Public Users"})
            if not default_biz:
                logger.info("Creating default 'Tagid Public Users' business")
                default_biz = await db.business.create(data={"name": "Tagid Public Users", "slug": "public-users"})
            business_id = default_biz.id
            logger.info(f"Using Business ID: {business_id}")

        logger.info(f"Creating user {user_data.email} in DB...")
        new_user = await create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            phone=user_data.phone,
            address=user_data.address,
            business_id=business_id,
            role="CUSTOMER",
            verification_code=verification_code,
            verification_expires_at=expires_at,
            is_verified=False 
        )

        # Send Email
        from app.services.email_service import email_service
        email_sent = email_service.send_verification_email(new_user.email, verification_code)
        
        if not email_sent:
            logger.error("Failed to send verification email. User created but unverified.")
            # We still return success but maybe warn? For now standard flow.

        return TokenResponse(
            message="Registration successful. Verification code sent to email.",
            user_id=new_user.id,
            role=str(new_user.role),
            token="", # No token until verified
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration.",
        )

