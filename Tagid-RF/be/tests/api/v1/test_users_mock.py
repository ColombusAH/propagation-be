"""
Mock-based tests for user endpoints (no DB required).
"""

from unittest.mock import AsyncMock, patch
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.deps import get_current_active_user
from tests.mock_utils import MockModel

client = TestClient(app)


def create_mock_user(
    id="user1", email="test@example.com", name="Test User", role="CUSTOMER", businessId="biz123"
):
    """Create a mock user with all required fields (and more) for Pydantic validation."""
    return MockModel(
        id=id,
        email=email,
        name=name,
        role=role,
        businessId=businessId,
        phone="1234567890",
        address="Test Address",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )


def override_user(user):
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_active_user] = lambda: user


class TestUsersEndpointsMock:
    """Tests for users endpoints using mocks."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    @patch("app.api.v1.endpoints.users.get_user_by_id", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.users.get_db")
    def test_get_user_self(self, mock_get_db, mock_crud_get):
        """Test getting own user profile."""
        mock_user = create_mock_user(id="user1", name="Test User")
        override_user(mock_user)

        mock_crud_get.return_value = mock_user

        response = client.get("/api/v1/users/user1")
        assert response.status_code == 200
        assert response.json()["name"] == "Test User"

    @patch("app.api.v1.endpoints.users.get_user_by_id", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.users.get_db")
    def test_get_user_other_as_admin(self, mock_get_db, mock_crud_get):
        """Test getting other profile as admin."""
        admin_user = create_mock_user(id="admin1", role="SUPER_ADMIN")
        override_user(admin_user)

        target_user = create_mock_user(id="user2", name="Target", role="CUSTOMER")

        mock_crud_get.return_value = target_user

        response = client.get("/api/v1/users/user2")
        assert response.status_code == 200
        assert response.json()["name"] == "Target"

    @patch("app.api.v1.endpoints.users.get_user_by_id", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.users.get_db")
    def test_get_user_other_forbidden(self, mock_get_db, mock_crud_get):
        """Test getting other profile as normal user (forbidden)."""
        user = create_mock_user(id="user1", role="CUSTOMER")
        override_user(user)

        response = client.get("/api/v1/users/user2")
        assert response.status_code == 403

    @patch("app.api.v1.endpoints.users.create_user", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.users.get_db")
    def test_create_user_success(self, mock_get_db, mock_crud_create):
        """Test creating a new user (admin)."""
        admin = create_mock_user(id="admin1", role="SUPER_ADMIN")
        override_user(admin)

        new_user = create_mock_user(
            id="new1", email="new@example.com", name="New User", role="CUSTOMER"
        )
        mock_crud_create.return_value = new_user

        payload = {
            "email": "new@example.com",
            "password": "password",
            "name": "New User",
            "role": "CUSTOMER",
            "phone": "0501234567",
            "address": "Tel Aviv",
            "businessId": "biz123",
        }

        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        assert response.json()["email"] == "new@example.com"

    @patch("app.api.v1.endpoints.users.create_user", new_callable=AsyncMock)
    @patch("app.api.v1.endpoints.users.get_db")
    def test_create_user_forbidden(self, mock_get_db, mock_crud_create):
        """Test creating user without permissions."""
        user = create_mock_user(id="user1", role="CUSTOMER")
        override_user(user)

        payload = {
            "email": "new@example.com",
            "password": "password",
            "name": "New User",
            "role": "CUSTOMER",
            "phone": "0501234567",
            "address": "Tel Aviv",
            "businessId": "biz123",
        }

        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 403
