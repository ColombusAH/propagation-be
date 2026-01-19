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
    from unittest.mock import MagicMock, patch

    from app.db.dependencies import get_db
    from app.main import app

    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db
    try:
        payload = {"token": "invalid-token-123"}

        with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")
            response = await client.post("/api/v1/auth/google", json=payload)
            # Token verification should fail and return 401
            assert response.status_code == 401
            assert "Invalid Google token" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
