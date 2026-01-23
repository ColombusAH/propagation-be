"""
Store management API endpoints.
"""

from typing import List, Optional

from app.models.store import Store, User
from app.services.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/stores", tags=["stores"])


# ============= Pydantic Schemas =============


class StoreCreate(BaseModel):
    """Schema for creating a new store."""

    name: str
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreUpdate(BaseModel):
    """Schema for updating a store."""

    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    """Schema for store response."""

    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    is_active: bool
    seller_count: int = 0
    manager_name: Optional[str] = None

    class Config:
        from_attributes = True


class AssignManagerRequest(BaseModel):
    """Schema for assigning a manager to a store."""

    user_id: int


# ============= API Endpoints =============


@router.get("", response_model=List[StoreResponse])
async def list_stores(is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    """
    List all stores.

    - **is_active**: Filter by active status
    """
    query = db.query(Store)

    if is_active is not None:
        query = query.filter(Store.is_active == is_active)

    stores = query.all()

    # Enrich with stats
    result = []
    for store in stores:
        # Count sellers in store
        seller_count = (
            db.query(User)
            .filter(
                User.store_id == store.id,
                User.role == "SELLER",
                User.is_active.is_(True),
            )
            .count()
        )

        # Get manager name
        manager = (
            db.query(User)
            .filter(
                User.store_id == store.id,
                User.role == "MANAGER",
                User.is_active.is_(True),
            )
            .first()
        )

        result.append(
            StoreResponse(
                id=store.id,
                name=store.name,
                address=store.address,
                phone=store.phone,
                is_active=store.is_active,
                seller_count=seller_count,
                manager_name=manager.name if manager else None,
            )
        )

    return result


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(store_data: StoreCreate, db: Session = Depends(get_db)):
    """
    Create a new store.

    Requires ADMIN role (not enforced here, should be added via dependency).
    """
    store = Store(
        name=store_data.name, address=store_data.address, phone=store_data.phone
    )

    db.add(store)
    db.commit()
    db.refresh(store)

    return StoreResponse(
        id=store.id,
        name=store.name,
        address=store.address,
        phone=store.phone,
        is_active=store.is_active,
        seller_count=0,
        manager_name=None,
    )


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(store_id: int, db: Session = Depends(get_db)):
    """Get a specific store by ID."""
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    # Get stats
    seller_count = (
        db.query(User)
        .filter(
            User.store_id == store.id, User.role == "SELLER", User.is_active.is_(True)
        )
        .count()
    )

    manager = (
        db.query(User)
        .filter(
            User.store_id == store.id, User.role == "MANAGER", User.is_active.is_(True)
        )
        .first()
    )

    return StoreResponse(
        id=store.id,
        name=store.name,
        address=store.address,
        phone=store.phone,
        is_active=store.is_active,
        seller_count=seller_count,
        manager_name=manager.name if manager else None,
    )


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int, store_data: StoreUpdate, db: Session = Depends(get_db)
):
    """Update a store."""
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    # Update fields
    if store_data.name is not None:
        store.name = store_data.name
    if store_data.address is not None:
        store.address = store_data.address
    if store_data.phone is not None:
        store.phone = store_data.phone
    if store_data.is_active is not None:
        store.is_active = store_data.is_active

    db.commit()
    db.refresh(store)

    return StoreResponse(
        id=store.id,
        name=store.name,
        address=store.address,
        phone=store.phone,
        is_active=store.is_active,
        seller_count=0,
        manager_name=None,
    )


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    """
    Delete a store (soft delete - sets is_active to False).
    """
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    store.is_active = False
    db.commit()

    return None


@router.post("/{store_id}/manager", response_model=dict)
async def assign_manager(
    store_id: int, request: AssignManagerRequest, db: Session = Depends(get_db)
):
    """
    Assign a manager to a store.

    The user must have MANAGER role.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )

    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user's store and role
    user.store_id = store_id
    user.role = "MANAGER"

    db.commit()

    return {"message": f"Manager {user.name} assigned to store {store.name}"}
