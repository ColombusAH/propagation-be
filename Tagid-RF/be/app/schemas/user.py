"""Pydantic schemas for user-related API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    phone: str
    address: str
    businessId: str
    role: str = "CUSTOMER"  # Default role


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without password)."""

    id: str
    email: str
    name: str
    phone: str
    address: str
    role: str
    businessId: str
    createdAt: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    message: str
    user_id: str
    role: str
    token: str
