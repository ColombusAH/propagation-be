import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_root(client: AsyncClient):
    """Test the auth root endpoint."""
    response = await client.get("/api/v1/auth/")
    assert response.status_code == 200
    assert response.json() == {"message": "Auth endpoint"}

@pytest.mark.asyncio
async def test_google_login_invalid_token(client: AsyncClient):
    """Test Google login with an invalid token."""
    payload = {"token": "invalid-token-123"}
    response = await client.post("/api/v1/auth/google", json=payload)
    # Token verification should fail and return 401
    assert response.status_code == 401
    assert "Invalid Google token" in response.json()["detail"]
