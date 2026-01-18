from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.dependencies.auth import get_current_user as get_current_user_auth
from app.core.deps import get_current_user as get_current_user_core
from app.core.permissions import requires_any_role
from app.main import app


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "user-123"
    user.email = "test@example.com"
    user.role = "STORE_MANAGER"
    return user


@pytest.fixture(autouse=True)
def setup_overrides(mock_user):
    app.dependency_overrides[get_current_user_core] = lambda: mock_user
    app.dependency_overrides[get_current_user_auth] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


class TestListTheftAlerts:
    """Tests for GET /alerts/ endpoint."""

    @pytest.mark.asyncio
    async def test_list_alerts_success(self, client):
        """Test listing theft alerts."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_alert = MagicMock()
            mock_alert.id = "alert-1"
            mock_alert.epc = "E280681000001234"
            mock_alert.productDescription = "Product A"
            mock_alert.detectedAt = datetime.now()
            mock_alert.location = "Exit Gate 1"
            mock_alert.resolved = False
            mock_alert.resolvedAt = None
            mock_alert.resolvedBy = None
            mock_alert.notes = None

            mock_prisma.client.theftalert.find_many = AsyncMock(return_value=[mock_alert])

            response = await client.get("/api/v1/alerts/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == "alert-1"

    @pytest.mark.asyncio
    async def test_list_alerts_with_resolved_filter(self, client):
        """Test listing alerts with resolved filter."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_prisma.client.theftalert.find_many = AsyncMock(return_value=[])

            response = await client.get("/api/v1/alerts/?resolved=true")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_alerts_pagination(self, client):
        """Test listing alerts with pagination."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_prisma.client.theftalert.find_many = AsyncMock(return_value=[])

            response = await client.get("/api/v1/alerts/?limit=10&offset=5")
            assert response.status_code == 200


class TestGetMyAlerts:
    """Tests for GET /alerts/my-alerts endpoint."""

    @pytest.mark.asyncio
    async def test_get_my_alerts(self, client):
        """Test getting current user's alerts."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_alert = MagicMock()
            mock_alert.id = "alert-1"
            mock_alert.epc = "E280681000001234"
            mock_alert.productDescription = "Product A"
            mock_alert.detectedAt = datetime.now()
            mock_alert.location = "Exit Gate 1"
            mock_alert.resolved = False
            mock_alert.resolvedAt = None
            mock_alert.resolvedBy = None
            mock_alert.notes = None

            mock_recipient = MagicMock()
            mock_recipient.theftAlert = mock_alert

            mock_prisma.client.alertrecipient.find_many = AsyncMock(return_value=[mock_recipient])

            response = await client.get("/api/v1/alerts/my-alerts")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_my_alerts_unread_only(self, client):
        """Test getting only unread alerts."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_prisma.client.alertrecipient.find_many = AsyncMock(return_value=[])

            response = await client.get("/api/v1/alerts/my-alerts?unread_only=true")
            assert response.status_code == 200


class TestGetAlertDetails:
    """Tests for GET /alerts/{alert_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_alert_details_found(self, client):
        """Test getting alert details - found."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_alert = MagicMock()
            mock_alert.id = "alert-1"
            mock_alert.epc = "E280681000001234"
            mock_alert.productDescription = "Product A"
            mock_alert.detectedAt = datetime.now()
            mock_alert.location = "Exit Gate 1"
            mock_alert.resolved = False
            mock_alert.resolvedAt = None
            mock_alert.resolvedBy = None
            mock_alert.notes = None

            mock_prisma.client.theftalert.find_unique = AsyncMock(return_value=mock_alert)

            response = await client.get("/api/v1/alerts/alert-1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_alert_details_not_found(self, client):
        """Test getting alert details - not found."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_prisma.client.theftalert.find_unique = AsyncMock(return_value=None)

            response = await client.get("/api/v1/alerts/unknown-alert")
            assert response.status_code == 404


class TestResolveAlert:
    """Tests for POST /alerts/{alert_id}/resolve endpoint."""

    @pytest.mark.asyncio
    async def test_resolve_alert_success(self, client):
        """Test resolving an alert."""
        with patch("app.api.v1.endpoints.alerts.theft_service") as mock_service:
            mock_service.resolve_alert = AsyncMock()

            response = await client.post(
                "/api/v1/alerts/alert-1/resolve",
                json={"notes": "False alarm - customer had receipt"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_resolve_alert_without_notes(self, client):
        """Test resolving alert without notes."""
        with patch("app.api.v1.endpoints.alerts.theft_service") as mock_service:
            mock_service.resolve_alert = AsyncMock()

            response = await client.post("/api/v1/alerts/alert-1/resolve", json={})
            assert response.status_code == 200


class TestMarkAlertRead:
    """Tests for POST /alerts/mark-read/{alert_id} endpoint."""

    @pytest.mark.asyncio
    async def test_mark_alert_read_success(self, client):
        """Test marking alert as read."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_recipient = MagicMock()
            mock_recipient.id = "recipient-1"

            mock_prisma.client.alertrecipient.find_first = AsyncMock(return_value=mock_recipient)
            mock_prisma.client.alertrecipient.update = AsyncMock()

            response = await client.post("/api/v1/alerts/mark-read/alert-1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_mark_alert_read_not_found(self, client):
        """Test marking non-existent alert as read."""
        with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_prisma:
            mock_prisma.client.alertrecipient.find_first = AsyncMock(return_value=None)

            response = await client.post("/api/v1/alerts/mark-read/unknown-alert")
            assert response.status_code == 404
