"""
Comprehensive tests for RFID Tags router.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient):
    """Test creating a new RFID tag."""
    from app.services.database import get_db

    now = datetime.now(timezone.utc)
    mock_tag = SimpleNamespace(
        id=1,
        epc="E280681000001234",
        product_name="Test Product",
        product_sku="SKU-123",
        price_cents=1000,
        is_paid=False,
        is_active=True,
        tid=None,
        user_memory=None,
        rssi=None,
        antenna_port=None,
        frequency=None,
        pc=None,
        crc=None,
        meta={},
        location=None,
        notes=None,
        store_id=None,
        read_count=1,
        first_seen=now,
        last_seen=now,
        created_at=now,
        updated_at=now,
    )

    async def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def mock_refresh(obj):
            obj.id = 1
            obj.read_count = 1
            obj.is_active = True
            obj.is_paid = False
            obj.first_seen = now
            obj.last_seen = now
            obj.created_at = now
            obj.updated_at = now
            # Copy other attributes from mock_tag if they exist
            for key in ["epc", "product_name", "product_sku", "price_cents", "meta"]:
                if hasattr(mock_tag, key):
                    setattr(obj, key, getattr(mock_tag, key))

        mock_db.refresh = MagicMock(side_effect=mock_refresh)
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.post(
            "/api/v1/tags/",
            json={
                "epc": "E280681000001234",
                "product_name": "Test Product",
                "product_sku": "SKU-123",
                "price_cents": 1000,
            },
        )
        assert response.status_code == 201
        assert response.json()["epc"] == "E280681000001234"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient):
    """Test updating an RFID tag using PUT."""
    from app.services.database import get_db

    tag_id = 1
    now = datetime.now(timezone.utc)
    mock_tag = SimpleNamespace(
        id=tag_id,
        epc="E1",
        product_name="Old",
        product_sku="OLD-SKU",
        price_cents=100,
        is_paid=False,
        is_active=True,
        location=None,
        notes=None,
        user_memory=None,
        meta=None,
        store_id=None,
        tid=None,
        rssi=None,
        antenna_port=None,
        frequency=None,
        pc=None,
        crc=None,
        read_count=1,
        first_seen=now,
        last_seen=now,
        created_at=now,
        updated_at=now,
    )

    async def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        payload = {
            "location": "Aisle 1",
            "notes": "Test notes",
            "user_memory": "FF00",
            "meta": {"test": True},
            "is_active": False,
            "product_name": "New Name",
            "product_sku": "NEW-SKU",
            "price_cents": 2000,
            "store_id": 10,
            "is_paid": True,
        }
        response = await client.put(f"/api/v1/tags/{tag_id}", json=payload)
        assert response.status_code == 200
        assert mock_tag.location == "Aisle 1"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_tag_stats(client: AsyncClient):
    """Test tag statistics endpoint."""
    from app.services.database import get_db

    async def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.count.return_value = 10
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("Zone A", 5)
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = -55.5

        mock_most_scanned = SimpleNamespace(id=1, epc="MOST1", read_count=500)
        mock_db.query.return_value.order_by.return_value.first.return_value = (
            mock_most_scanned
        )

        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        # CORRECT URL IS /stats/summary
        response = await client.get("/api/v1/tags/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_tags"] == 10
    finally:
        app.dependency_overrides.clear()
