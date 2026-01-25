"""
Coverage tests for Users API endpoints.
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.dependencies.auth import get_current_user
from app.db.dependencies import get_db
from app.main import app


# Create a mock user
def create_mock_user(id="u1", role="SUPER_ADMIN"):
    return SimpleNamespace(
        id=id,
        email="test@example.com",
        name="Test User",
        phone="000-000-0000",
        address="Test Address",
        role=role,
        businessId="b1",
        subId=None,
        darkMode=False,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        deletedAt=None,
        latitude=None,
        longitude=None,
        receiveTheftAlerts=False,
    )


@pytest.fixture
def auth_override():
    mock_user = create_mock_user()
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()
    yield
    app.dependency_overrides.clear()


class TestUsersEndpointCoverage:

    @pytest.mark.asyncio
    async def test_get_me(self, client, auth_override):
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_id_self(self, client, auth_override):
        with patch("app.api.v1.endpoints.users.get_user_by_id") as mock_get:
            mock_get.return_value = create_mock_user("u1")
            response = await client.get("/api/v1/users/u1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_by_id_other_admin(self, client, auth_override):
        # Admin viewing someone else
        with patch("app.api.v1.endpoints.users.get_user_by_id") as mock_get:
            mock_get.return_value = create_mock_user("u2")
            response = await client.get("/api/v1/users/u2")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_by_id_forbidden(self, client):
        # Regular user viewing someone else
        mock_user = create_mock_user("u1", role="CUSTOMER")
        app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            response = await client.get("/api/v1/users/u2")
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client, auth_override):
        with patch("app.api.v1.endpoints.users.get_user_by_id") as mock_get:
            mock_get.return_value = None
            response = await client.get("/api/v1/users/MISSING")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_user_forbidden_role(self, client, auth_override):
        # CUSTOMER cannot create users
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(role="CUSTOMER")
        try:
            payload = {
                "email": "n@example.com",
                "password": "password123",
                "name": "n",
                "role": "EMPLOYEE",
                "phone": "0",
                "address": "a",
                "businessId": "b",
            }
            response = await client.post("/api/v1/users/", json=payload)
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_user_invalid_role_target(self, client, auth_override):
        # STORE_MANAGER cannot create NETWORK_MANAGER
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(role="STORE_MANAGER")
        try:
            payload = {
                "email": "n@example.com",
                "password": "password123",
                "name": "n",
                "role": "NETWORK_MANAGER",
                "phone": "0",
                "address": "a",
                "businessId": "b",
            }
            response = await client.post("/api/v1/users/", json=payload)
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client, auth_override):
        with patch("app.api.v1.endpoints.users.create_user") as mock_create:
            mock_create.side_effect = Exception("Unique constraint failed")
            payload = {
                "email": "dup@example.com",
                "password": "password123",
                "name": "n",
                "role": "CUSTOMER",
                "phone": "0",
                "address": "a",
                "businessId": "b",
            }
            response = await client.post("/api/v1/users/", json=payload)
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_users_root(self, client):
        response = await client.get("/api/v1/users/")
        assert response.status_code == 200
        assert response.json()["message"] == "Users endpoint"

    @pytest.mark.asyncio
    async def test_create_user_success(self, client, auth_override):
        with patch("app.api.v1.endpoints.users.create_user") as mock_create:
            mock_create.return_value = create_mock_user("u-new")
            payload = {
                "email": "new@example.com",
                "password": "password123",
                "name": "New User",
                "role": "CUSTOMER",
                "phone": "000",
                "address": "Addr",
                "businessId": "b1",
            }
            response = await client.post("/api/v1/users/", json=payload)
            assert response.status_code == 201
            assert response.json()["id"] == "u-new"
