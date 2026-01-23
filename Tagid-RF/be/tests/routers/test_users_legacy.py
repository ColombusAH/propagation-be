"""
Tests for Users Router to increase coverage.
Covers list, create, get, update, delete, and store assignment.
Uses a dedicated FastAPI instance to avoid conflicts with Prisma routers.
"""

from unittest.mock import MagicMock, patch

import pytest
from app.models.store import Store, User
from app.routers.users import router
from app.services.database import get_db
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    return db, mock_query


@pytest.fixture
async def client(test_app, mock_db):
    test_app.dependency_overrides[get_db] = lambda: mock_db[0]
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac
    test_app.dependency_overrides.clear()


def _create_mock_user(id=1, email="test@example.com"):
    user = MagicMock(spec=User)
    user.id = id
    user.name = "Test User"
    user.email = email
    user.phone = "123456"
    user.role = "SELLER"
    user.store_id = 1
    user.is_active = True
    return user


@pytest.mark.asyncio
async def test_list_users_with_filters(client: AsyncClient, mock_db):
    """Test listing users with search filters."""
    db, mock_query = mock_db
    mock_user = _create_mock_user()
    mock_query.all.return_value = [mock_user]

    mock_store = MagicMock(spec=Store)
    mock_store.name = "Store A"
    mock_query.first.return_value = mock_store

    response = await client.get("/users?role=SELLER&store_id=1&is_active=true")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, mock_db):
    """Test successful user creation."""
    db, mock_query = mock_db
    mock_query.first.return_value = None  # Email available

    mock_user = _create_mock_user(id=10, email="new@example.com")
    with patch("app.routers.users.User", return_value=mock_user):
        user_data = {"name": "New", "email": "new@example.com", "role": "SELLER"}
        response = await client.post("/users", json=user_data)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_user_invalid_role(client: AsyncClient, mock_db):
    """Test invalid role exception."""
    db, mock_query = mock_db
    mock_query.first.return_value = None

    user_data = {"name": "X", "email": "a@b.com", "role": "INVALID"}
    response = await client.post("/users", json=user_data)
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_by_id_success(client: AsyncClient, mock_db):
    """Test get user by ID with store enrichment."""
    db, mock_query = mock_db
    user = _create_mock_user(id=1)
    mock_store = MagicMock(spec=Store)
    mock_store.name = "Store A"

    mock_query.first.side_effect = [user, mock_store]

    response = await client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["store_name"] == "Store A"


@pytest.mark.asyncio
async def test_update_user_full(client: AsyncClient, mock_db):
    """Test full update logic and fix validation issues."""
    db, mock_query = mock_db
    user = _create_mock_user()

    # Store mock for enrichment after update
    mock_store = MagicMock(spec=Store)
    mock_store.name = "Store B"

    # first() calls: 1. find user, 2. check email, 3. store name enrichment
    mock_query.first.side_effect = [user, None, mock_store]

    update_data = {
        "name": "Updated",
        "email": "updated@ex.com",
        "is_active": False,
        "role": "ADMIN",
        "store_id": 2,
    }
    response = await client.put("/users/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["is_active"] is False
    assert data["store_name"] == "Store B"


@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient, mock_db):
    """Test delete logic."""
    db, mock_query = mock_db
    user = _create_mock_user()
    mock_query.first.return_value = user

    response = await client.delete("/users/1")
    assert response.status_code == 204
    assert user.is_active is False
    assert db.commit.called


@pytest.mark.asyncio
async def test_assign_store_errors(client: AsyncClient, mock_db):
    """Test assign store edge cases."""
    db, mock_query = mock_db

    # Case 1: User not found
    mock_query.first.return_value = None
    response = await client.post("/users/1/assign-store", json={"store_id": 10})
    assert response.status_code == 404

    # Case 2: Store not found
    user = _create_mock_user()
    mock_query.first.side_effect = [user, None]
    response = await client.post("/users/1/assign-store", json={"store_id": 999})
    assert response.status_code == 404
    assert "Store not found" in response.json()["detail"]
