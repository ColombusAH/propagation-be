"""
Tests for Tags API - Basic CRUD operations.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient):
    """Test creating a new RFID tag."""
    epc = "E2" + uuid.uuid4().hex[:22].upper()
    payload = {
        "epc": epc,
        "rssi": -55.5,
        "location": "Test Area",
        "metadata": {"source": "test"},
    }
    response = await client.post("/api/v1/tags/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["epc"] == epc
    assert data["location"] == "Test Area"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient):
    """Test updating tag metadata."""
    # First create a tag
    epc = "E2" + uuid.uuid4().hex[:22].upper()
    create_res = await client.post("/api/v1/tags/", json={"epc": epc})
    tag_id = create_res.json()["id"]

    # Update it
    update_payload = {
        "location": "New Lab",
        "notes": "Updated via test",
        "metadata": {"updated": True},
    }
    response = await client.put(f"/api/v1/tags/{tag_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["location"] == "New Lab"
    assert response.json()["notes"] == "Updated via test"


@pytest.mark.asyncio
async def test_get_tag_stats(client: AsyncClient):
    """Test the stats summary endpoint."""
    response = await client.get("/api/v1/tags/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_tags" in data
    assert "active_tags" in data
