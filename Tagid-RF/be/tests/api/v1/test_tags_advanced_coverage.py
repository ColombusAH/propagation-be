import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_list_tags_advanced_filters(client: AsyncClient):
    """Test list_tags with various filter combinations (line 225+)."""
    # Filter by active and not active
    res = await client.get("/api/v1/tags/?is_active=false")
    assert res.status_code == 200
    
    # Filter by search that matches nothing
    res = await client.get("/api/v1/tags/?search=NON_EXISTENT_EPC_12345")
    assert res.status_code == 200
    assert len(res.json()) == 0
    
    # Pagination
    res = await client.get("/api/v1/tags/?page=1&page_size=10")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_create_tag_full_metadata(client: AsyncClient):
    """Test creating a tag with all optional fields to cover update/create branches."""
    epc = "EPC" + uuid.uuid4().hex[:20].upper()
    data = {
        "epc": epc,
        "rssi": -40,
        "antenna_port": 1,
        "frequency": 915.5,
        "location": "Warehouse",
        "tid": "TID123",
        "pc": "PC123",
        "crc": "CRC123",
        "user_memory": "MEM123",
        "product_name": "Test Product",
        "product_sku": "SKU123",
        "price_cents": 100,
        "store_id": 1,
        "is_paid": True,
        "meta": {"key": "value"}
    }
    # Initial create
    res1 = await client.post("/api/v1/tags/", json=data)
    assert res1.status_code == 201
    
    # Update with some nulls to test None checks
    data["rssi"] = None
    data["location"] = None
    res2 = await client.post("/api/v1/tags/", json=data)
    assert res2.status_code == 201
