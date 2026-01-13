import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status

@pytest.mark.asyncio
async def test_google_login_no_client_id(client: AsyncClient):
    """Test Google login when client ID is missing."""
    with patch("app.api.v1.endpoints.auth.GOOGLE_CLIENT_ID", None):
        response = await client.post("/api/v1/auth/google", json={"token": "test"})
        assert response.status_code == 500
        assert "not configured" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_google_login_invalid_token_format(client: AsyncClient):
    """Test Google login with token that fails verification."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token", side_effect=ValueError("Invalid token")):
        response = await client.post("/api/v1/auth/google", json={"token": "invalid"})
        assert response.status_code == 401
        assert "invalid google token" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_google_login_user_not_found(client: AsyncClient):
    """Test Google login when user is authenticated by Google but missing in DB."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify, \
         patch("app.api.v1.endpoints.auth.get_user_by_email", return_value=None):
        
        mock_verify.return_value = {"email": "stranger@example.com", "sub": "123"}
        response = await client.post("/api/v1/auth/google", json={"token": "valid"})
        assert response.status_code == 401
        assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_google_login_db_error(client: AsyncClient):
    """Test Google login with database exception."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify, \
         patch("app.api.v1.endpoints.auth.get_user_by_email", side_effect=Exception("DB Down")):
        
        mock_verify.return_value = {"email": "test@example.com", "sub": "123"}
        response = await client.post("/api/v1/auth/google", json={"token": "valid"})
        assert response.status_code == 500
        assert "unexpected internal error" in response.json()["detail"].lower()
