import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from app.main import app
from app.core.deps import get_current_user
from app.api.dependencies.auth import get_current_user as get_current_user_api

# Function-level fixture for auth override
@pytest.fixture
def auth_mock():
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.role = "STORE_MANAGER"
    mock_user.businessId = "biz-123"
    return mock_user

@pytest.fixture
def override_auth(auth_mock):
    app.dependency_overrides[get_current_user] = lambda: auth_mock
    app.dependency_overrides[get_current_user_api] = lambda: auth_mock
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_list_theft_alerts(client, db_session, override_auth):
    """Test listing theft alerts."""
    mock_alert = MagicMock()
    mock_alert.id = "alert-1"
    mock_alert.epc = "urn:epc:123"
    mock_alert.resolved = False
    mock_alert.detectedAt = datetime.now()
    mock_alert.productDescription = "Test Product"
    mock_alert.location = "Test Location"
    mock_alert.resolvedBy = None
    mock_alert.notes = None
    
    db_session.client.theftalert.find_many.return_value = [mock_alert]
    
    response = await client.get("/api/v1/alerts/?limit=10", headers={"Authorization": "Bearer token"})
    if response.status_code != 200:
        print(f"DEBUG ERROR: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "alert-1"

@pytest.mark.asyncio
async def test_list_theft_alerts_error(client, db_session, override_auth):
    """Test error handling in list alerts."""
    db_session.client.theftalert.find_many.side_effect = Exception("DB Error")
    
    response = await client.get("/api/v1/alerts/", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_my_alerts(client, db_session, override_auth):
    """Test getting user alerts."""
    mock_recipient = MagicMock()
    mock_recipient.theftAlert.id = "alert-1"
    mock_recipient.theftAlert.detectedAt = datetime.now()
    mock_recipient.theftAlert.epc = "urn:epc:id:1"
    mock_recipient.theftAlert.productDescription = "Test Product"
    mock_recipient.theftAlert.location = "Test Loc"
    mock_recipient.theftAlert.resolvedBy = None
    mock_recipient.theftAlert.notes = None
    mock_recipient.theftAlert.resolved = False
    mock_recipient.isRead = False
    mock_recipient.userId = "user-1"
    mock_recipient.createdAt = datetime.now()
    
    db_session.client.alertrecipient.find_many.return_value = [mock_recipient]
    
    response = await client.get("/api/v1/alerts/my-alerts", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_get_alert_details(client, db_session, override_auth):
    """Test getting single alert details."""
    mock_alert = MagicMock()
    mock_alert.id = "alert-1"
    mock_alert.detectedAt = datetime.now()
    mock_alert.epc = "urn:epc:id:sgtin:..."
    mock_alert.productDescription = "Test Product"
    mock_alert.location = "Test Location"
    mock_alert.resolvedBy = None
    mock_alert.notes = None
    mock_alert.resolved = False
    
    db_session.client.theftalert.find_unique.return_value = mock_alert
    
    response = await client.get("/api/v1/alerts/alert-1", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 200
    assert response.json()["id"] == "alert-1"

@pytest.mark.asyncio
async def test_get_alert_details_not_found(client, db_session, override_auth):
    """Test alert not found."""
    db_session.client.theftalert.find_unique.return_value = None
    
    response = await client.get("/api/v1/alerts/unknown", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_resolve_alert(client, db_session, override_auth):
    """Test resolving an alert."""
    with patch("app.api.v1.endpoints.alerts.theft_service.resolve_alert", new_callable=AsyncMock) as mock_resolve:
        response = await client.post("/api/v1/alerts/alert-1/resolve", json={"notes": "Fixed"}, headers={"Authorization": "Bearer token"})
        
        assert response.status_code == 200
        mock_resolve.assert_called_once()

@pytest.mark.asyncio
async def test_mark_alert_read(client, db_session, override_auth):
    """Test marking alert as read."""
    mock_recipient = MagicMock()
    mock_recipient.id = "rec-1"
    mock_recipient.theftAlertId = "alert-1"
    mock_recipient.userId = "user-1"
    mock_recipient.isRead = False
    mock_recipient.createdAt = datetime.now()
    # Mock nested alert if needed by response
    mock_recipient.theftAlert = MagicMock()
    mock_recipient.theftAlert.id = "alert-1"
    mock_recipient.theftAlert.detectedAt = datetime.now()
    mock_recipient.theftAlert.productDescription = "Test P"
    mock_recipient.theftAlert.location = "Loc"
    mock_recipient.theftAlert.resolved = False
    mock_recipient.theftAlert.resolvedBy = None
    mock_recipient.theftAlert.notes = None
    
    db_session.client.alertrecipient.find_first.return_value = mock_recipient
    
    response = await client.post("/api/v1/alerts/mark-read/alert-1", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 200
    db_session.client.alertrecipient.update.assert_called_once()

@pytest.mark.asyncio
async def test_mark_alert_read_not_found(client, db_session, override_auth):
    """Test marking alert read not found."""
    db_session.client.alertrecipient.find_first.return_value = None
    
    response = await client.post("/api/v1/alerts/mark-read/unknown", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 404
