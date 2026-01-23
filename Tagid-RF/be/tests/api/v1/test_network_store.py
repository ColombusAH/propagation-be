"""
Tests for Business (Network) creation and Store registration.
"""

import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.skip(reason="Endpoint POST /api/v1/network does not exist")
@pytest.mark.asyncio
async def test_create_network_and_store(async_client: AsyncClient, normal_user_token_headers: dict):
    # Create Business (Network)
    net_resp = await async_client.post(
        f"{settings.API_V1_STR}/network",
        json={"name": "TestBiz", "slug": "testbiz"},
        headers=normal_user_token_headers,
    )
    assert net_resp.status_code == 200
    net_data = net_resp.json()
    assert net_data["slug"] == "testbiz"
    assert "id" in net_data

    # Create Store under that Business
    store_resp = await async_client.post(
        f"{settings.API_V1_STR}/stores",
        json={"name": "Main Store", "business_id": net_data["id"], "slug": "mainstore"},
        headers=normal_user_token_headers,
    )
    assert store_resp.status_code == 200
    store_data = store_resp.json()
    assert store_data["slug"] == "mainstore"
    assert store_data["business_id"] == net_data["id"]
