from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Aggressive mocking at source to prevent side effects
with patch("app.services.push_notifications.PushNotificationService"):
    with patch("app.services.theft_detection.TheftDetectionService"):
        from app.api.v1.endpoints.alerts import router

from app.api.dependencies.auth import get_current_user as auth_get_user
from app.core.deps import get_current_user as core_get_user
from datetime import datetime

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "user_123"
    user.role = "STORE_MANAGER"
    return user

@pytest.fixture
def test_app(mock_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[auth_get_user] = lambda: mock_user
    app.dependency_overrides[core_get_user] = lambda: mock_user
    return app

@pytest.fixture
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac

def create_mock_alert(id, epc):
    alert = MagicMock()
    alert.id = str(id)
    alert.epc = str(epc)
    alert.productDescription = "Description"
    alert.detectedAt = datetime.now()
    alert.location = "Gate 1"
    alert.resolved = False
    alert.resolvedAt = None
    alert.resolvedBy = None
    alert.notes = None
    return alert

@pytest.mark.asyncio
async def test_list_theft_alerts_success(client):
    with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_p:
        mock_p.client.theftalert.find_many = AsyncMock(return_value=[create_mock_alert("a1", "e1")])
        response = await client.get("/?resolved=false")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_alert_details_success(client):
    with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_p:
        mock_p.client.theftalert.find_unique = AsyncMock(return_value=create_mock_alert("a2", "e2"))
        response = await client.get("/a2")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_resolve_alert_success(client):
    # Patch the attribute on the module directly
    import app.api.v1.endpoints.alerts as alerts_mod
    with patch.object(alerts_mod, 'theft_service') as mock_svc:
        mock_svc.resolve_alert = AsyncMock()
        response = await client.post("/a3/resolve", json={"notes": "fixed"})
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_my_alerts_success(client):
    with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_p:
        mock_rec = MagicMock()
        mock_rec.theftAlert = create_mock_alert("a_my", "e_my")
        mock_p.client.alertrecipient.find_many = AsyncMock(return_value=[mock_rec])
        response = await client.get("/my-alerts")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_mark_alert_read_success(client):
    with patch("app.api.v1.endpoints.alerts.prisma_client") as mock_p:
        mock_rec = MagicMock(id="r1")
        mock_p.client.alertrecipient.find_first = AsyncMock(return_value=mock_rec)
        mock_p.client.alertrecipient.update = AsyncMock()
        response = await client.post("/mark-read/a4")
        assert response.status_code == 200
