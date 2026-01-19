"""
Tests for creating and retrieving RfidTag (product tag) records via API.
"""

import pytest
from app.core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_rfid_tag(
    async_client: AsyncClient, normal_user_token_headers: dict
):
    tag_payload = {
        "epc": "EPC-TEST-001",
        "productId": "SKU-001",
        "productDescription": "Test Product",
        "isPaid": False,
        "status": "ACTIVE",
    }
    resp = await async_client.post(
        f"{settings.API_V1_STR}/tags",
        json=tag_payload,
        headers=normal_user_token_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    for key, value in tag_payload.items():
        assert data[key] == value
    assert "id" in data
