import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient):
    """Test soft deleting a tag."""
    # Create tag
    epc = "DELETE-ME-123"
    create_res = await client.post("/api/v1/tags/", json={"epc": epc})
    tag_id = create_res.json()["id"]
    
    # Delete it
    response = await client.delete(f"/api/v1/tags/{tag_id}")
    assert response.status_code == 204
    
    # Verify it's inactive
    get_res = await client.get(f"/api/v1/tags/{tag_id}")
    assert get_res.json()["is_active"] is False

@pytest.mark.asyncio
async def test_get_recent_scans(client: AsyncClient):
    """Test retrieving recent scan history."""
    response = await client.get("/api/v1/tags/recent/scans?hours=1&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
