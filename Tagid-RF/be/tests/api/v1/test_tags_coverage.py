import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_get_tag_not_found(client: AsyncClient):
    """Test getting a non-existent tag."""
    response = await client.get("/api/v1/tags/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_tag_by_epc_not_found(client: AsyncClient):
    """Test getting a non-existent tag by EPC."""
    response = await client.get("/api/v1/tags/epc/NONEXISTENT")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_tag_not_found(client: AsyncClient):
    """Test updating a non-existent tag."""
    response = await client.put("/api/v1/tags/999999", json={"location": "nowhere"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient):
    """Test deleting (soft delete) a tag."""
    # Create
    epc = "E2" + uuid.uuid4().hex[:22].upper()
    create_res = await client.post("/api/v1/tags/", json={"epc": epc})
    tag_id = create_res.json()["id"]
    
    # Delete
    del_res = await client.delete(f"/api/v1/tags/{tag_id}")
    assert del_res.status_code == 204
    
    get_res = await client.get(f"/api/v1/tags/{tag_id}")
    assert get_res.status_code == 200
    assert get_res.json()["is_active"] is False

@pytest.mark.asyncio
async def test_delete_tag_not_found(client: AsyncClient):
    """Test deleting a non-existent tag."""
    response = await client.delete("/api/v1/tags/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_tags_filtering(client: AsyncClient):
    """Test listing tags with filters."""
    # Create active and inactive tags
    epc1 = "E2" + uuid.uuid4().hex[:22].upper()
    await client.post("/api/v1/tags/", json={"epc": epc1}) # Active by default
    
    res = await client.get("/api/v1/tags/?is_active=true")
    assert res.status_code == 200
    tags = res.json()
    assert len(tags) >= 1
    
    # Test search
    res_search = await client.get(f"/api/v1/tags/?search={epc1}")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1
    assert res_search.json()[0]["epc"] == epc1

@pytest.mark.asyncio
async def test_create_existing_tag_update(client: AsyncClient):
    """Test sending POST for existing tag updates it."""
    epc = "E2" + uuid.uuid4().hex[:22].upper()
    # First create
    res1 = await client.post("/api/v1/tags/", json={"epc": epc, "location": "Loc1"})
    assert res1.status_code == 201
    
    # Second create (update)
    res2 = await client.post("/api/v1/tags/", json={"epc": epc, "location": "Loc2"})
    assert res2.status_code == 201 
    
    # Check update
    get_res = await client.get(f"/api/v1/tags/epc/{epc}")
    assert get_res.json()["location"] == "Loc2"
    assert get_res.json()["read_count"] >= 2
