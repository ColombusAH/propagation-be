"""
Additional integration tests for tag mapping API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_tag_mapping(async_client: AsyncClient, auth_headers):
    """Test creating a new tag mapping."""
    response = await async_client.post(
        "/api/v1/tag-mapping/",
        headers=auth_headers,
        json={
            "epc": "E280116060000020957A3A3B",
            "tid": "E2003412",
            "productName": "Test Product",
            "productDescription": "Test Description",
        },
    )

    # May return 200 or 201 depending on implementation
    assert response.status_code in [200, 201]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_tag_mappings(async_client: AsyncClient, auth_headers):
    """Test listing tag mappings."""
    response = await async_client.get(
        "/api/v1/tag-mapping/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_tag_mapping_by_epc(async_client: AsyncClient, auth_headers):
    """Test getting a tag mapping by EPC."""
    # First create a tag
    create_response = await async_client.post(
        "/api/v1/tag-mapping/",
        headers=auth_headers,
        json={
            "epc": "E280116060000020957A3A3C",
            "tid": "E2003413",
            "productName": "Test Product 2",
        },
    )

    if create_response.status_code in [200, 201]:
        # Then get it
        response = await async_client.get(
            "/api/v1/tag-mapping/E280116060000020957A3A3C",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["epc"] == "E280116060000020957A3A3C"
