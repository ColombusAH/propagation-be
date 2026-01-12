import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api.dependencies.auth import get_current_user
from prisma.models import User

@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    """Test /me endpoint with dependency override."""
    mock_user = MagicMock(spec=User)
    mock_user.email = "me@example.com"
    mock_user.id = "user-123"
    mock_user.role = "USER"
    mock_user.businessId = "biz-1"
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"
    finally:
        # Clear overrides
        app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_google_login_missing_info(client: AsyncClient):
    """Test Google login when token info is missing email or sub."""
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {"email": "test@example.com"} # Missing 'sub'
        response = await client.post("/api/v1/auth/google", json={"token": "valid"})
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_google_login_subid_update_fail(client: AsyncClient):
    """Test Google login when subId update fails."""
    mock_user = MagicMock()
    mock_user.email = "update@example.com"
    mock_user.subId = "old-sub"
    mock_user.id = "user-789"
    
    with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify, \
         patch("app.api.v1.endpoints.auth.get_user_by_email", return_value=mock_user), \
         patch("app.api.v1.endpoints.auth.update_user_google_info", side_effect=Exception("Update Error")):
        
        mock_verify.return_value = {"email": "update@example.com", "sub": "new-sub"}
        response = await client.post("/api/v1/auth/google", json={"token": "valid"})
        assert response.status_code == 500
