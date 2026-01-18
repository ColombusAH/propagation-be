"""
Tests for Stores Router to increase coverage.
Covers list, create, get, and update functionality.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.models.store import Store, User
from app.routers.stores import router
from app.services.database import get_db


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    # Chain methods to return the same mock_query
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    return db, mock_query


@pytest.fixture
async def client(test_app, mock_db):
    test_app.dependency_overrides[get_db] = lambda: mock_db[0]
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac
    test_app.dependency_overrides.clear()


def _create_mock_store(id=1, name="Main Store"):
    store = MagicMock(spec=Store)
    store.id = id
    store.name = name
    store.address = "Tel Aviv"
    store.phone = "123456"
    store.is_active = True
    return store


@pytest.mark.asyncio
async def test_list_stores(client: AsyncClient, mock_db):
    """Test listing active stores with enrichment."""
    db, mock_query = mock_db
    mock_query.all.return_value = [_create_mock_store()]

    # Enrichment: Count sellers and find manager
    mock_query.count.return_value = 5

    # Return a manager with a name to satisfy StoreResponse
    mock_manager = MagicMock(spec=User)
    mock_manager.name = "John Manager"
    mock_query.first.return_value = mock_manager

    response = await client.get("/stores?is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["manager_name"] == "John Manager"


@pytest.mark.asyncio
async def test_create_store(client: AsyncClient, mock_db):
    """Test creating a new store."""
    db, mock_query = mock_db

    # After creation, router enriches the response
    mock_query.count.return_value = 0
    mock_query.first.return_value = None

    mock_store = _create_mock_store(id=10, name="New Store")
    with patch("app.routers.stores.Store", return_value=mock_store):
        store_data = {"name": "New Store", "address": "New York"}
        response = await client.post("/stores", json=store_data)

        assert response.status_code == 201
        assert response.json()["id"] == 10


@pytest.mark.asyncio
async def test_get_store_success(client: AsyncClient, mock_db):
    """Test getting a store by ID."""
    db, mock_query = mock_db
    store = _create_mock_store()

    # first() calls: 1. find store, 2. enrichment manager name
    mock_query.first.side_effect = [store, None]
    mock_query.count.return_value = 1

    response = await client.get("/stores/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_update_store_success(client: AsyncClient, mock_db):
    """Test updating store details."""
    db, mock_query = mock_db
    store = _create_mock_store()

    # first() calls: 1. find store to update, 2. enrichment manager name
    mock_query.first.side_effect = [store, None]
    mock_query.count.return_value = 2

    update_data = {"name": "Updated Name", "is_active": False}
    response = await client.put("/stores/1", json=update_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
