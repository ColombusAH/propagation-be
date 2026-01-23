import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.skip(reason="Integration tests require DB and business setup")


async def test_get_network_qr(
    async_client: AsyncClient, normal_user_token_headers: dict, db_session
):
    """
    Test retrieving Network QR for a user associated with a business.
    """
    from unittest.mock import MagicMock

    from app.api.dependencies.auth import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.businessId = "biz-123"
    mock_user.role = "CUSTOMER"  # Or minimal role

    # We also need to ensure business lookup works if the endpoint uses it.
    # network endpoint likely uses businessId from user.

    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        response = await async_client.get(
            f"{settings.API_V1_STR}/network/qr",
            headers=normal_user_token_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "slug" in data
        assert "entry_url" in data
        assert "business_name" in data

        # Verify slug format (cuid-like or at least string)
        assert len(data["slug"]) > 0

        # Verify URL construction
        expected_url_prefix = "https://app.tagid.com/enter/"
        assert data["entry_url"].startswith(expected_url_prefix)
        assert data["entry_url"].endswith(data["slug"])
    finally:
        app.dependency_overrides.clear()


async def test_get_network_qr_unauthorized(async_client: AsyncClient):
    """
    Test that unauthenticated users cannot access the endpoint.
    """
    # Ensure no override
    from app.main import app

    app.dependency_overrides.pop("get_current_user", None)

    response = await async_client.get(f"{settings.API_V1_STR}/network/qr")
    assert response.status_code == 401
