"""API endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from prisma import Prisma
from prisma.models import User

from app.db.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.crud.user import get_user_by_id, create_user
from app.schemas.user import UserResponse, UserRegister

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def users_root():
    """Root endpoint for the users module."""
    return {"message": "Users endpoint"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get user by ID.
    
    Requires authentication. Users can only view their own info unless they are admin.
    """
    # Check permissions: users can view themselves, admins can view anyone
    if current_user.id != user_id and current_user.role not in ["SUPER_ADMIN", "NETWORK_MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserRegister,
    db: Prisma = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Create a new user.
    
    Only SUPER_ADMIN, NETWORK_MANAGER, and STORE_MANAGER can create users.
    Role restrictions:
    - SUPER_ADMIN: Can create any role
    - NETWORK_MANAGER: Can create STORE_MANAGER, EMPLOYEE, CUSTOMER
    - STORE_MANAGER: Can create EMPLOYEE, CUSTOMER
    """
    # Check permissions
    allowed_roles = {
        "SUPER_ADMIN": ["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE", "CUSTOMER"],
        "NETWORK_MANAGER": ["STORE_MANAGER", "EMPLOYEE", "CUSTOMER"],
        "STORE_MANAGER": ["EMPLOYEE", "CUSTOMER"]
    }
    
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users"
        )
    
    if user_data.role not in allowed_roles[current_user.role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to create users with role {user_data.role}"
        )
    
    try:
        new_user = await create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            phone=user_data.phone,
            address=user_data.address,
            business_id=user_data.businessId,
            role=user_data.role
        )
        
        return UserResponse.model_validate(new_user)
    
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        if "Unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )