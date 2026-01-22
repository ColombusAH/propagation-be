import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import status

class MockUser:
    def __init__(self):
        self.id = "user-123"
        self.email = "test@example.com"
        self.role = "CUSTOMER"
        self.businessId = "biz-123"
        self.subId = "google-123"
        self.createdAt = datetime.now()
        self.updatedAt = datetime.now()

@pytest.mark.asyncio
async def test_auth_google_login_success(client, db_session):
    """Test successful Google login."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": "test@example.com",
            "sub": "google-123",
            "iss": "accounts.google.com"
        }
        
        mock_user = MockUser()
        
        db_session.client.user.find_unique.return_value = mock_user
        
        response = await client.post("/api/v1/auth/google", json={"token": "valid-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user_id"] == "user-123"

@pytest.mark.asyncio
async def test_auth_google_login_update_sub(client, db_session):
    """Test Google login updates google_sub_id if changed."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": "test@example.com",
            "sub": "google-new-123"
        }
        
        mock_user = MockUser()
        mock_user.subId = "google-old-123" # Different sub
        
        db_session.client.user.find_unique.return_value = mock_user
        
        response = await client.post("/api/v1/auth/google", json={"token": "valid-token"})
        
        assert response.status_code == 200
        # Verify update was called
        db_session.client.user.update.assert_called()
        call_args = db_session.client.user.update.call_args
        assert call_args[1]['data']['subId'] == "google-new-123"

@pytest.mark.asyncio
async def test_auth_google_login_user_not_found(client, db_session):
    """Test Google login failure when user doesn't exist."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": "unknown@example.com",
            "sub": "google-123"
        }
        
        db_session.client.user.find_unique.return_value = None
        
        response = await client.post("/api/v1/auth/google", json={"token": "valid-token"})
        
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_google_login_invalid_token(client, db_session):
    """Test Google login with invalid token."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")
        
        response = await client.post("/api/v1/auth/google", json={"token": "invalid-token"})
        
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_google_missing_email(client, db_session):
    """Test Google login when token is missing email."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "sub": "google-123"
            # No email
        }
        
        response = await client.post("/api/v1/auth/google", json={"token": "valid-token"})
        
        assert response.status_code == 400
        assert "Could not extract required user information" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_register_non_customer(client, db_session):
    """Test registration failure for non-CUSTOMER role."""
    payload = {
        "email": "admin@example.com",
        "password": "password123",
        "name": "Admin",
        "role": "SUPER_ADMIN",
        "phone": "123",
        "businessId": "biz",
        "address": "123 Main St"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 400
    assert "only allows CUSTOMER role" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_dev_login(client, db_session):
    """Test dev login endpoint."""
    # Mock finding business and user
    db_session.client.business.find_first.return_value = MagicMock(id="biz-dev")
    
    mock_user = MockUser()
    mock_user.id = "dev-user-id"
    mock_user.email = "dev_store_manager@example.com"
    mock_user.role = "STORE_MANAGER"
    mock_user.businessId = "biz-dev"
    
    db_session.client.user.find_unique.return_value = mock_user
    
    with patch("prisma.Prisma", return_value=db_session): # Patch local Prisma used in dev_login
        response = await client.post("/api/v1/auth/dev-login", json={"role": "STORE_MANAGER"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "STORE_MANAGER"
