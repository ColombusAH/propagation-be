"""
Integration tests for alerts API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_alerts_manager(async_client: AsyncClient, manager_auth_headers):
    """Test listing alerts as manager."""
    response = await async_client.get(
        "/api/v1/alerts/",
        headers=manager_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_alerts_unauthorized(async_client: AsyncClient, auth_headers):
    """Test that regular users cannot list all alerts."""
    response = await async_client.get(
        "/api/v1/alerts/",
        headers=auth_headers,
    )

    assert response.status_code == 403  # Forbidden


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_my_alerts(async_client: AsyncClient, auth_headers):
    """Test getting user's own alerts."""
    response = await async_client.get(
        "/api/v1/alerts/my-alerts",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
