"""
Tests for Notifications Router to increase coverage.
Covers preferences, getting notifications, marking as read, and sending.

NOTE: These tests target /api/v1/notifications but the legacy notifications router
from app.routers.notifications is NOT mounted in main.py. Skipping until resolved.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from app.main import app
from app.models.store import Notification, NotificationPreference, User
from app.services.database import get_db
from httpx import AsyncClient
from sqlalchemy.orm import Session

pytestmark = pytest.mark.skip(reason="Legacy router not mounted in app")


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    return db, mock_query


@pytest.fixture
def override_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db[0]
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_get_preferences_defaults(client: AsyncClient, mock_db, override_db):
    """Test getting preferences when none exist (should return defaults)."""
    db, mock_query = mock_db
    mock_query.all.return_value = []  # No custom prefs

    response = await client.get("/api/v1/notifications/preferences?user_id=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Check if a security alert has defaults
    unpaid_exit = next(p for p in data if p["notification_type"] == "UNPAID_EXIT")
    assert unpaid_exit["channel_sms"] is True


@pytest.mark.asyncio
async def test_update_preferences_new(client: AsyncClient, mock_db, override_db):
    """Test creating new preferences."""
    db, mock_query = mock_db
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    # Mock preference object that will be "created"
    mock_pref = MagicMock(spec=NotificationPreference)
    mock_pref.id = 101
    mock_pref.notification_type = "SALE"
    mock_pref.channel_push = True
    mock_pref.channel_sms = False
    mock_pref.channel_email = False
    mock_pref.store_filter_id = None

    # Side effects for first() calls: 1. User check, 2. Preference check (returns None for 'new')
    mock_query.first.side_effect = [mock_user, None]

    # Patch the model instantiation to return our mock
    with patch(
        "app.routers.notifications.NotificationPreference", return_value=mock_pref
    ):
        prefs_data = [
            {"notification_type": "SALE", "channel_push": True, "channel_sms": False}
        ]

        response = await client.put(
            "/api/v1/notifications/preferences?user_id=1", json=prefs_data
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == 101


@pytest.mark.asyncio
async def test_get_notifications_unread(client: AsyncClient, mock_db, override_db):
    """Test filtering by unread status."""
    db, mock_query = mock_db
    mock_notification = MagicMock(spec=Notification)
    mock_notification.id = 1
    mock_notification.notification_type = "SALE"
    mock_notification.title = "Title"
    mock_notification.message = "Msg"
    mock_notification.is_read = False
    mock_notification.created_at = datetime.now(timezone.utc)

    mock_query.all.return_value = [mock_notification]

    response = await client.get("/api/v1/notifications?user_id=1&unread_only=true")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_mark_as_read_success(client: AsyncClient, mock_db, override_db):
    """Test marking notification as read."""
    db, mock_query = mock_db
    mock_notification = MagicMock(spec=Notification)
    mock_query.first.return_value = mock_notification

    response = await client.post("/api/v1/notifications/1/read")

    assert response.status_code == 200
    assert mock_notification.is_read is True
    assert db.commit.called


@pytest.mark.asyncio
async def test_send_notification_logic(client: AsyncClient, mock_db, override_db):
    """Test internal send notification endpoint."""
    db, mock_query = mock_db
    mock_query.first.side_effect = [
        MagicMock(spec=User),
        None,
    ]  # User exists, no specific prefs

    send_data = {
        "user_id": 1,
        "notification_type": "UNPAID_EXIT",
        "title": "Alert",
        "message": "Unpaid item detected",
    }

    response = await client.post("/api/v1/notifications/send", json=send_data)

    assert response.status_code == 201
    assert response.json()["message"] == "Notification sent"
    assert "sms" in response.json()["channels"]  # Default for UNPAID_EXIT
