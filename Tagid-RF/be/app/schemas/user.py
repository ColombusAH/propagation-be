"""Pydantic schemas for user-related API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """
    Schema for user registration.
    
    Used when creating a new user account in the system.
    
    Example:
        ```python
        user = UserRegister(
            email="user@example.com",
            password="SecurePass123!",
            name="John Doe",
            phone="+972-50-1234567",
            address="123 Main St, Tel Aviv",
            businessId="123456789",
            role="CUSTOMER"
        )
        ```
    """

    email: EmailStr = Field(description="User's email address (must be valid email format)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    name: str = Field(description="User's full name")
    phone: str = Field(description="Phone number (include country code)")
    address: str = Field(description="Physical address")
    businessId: str = Field(description="Business/Tax ID number")
    role: str = Field(
        default="CUSTOMER",
        description="User role: CUSTOMER, CASHIER, MANAGER, or ADMIN"
    )


class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Used for authenticating existing users.
    
    Example:
        ```python
        login = UserLogin(
            email="user@example.com",
            password="SecurePass123!"
        )
        ```
    """

    email: EmailStr = Field(description="User's registered email address")
    password: str = Field(description="User's password")


class UserResponse(BaseModel):
    """
    Schema for user response (without password).
    
    Returned after successful registration, login, or when fetching user data.
    Password is never included in responses for security.
    
    Example Response:
        ```json
        {
            "id": "user_abc123",
            "email": "user@example.com",
            "name": "John Doe",
            "phone": "+972-50-1234567",
            "address": "123 Main St, Tel Aviv",
            "role": "CUSTOMER",
            "businessId": "123456789",
            "createdAt": "2026-01-06T10:00:00Z"
        }
        ```
    """

    id: str = Field(description="Unique user identifier")
    email: str = Field(description="User's email address")
    name: str = Field(description="User's full name")
    phone: str = Field(description="Phone number")
    address: str = Field(description="Physical address")
    role: str = Field(description="User role (CUSTOMER, CASHIER, MANAGER, ADMIN)")
    businessId: str = Field(description="Business/Tax ID number")
    createdAt: datetime = Field(description="Account creation timestamp")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    
    Returned after successful login. The token should be included in
    subsequent API requests in the Authorization header.
    
    Example Response:
        ```json
        {
            "message": "Login successful",
            "user_id": "user_abc123",
            "role": "CUSTOMER",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        ```
        
    Usage:
        ```javascript
        // Include token in API requests
        fetch('/api/v1/orders', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        ```
    """

    message: str = Field(description="Success message")
    user_id: str = Field(description="Authenticated user's ID")
    role: str = Field(description="User's role for authorization")
    token: str = Field(description="JWT authentication token (include in Authorization header)")
