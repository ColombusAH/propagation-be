import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tags_advanced_filters(client: AsyncClient):
    """Test list_tags with various filter combinations (line 225+)."""
    from unittest.mock import MagicMock

    from app.main import app
    from app.services.database import get_db

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.count.return_value = 0

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
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
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_tag_full_metadata(client: AsyncClient):
    """Test creating a tag with all optional fields to cover update/create branches."""
    import datetime
    from types import SimpleNamespace
    from unittest.mock import MagicMock, patch

    from app.main import app
    from app.services.database import get_db

    epc = "EPC" + uuid.uuid4().hex[:20].upper()

    mock_tag = SimpleNamespace(
        id=1,
        epc=epc,
        tid="TID123",
        read_count=1,
        first_seen=datetime.datetime.now(),
        last_seen=datetime.datetime.now(),
        rssi=-40,
        antenna_port=1,
        location="Warehouse",
        is_active=True,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )

    mock_db = MagicMock()
    # Mock for "not found" so it creates
    mock_db.query.return_value.filter.return_value.first.return_value = None

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
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
            "meta": {"key": "value"},
        }

        with (
            patch("app.routers.tags.RFIDTag", return_value=mock_tag),
            patch("app.routers.tags.RFIDScanHistory", return_value=MagicMock()),
        ):

            # Initial create
            res1 = await client.post("/api/v1/tags/", json=data)
            assert res1.status_code in [201, 200]

            # For the second call, we want it to "exist" or just be created again
            # To test update branch, mock_db should return mock_tag
            mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

            # Update with some nulls to test None checks
            data["rssi"] = None
            data["location"] = None
            res2 = await client.post("/api/v1/tags/", json=data)
            # Depending on implementation, create_or_update might return 201 or 200
            assert res2.status_code in [201, 200]
    finally:
        app.dependency_overrides.clear()
