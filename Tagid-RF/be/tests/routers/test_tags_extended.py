"""
Extended tests for Tags Router to reach 90% coverage.
Covers complex filtering, tag updates, and scan history.
"""

import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.rfid_tag import RFIDScanHistory, RFIDTag
from app.services.database import get_db


def _create_mock_tag_obj(id=1, epc="EPC123"):
    tag = MagicMock(spec=RFIDTag)
    tag.id = id
    tag.epc = epc
    tag.tid = "TID123"
    tag.read_count = 1
    tag.first_seen = datetime.now(timezone.utc)
    tag.last_seen = datetime.now(timezone.utc)
    tag.rssi = -60.0
    tag.antenna_port = 1
    tag.frequency = 915.0
    tag.pc = "3000"
    tag.crc = "AAAA"
    tag.user_memory = "MEM"
    tag.location = "Warehouse"
    tag.notes = "Notes"
    tag.is_active = True
    tag.created_at = datetime.now(timezone.utc)
    tag.updated_at = datetime.now(timezone.utc)
    tag.is_paid = False
    tag.product_name = "Product"
    tag.product_sku = "SKU"
    tag.price_cents = 1000
    tag.store_id = 1
    tag.meta = {}  # Pydantic looks for 'meta' for RFIDTagResponse
    tag.metadata = {}
    return tag


def _create_mock_history_obj():
    hist = MagicMock(spec=RFIDScanHistory)
    hist.id = 1
    hist.epc = "EPC123"
    hist.tid = "TID123"
    hist.rssi = -60.0
    hist.antenna_port = 1
    hist.frequency = 915.0
    hist.location = "Warehouse"
    hist.reader_id = "READER1"
    hist.metadata = {}  # Pydantic looks for 'metadata' (alias) for RFIDScanHistoryResponse
    hist.meta = {}
    hist.scanned_at = datetime.now(timezone.utc)
    return hist


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    return db, mock_query


@pytest.fixture
def override_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db[0]
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_list_tags_with_filters(client: AsyncClient, mock_db, override_db):
    """Test listing tags with search and activity filters."""
    db, mock_query = mock_db
    mock_query.count.return_value = 1
    mock_query.all.return_value = [_create_mock_tag_obj()]

    response = await client.get("/api/v1/tags/?search=TEST&is_active=true&page=2&page_size=10")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_create_tag_new(client: AsyncClient, mock_db, override_db):
    """Test creating a brand new tag."""
    db, mock_query = mock_db
    mock_query.first.return_value = None

    new_tag = _create_mock_tag_obj(epc="NEW_EPC")

    with (
        patch("app.routers.tags.RFIDTag", return_value=new_tag),
        patch("app.routers.tags.RFIDScanHistory", return_value=MagicMock()),
    ):
        tag_data = {"epc": "NEW_EPC", "product_name": "New Item", "price_cents": 1000}

        response = await client.post("/api/v1/tags/", json=tag_data)

        assert response.status_code == 201
        assert response.json()["epc"] == "NEW_EPC"


@pytest.mark.asyncio
async def test_create_tag_existing(client: AsyncClient, mock_db, override_db):
    """Test scanning an existing tag (updates read count)."""
    db, mock_query = mock_db
    existing_tag = _create_mock_tag_obj(epc="EXISTING")
    existing_tag.read_count = 5
    mock_query.first.return_value = existing_tag

    tag_data = {"epc": "EXISTING", "rssi": -50}

    response = await client.post("/api/v1/tags/", json=tag_data)

    assert response.status_code == 201
    assert existing_tag.read_count == 6


@pytest.mark.asyncio
async def test_get_tag_by_epc_success(client: AsyncClient, mock_db, override_db):
    """Test lookup by EPC."""
    db, mock_query = mock_db
    tag = _create_mock_tag_obj(epc="EPC123")
    mock_query.first.return_value = tag

    response = await client.get("/api/v1/tags/epc/EPC123")
    assert response.status_code == 200
    assert response.json()["epc"] == "EPC123"


@pytest.mark.asyncio
async def test_update_tag_partial(client: AsyncClient, mock_db, override_db):
    """Test partial tag update."""
    db, mock_query = mock_db
    tag = _create_mock_tag_obj()
    mock_query.first.return_value = tag

    update_data = {"location": "New Location", "is_paid": True}
    response = await client.put("/api/v1/tags/1", json=update_data)

    assert response.status_code == 200
    assert tag.location == "New Location"
    assert tag.is_paid is True


@pytest.mark.asyncio
async def test_get_recent_scans(client: AsyncClient, mock_db, override_db):
    """Test history endpoint."""
    db, mock_query = mock_db
    mock_query.all.return_value = [_create_mock_history_obj()]

    response = await client.get("/api/v1/tags/recent/scans?hours=2&limit=10")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_tag_stats(client: AsyncClient, mock_db, override_db):
    """Test summary stats logic."""
    db, mock_query = mock_db

    # Mock multiple counts
    mock_query.count.side_effect = [100, 90, 500, 50]

    # most_scanned_tag (.first)
    most_scanned = _create_mock_tag_obj(epc="MOST")
    most_scanned.read_count = 1000
    mock_query.first.return_value = most_scanned

    # average_rssi (.scalar)
    mock_query.scalar.return_value = -45.5

    # location distribution (.all)
    mock_query.all.return_value = [("Location A", 40), ("Location B", 60)]

    response = await client.get("/api/v1/tags/stats/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_tags"] == 100
    assert data["active_tags"] == 90
    assert data["scans_today"] == 500
    assert data["most_scanned_tag"]["epc"] == "MOST"
    assert data["tags_by_location"]["Location A"] == 40


@pytest.mark.asyncio
async def test_delete_tag_success(client: AsyncClient, mock_db, override_db):
    """Test soft delete."""
    db, mock_query = mock_db
    tag = _create_mock_tag_obj()
    mock_query.first.return_value = tag

    response = await client.delete("/api/v1/tags/1")
    assert response.status_code == 204
    assert tag.is_active is False
    assert db.commit.called


@pytest.mark.asyncio
async def test_reader_connect_success(client: AsyncClient):
    """Test reader connect endpoint."""
    with (
        patch("app.services.rfid_reader.rfid_reader_service.connect", return_value=True),
        patch(
            "app.services.rfid_reader.rfid_reader_service.get_reader_info",
            new_callable=AsyncMock,
            return_value={"model": "MOCK"},
        ),
    ):
        response = await client.post("/api/v1/tags/reader/connect")
        assert response.status_code == 200
        assert response.json()["status"] == "connected"


@pytest.mark.asyncio
async def test_reader_start_scanning_failure(client: AsyncClient):
    """Test scanning failure when not connected."""
    with patch("app.services.rfid_reader.rfid_reader_service.is_connected", False):
        response = await client.post("/api/v1/tags/reader/start-scanning")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_reader_read_single_success(client: AsyncClient):
    """Test single tag read."""
    mock_tag = {"epc": "LIVE01", "rssi": -40}
    with (
        patch("app.services.rfid_reader.rfid_reader_service.is_connected", True),
        patch(
            "app.services.rfid_reader.rfid_reader_service.read_single_tag",
            new_callable=AsyncMock,
            return_value=mock_tag,
        ),
    ):
        response = await client.post("/api/v1/tags/reader/read-single")
        assert response.status_code == 200
        assert response.json()["tag"]["epc"] == "LIVE01"


@pytest.mark.asyncio
async def test_reader_stop_scanning_success(client: AsyncClient):
    """Test stopping the reader."""
    with patch(
        "app.services.rfid_reader.rfid_reader_service.stop_scanning", new_callable=AsyncMock
    ):
        response = await client.post("/api/v1/tags/reader/stop-scanning")
        assert response.status_code == 200
        assert response.json()["status"] == "stopped"


@pytest.mark.asyncio
async def test_get_reader_status_connected(client: AsyncClient):
    """Test status endpoint when connected."""
    mock_info = {"model": "MOCK-READER", "firmware": "1.0"}
    from app.services.rfid_reader import rfid_reader_service

    with (
        patch(
            "app.services.rfid_reader.rfid_reader_service.get_reader_info",
            new_callable=AsyncMock,
            return_value=mock_info,
        ),
        patch.object(rfid_reader_service, "is_connected", True, create=True),
        patch.object(rfid_reader_service, "is_scanning", True, create=True),
        patch.object(rfid_reader_service, "connection_type", "tcp", create=True),
        patch.object(rfid_reader_service, "reader_ip", "192.168.1.100", create=True),
        patch.object(rfid_reader_service, "reader_port", 4001, create=True),
    ):

        response = await client.get("/api/v1/tags/reader/status")
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["scanning"] is True


@pytest.mark.asyncio
async def test_reader_connect_failure(client: AsyncClient):
    """Test connection failure handling."""
    with patch(
        "app.services.rfid_reader.rfid_reader_service.connect",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = await client.post("/api/v1/tags/reader/connect")
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_live_recent_not_running(client: AsyncClient):
    """Test live stats when listener is not available."""
    # Use side_effect to raise ImportError when tag_listener_server is imported
    import builtins

    original_import = builtins.__import__

    def mocked_import(name, *args, **kwargs):
        if name == "tag_listener_server":
            raise ImportError("Mocked import error")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mocked_import):
        response = await client.get("/api/v1/tags/live/recent")
        assert response.status_code == 200
        assert "message" in response.json()
        assert (
            "not available" in response.json()["message"]
            or "not running" in response.json()["message"]
        )


@pytest.mark.asyncio
async def test_get_tag_by_id_success(client: AsyncClient, mock_db, override_db):
    """Test get_tag by ID."""
    db, mock_query = mock_db
    tag = _create_mock_tag_obj()
    mock_query.first.return_value = tag

    response = await client.get("/api/v1/tags/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
