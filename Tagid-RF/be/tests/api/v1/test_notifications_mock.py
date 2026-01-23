"""
Mock-based tests for notifications endpoints (no DB required).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.api.dependencies.auth import get_current_user
from app.db.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from tests.mock_utils import MockModel

client = TestClient(app)


def override_user(user):
    app.dependency_overrides[get_current_user] = lambda: user


class TestNotificationsEndpointsMock:
    """Tests for notifications endpoints using mocks."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_get_notification_settings_defaults(self):
        """Test getting settings when no preferences exist (defaults)."""
        mock_user = MockModel(id="user1", darkMode=False)
        override_user(mock_user)

        mock_db = MagicMock()
        mock_db.notificationpreference.find_many = AsyncMock(return_value=[])

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["push"] is True
        assert data["sms"] is False
        assert data["email"] is True
        assert data["darkMode"] is False

    def test_get_notification_settings_custom(self):
        """Test getting settings with existing preferences."""
        mock_user = MockModel(id="user1", darkMode=True)
        override_user(mock_user)

        mock_db = MagicMock()

        # Mock existing preferences
        prefs = [
            MockModel(channelType="PUSH", enabled=False),
            MockModel(channelType="SMS", enabled=True),
        ]
        mock_db.notificationpreference.find_many = AsyncMock(return_value=prefs)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["push"] is False  # Overridden
        assert data["sms"] is True  # Overridden
        assert data["email"] is True  # Default (not in DB)
        assert data["darkMode"] is True

    def test_update_notification_settings(self):
        """Test updating settings (create and update flows)."""
        mock_user = MockModel(id="user1", darkMode=False)
        override_user(mock_user)

        mock_db = MagicMock()

        # 1. Update darkMode
        mock_db.user.update = AsyncMock()

        # 2. Update preferences loop
        existing_pref = MockModel(id="pref1", channelType="PUSH")

        async def mock_find_first(where):
            if where.get("channelType") == "PUSH":
                return existing_pref
            return None

        mock_db.notificationpreference.find_first = AsyncMock(
            side_effect=mock_find_first
        )
        mock_db.notificationpreference.update = AsyncMock()
        mock_db.notificationpreference.create = AsyncMock()

        # 3. Final fetch
        mock_db.user.find_unique = AsyncMock(
            return_value=MockModel(id="user1", darkMode=True)
        )
        mock_db.notificationpreference.find_many = AsyncMock(
            return_value=[
                MockModel(channelType="PUSH", enabled=False),
                MockModel(channelType="SMS", enabled=True),
            ]
        )

        app.dependency_overrides[get_db] = lambda: mock_db

        payload = {"push": False, "sms": True, "darkMode": True}

        response = client.put("/api/v1/notifications/settings", json=payload)
        assert response.status_code == 200
        data = response.json()

        mock_db.user.update.assert_awaited_once()
        mock_db.notificationpreference.update.assert_awaited_once()
        mock_db.notificationpreference.create.assert_awaited_once()

        assert data["darkMode"] is True
        assert data["push"] is False
        assert data["sms"] is True
