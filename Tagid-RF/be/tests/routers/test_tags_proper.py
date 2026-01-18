"""
Tests for Tags Router to improve code coverage.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from app.main import app
from app.services.database import get_db


def make_mock_tag(**kwargs):
    """Create a mock tag with all required fields."""
    now = datetime.now(timezone.utc)
    defaults = {
        "id": 1,
        "epc": "E2806810000000001234ABCD",
        "tid": None,
        "user_memory": None,
        "rssi": -50.0,
        "antenna_port": 1,
        "frequency": 915.25,
        "pc": None,
        "crc": None,
        "meta": None,
        "location": "Warehouse",
        "notes": None,
        "product_name": None,
        "product_sku": None,
        "price_cents": None,
        "store_id": None,
        "is_paid": False,
        "paid_at": None,
        "read_count": 1,
        "is_active": True,
        "first_seen": now,
        "last_seen": now,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    tag = MagicMock()
    for k, v in defaults.items():
        setattr(tag, k, v)
    return tag


@pytest.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db():
    mock = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_create_or_update_tag_new(ac, mock_db):
    """Test creating a new tag."""
    mock_db.query().filter().first.return_value = None

    # Mock the add to populate the tag with an id
    def add_side_effect(obj):
        if hasattr(obj, "epc"):
            obj.id = 1
            obj.read_count = 1
            obj.is_active = True
            obj.first_seen = datetime.now(timezone.utc)
            obj.last_seen = datetime.now(timezone.utc)
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

    mock_db.add.side_effect = add_side_effect

    tag_data = {"epc": "E2806810000000001234ABCD", "rssi": -45, "antenna_port": 1}

    response = await ac.post("/api/v1/tags/", json=tag_data)

    assert response.status_code == 201
    assert mock_db.add.call_count >= 1
    assert mock_db.commit.call_count >= 1


@pytest.mark.asyncio
async def test_create_or_update_tag_existing(ac, mock_db):
    """Test updating an existing tag via POST."""
    existing_tag = make_mock_tag(read_count=1, rssi=-50, is_paid=False)
    mock_db.query().filter().first.return_value = existing_tag

    tag_data = {"epc": "E2806810000000001234ABCD", "rssi": -40, "is_paid": True}

    response = await ac.post("/api/v1/tags/", json=tag_data)

    assert response.status_code == 201
    assert existing_tag.read_count == 2
    assert existing_tag.rssi == -40
    assert existing_tag.is_paid is True


@pytest.mark.asyncio
async def test_list_tags_with_filters(ac, mock_db):
    """Test listing tags with search and activity filters."""
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    await ac.get("/api/v1/tags/?is_active=true&search=test&page=2&page_size=20")

    assert mock_db.query.called


@pytest.mark.asyncio
async def test_get_tag_endpoints(ac, mock_db):
    """Test GET /tags/{id} and /tags/epc/{epc}."""
    tag = make_mock_tag(id=1, epc="EPC123")
    mock_db.query().filter().first.return_value = tag

    res1 = await ac.get("/api/v1/tags/1")
    assert res1.status_code == 200
    assert res1.json()["epc"] == "EPC123"

    res2 = await ac.get("/api/v1/tags/epc/EPC123")
    assert res2.status_code == 200

    mock_db.query().filter().first.return_value = None
    res3 = await ac.get("/api/v1/tags/999")
    assert res3.status_code == 404


@pytest.mark.asyncio
async def test_update_tag_put(ac, mock_db):
    """Test PUT /tags/{id} for partial updates."""
    tag = make_mock_tag(location="Old Loc")
    mock_db.query().filter().first.return_value = tag

    response = await ac.put("/api/v1/tags/1", json={"location": "New Loc", "is_paid": True})

    assert response.status_code == 200
    assert tag.location == "New Loc"
    assert tag.is_paid is True


@pytest.mark.asyncio
async def test_delete_tag_soft(ac, mock_db):
    """Test DELETE /tags/{id} performs soft delete."""
    tag = make_mock_tag(is_active=True)
    mock_db.query().filter().first.return_value = tag

    response = await ac.delete("/api/v1/tags/1")

    assert response.status_code == 204
    assert tag.is_active is False


@pytest.mark.asyncio
async def test_get_recent_scans(ac, mock_db):
    """Test retrieval of recent scan history."""
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    response = await ac.get("/api/v1/tags/recent/scans?hours=48&limit=50")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_tag_stats(ac, mock_db):
    """Test summary statistics endpoint."""
    mock_db.query().count.return_value = 10
    mock_db.query().filter().count.return_value = 5
    mock_db.query().order_by().first.return_value = make_mock_tag(epc="BEST", read_count=100)
    mock_db.query().filter().scalar.return_value = -55.0
    mock_db.query().filter().group_by().all.return_value = [("Warehouse", 10)]

    response = await ac.get("/api/v1/tags/stats/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_tags"] == 10


@pytest.mark.asyncio
async def test_reader_connect_success(ac):
    """Test hardware connect endpoint."""
    with patch("app.services.rfid_reader.rfid_reader_service") as mock_service:
        mock_service.connect = AsyncMock(return_value=True)
        mock_service.get_reader_info = AsyncMock(return_value={"model": "M-200"})
        mock_service.reader_ip = "127.0.0.1"
        mock_service.reader_port = 4001

        res = await ac.post("/api/v1/tags/reader/connect")
        assert res.status_code == 200
        assert res.json()["status"] == "connected"


@pytest.mark.asyncio
async def test_reader_connect_failure(ac):
    """Test hardware connect failure."""
    with patch("app.services.rfid_reader.rfid_reader_service") as mock_service:
        mock_service.connect = AsyncMock(return_value=False)

        res = await ac.post("/api/v1/tags/reader/connect")
        assert res.status_code == 500


@pytest.mark.asyncio
async def test_start_scanning(ac):
    """Test start scanning endpoint."""
    with patch("app.services.rfid_reader.rfid_reader_service") as mock_service:
        mock_service.is_connected = True
        mock_service.start_scanning = AsyncMock()

        res = await ac.post("/api/v1/tags/reader/start-scanning")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_stop_scanning(ac):
    """Test stop scanning endpoint."""
    with patch("app.services.rfid_reader.rfid_reader_service") as mock_service:
        mock_service.stop_scanning = AsyncMock()

        res = await ac.post("/api/v1/tags/reader/stop-scanning")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_disconnect(ac):
    """Test disconnect endpoint."""
    with patch("app.services.rfid_reader.rfid_reader_service") as mock_service:
        mock_service.disconnect = AsyncMock()

        res = await ac.post("/api/v1/tags/reader/disconnect")
        assert res.status_code == 200
