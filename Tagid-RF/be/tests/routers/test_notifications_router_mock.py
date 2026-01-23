"""
Mock-based tests for SQLAlchemy Notifications Router.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.store import Notification, NotificationPreference, User
from app.routers.notifications import router as notifications_router
from app.services.database import get_db

# Create a dedicated app for testing the legacy router
test_app = FastAPI()
test_app.include_router(notifications_router)
client = TestClient(test_app)


class TestNotificationsRouterMock:
    """Tests for legacy notifications router using SQLAlchemy mocks."""

    def teardown_method(self):
        test_app.dependency_overrides.clear()

    def test_get_preferences_defaults(self):
        """Test getting default preferences when none exist."""
        mock_db = MagicMock()
        # Mock query(...).filter(...).all() returning empty list
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = []

        test_app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/notifications/preferences?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Check if UNPAID_EXIT has SMS/Email enabled by default
        unpaid_exit = next(p for p in data if p["notification_type"] == "UNPAID_EXIT")
        assert unpaid_exit["channel_sms"] is True

    def test_get_preferences_existing(self):
        """Test getting existing preferences."""
        mock_db = MagicMock()
        pref = MagicMock(spec=NotificationPreference)
        pref.id = 10
        pref.notification_type = "SALE"
        pref.channel_push = True
        pref.channel_sms = False
        pref.channel_email = False
        pref.store_filter_id = 5

        mock_db.query.return_value.filter.return_value.all.return_value = [pref]

        test_app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/notifications/preferences?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 10
        assert data[0]["notification_type"] == "SALE"

    def test_update_preferences_new(self):
        """Test creating new preferences."""
        mock_db = MagicMock()
        # Mock user exists
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            MagicMock(spec=User),  # user
            None,  # no existing pref
        ]

        # Mock refresh to set an ID on the pref object
        def mock_refresh(obj):
            obj.id = 99

        mock_db.refresh.side_effect = mock_refresh

        test_app.dependency_overrides[get_db] = lambda: mock_db

        payload = [{"notification_type": "SALE", "channel_push": True}]

        response = client.put("/notifications/preferences?user_id=1", json=payload)
        assert response.status_code == 200
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_get_notifications(self):
        """Test retrieving notifications list."""
        mock_db = MagicMock()
        n1 = MagicMock(spec=Notification)
        n1.id = 1
        n1.notification_type = "SALE"
        n1.title = "Title"
        n1.message = "Msg"
        n1.is_read = False
        n1.created_at = datetime(2023, 1, 1)

        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            n1
        ]

        test_app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/notifications?user_id=1&unread_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1

    def test_mark_as_read(self):
        """Test marking notification as read."""
        mock_db = MagicMock()
        notification = MagicMock(spec=Notification)
        mock_db.query.return_value.filter.return_value.first.return_value = notification

        test_app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/notifications/1/read")
        assert response.status_code == 200
        assert notification.is_read is True
        assert mock_db.commit.called

    def test_send_notification(self):
        """Test internal send notification logic."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            MagicMock(spec=User),  # user
            None,  # no pref (use defaults)
        ]

        test_app.dependency_overrides[get_db] = lambda: mock_db

        payload = {
            "user_id": 1,
            "notification_type": "SALE",
            "title": "New Sale",
            "message": "You made a sale!",
        }

        response = client.post("/notifications/send", json=payload)
        assert response.status_code == 201
        assert mock_db.add.called
        assert mock_db.commit.called
        data = response.json()
        assert "push" in data["channels"]
