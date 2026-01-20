import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_get_network_qr(
    async_client: AsyncClient, normal_user_token_headers: dict, db_session
):
    """
    Test retrieving Network QR for a user associated with a business.
    """
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


async def test_get_network_qr_unauthorized(async_client: AsyncClient):
    """
    Test that unauthenticated users cannot access the endpoint.
    """
    response = await async_client.get(f"{settings.API_V1_STR}/network/qr")
    assert response.status_code == 401
