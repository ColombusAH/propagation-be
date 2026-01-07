"""
User management API endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.models.store import Store, User
from app.services.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


# ============= Pydantic Schemas =============

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "SELLER"  # ADMIN, MANAGER, SELLER, CUSTOMER
    store_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    store_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    store_id: Optional[int]
    store_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class AssignStoreRequest(BaseModel):
    """Schema for assigning a user to a store."""
    store_id: int


# ============= API Endpoints =============

@router.get("", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = None,
    store_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all users.
    
    - **role**: Filter by role (ADMIN, MANAGER, SELLER, CUSTOMER)
    - **store_id**: Filter by store
    - **is_active**: Filter by active status
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role.upper())
    if store_id:
        query = query.filter(User.store_id == store_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.all()
    
    # Enrich with store names
    result = []
    for user in users:
        store_name = None
        if user.store_id:
            store = db.query(Store).filter(Store.id == user.store_id).first()
            store_name = store.name if store else None
        
        result.append(UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            store_id=user.store_id,
            store_name=store_name,
            is_active=user.is_active
        ))
    
    return result


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    - ADMIN: Can create MANAGER and SELLER
    - MANAGER: Can create SELLER only
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    valid_roles = ["ADMIN", "MANAGER", "SELLER", "CUSTOMER"]
    if user_data.role.upper() not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role.upper(),
        store_id=user_data.store_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Get store name
    store_name = None
    if user.store_id:
        store = db.query(Store).filter(Store.id == user.store_id).first()
        store_name = store.name if store else None
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        store_id=user.store_id,
        store_name=store_name,
        is_active=user.is_active
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    store_name = None
    if user.store_id:
        store = db.query(Store).filter(Store.id == user.store_id).first()
        store_name = store.name if store else None
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        store_id=user.store_id,
        store_name=store_name,
        is_active=user.is_active
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.email is not None:
        # Check email uniqueness
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.role is not None:
        user.role = user_data.role.upper()
    if user_data.store_id is not None:
        user.store_id = user_data.store_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    store_name = None
    if user.store_id:
        store = db.query(Store).filter(Store.id == user.store_id).first()
        store_name = store.name if store else None
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        store_id=user.store_id,
        store_name=store_name,
        is_active=user.is_active
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user (soft delete - sets is_active to False).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return None


@router.post("/{user_id}/assign-store", response_model=dict)
async def assign_user_to_store(
    user_id: int,
    request: AssignStoreRequest,
    db: Session = Depends(get_db)
):
    """Assign a user to a store."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    store = db.query(Store).filter(Store.id == request.store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    user.store_id = request.store_id
    db.commit()
    
    return {"message": f"User {user.name} assigned to store {store.name}"}
