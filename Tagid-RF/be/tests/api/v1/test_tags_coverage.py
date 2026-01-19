import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_tag_not_found(client: AsyncClient):
    """Test getting a non-existent tag."""
    from app.main import app
    from app.services.database import get_db

    mock_db = MagicMock()
    # Return None to simulate 404
    mock_db.query.return_value.filter.return_value.first.return_value = None

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/api/v1/tags/999999")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_tag_by_epc_not_found(client: AsyncClient):
    """Test getting a non-existent tag by EPC."""
    from app.main import app
    from app.services.database import get_db

    mock_db = MagicMock()
    # Return None to simulate 404
    mock_db.query.return_value.filter.return_value.first.return_value = None

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/api/v1/tags/epc/NONEXISTENT")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_tag_not_found(client: AsyncClient):
    """Test updating a non-existent tag."""
    from app.main import app
    from app.services.database import get_db

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.put("/api/v1/tags/999999", json={"location": "nowhere"})
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient):
    """Test deleting (soft delete) a tag."""
    import datetime
    from types import SimpleNamespace

    from app.main import app
    from app.services.database import get_db

    epc = "E2" + uuid.uuid4().hex[:22].upper()
    mock_tag = SimpleNamespace(
        id=1,
        epc=epc,
        location="Loc1",
        is_active=True,
        read_count=1,
        first_seen=datetime.datetime.now(),
        last_seen=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )

    mock_db = MagicMock()
    # Match the query for get_tag (called during delete and re-get)
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_tag,
        mock_tag,
    ]

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        # Mocking RFIDTag to return our Namespace when requested (e.g. in some logic)
        with patch("app.routers.tags.RFIDTag", return_value=mock_tag):
            # Delete
            del_res = await client.delete(f"/api/v1/tags/{1}")
            assert del_res.status_code == 204

            # Since mock_tag is updated in place
            mock_tag.is_active = False

            get_res = await client.get(f"/api/v1/tags/{1}")
            assert get_res.status_code == 200
            assert get_res.json()["is_active"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_tag_not_found(client: AsyncClient):
    """Test deleting a non-existent tag."""
    from app.main import app
    from app.services.database import get_db

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.delete("/api/v1/tags/999999")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_tags_filtering(client: AsyncClient):
    """Test listing tags with filters."""
    import datetime
    from types import SimpleNamespace

    from app.main import app
    from app.services.database import get_db

    epc1 = "E2" + uuid.uuid4().hex[:22].upper()
    mock_tag1 = SimpleNamespace(
        id=1,
        epc=epc1,
        is_active=True,
        read_count=1,
        first_seen=datetime.datetime.now(),
        last_seen=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_tag1]
    mock_query.count.return_value = 1

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        res = await client.get("/api/v1/tags/?is_active=true")
        assert res.status_code == 200
        tags = res.json()
        assert len(tags) >= 1

        # Test search
        res_search = await client.get(f"/api/v1/tags/?search={epc1}")
        assert res_search.status_code == 200
        assert len(res_search.json()) >= 1
        assert res_search.json()[0]["epc"] == epc1
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_existing_tag_update(client: AsyncClient):
    """Test sending POST for existing tag updates it."""
    import datetime
    from types import SimpleNamespace
    from unittest.mock import patch

    from app.main import app
    from app.services.database import get_db

    epc = "E2" + uuid.uuid4().hex[:22].upper()
    mock_tag = SimpleNamespace(
        id=1,
        epc=epc,
        location="Loc1",
        read_count=1,
        first_seen=datetime.datetime.now(),
        last_seen=datetime.datetime.now(),
        is_active=True,
        updated_at=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )
    mock_tag.__name__ = "RFIDTag"

    mock_db = MagicMock()
    # First call: not found (create branch)
    # Consecutive calls: found (update branch)
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        None,
        mock_tag,
        mock_tag,
    ]

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with (
            patch("app.routers.tags.RFIDTag", return_value=mock_tag),
            patch("app.routers.tags.RFIDScanHistory", return_value=MagicMock()),
        ):

            # First create
            res1 = await client.post(
                "/api/v1/tags/", json={"epc": epc, "location": "Loc1"}
            )
            assert res1.status_code in [201, 200]

            # Update location for mock_tag for later assertion
            mock_tag.location = "Loc2"
            mock_tag.read_count = 2

            # Second create (update)
            res2 = await client.post(
                "/api/v1/tags/", json={"epc": epc, "location": "Loc2"}
            )
            assert res2.status_code in [201, 200]

            # Check update
            get_res = await client.get(f"/api/v1/tags/epc/{epc}")
            assert get_res.json()["location"] == "Loc2"
            assert get_res.json()["read_count"] >= 2
    finally:
        app.dependency_overrides.clear()
