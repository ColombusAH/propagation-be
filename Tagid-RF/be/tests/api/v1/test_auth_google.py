from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_google_login_success(client: AsyncClient):
    """Test successful Google login with mocking."""
    payload = {"token": "mock-valid-token"}

    with (
        patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify,
        patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get_user,
    ):

        mock_verify.return_value = {"email": "test@example.com", "sub": "google-sub-123"}

        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.subId = "google-sub-123"
        mock_user.role = "admin"
        mock_user.businessId = "biz-123"
        mock_get_user.return_value = mock_user

        response = await client.post("/api/v1/auth/google", json=payload)
        assert response.status_code == 200
        assert "token" in response.json()
        assert response.json()["user_id"] == "user-123"
