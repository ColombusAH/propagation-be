"""
Tests for app/main.py - Entry point, middleware, and lifespan events.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from app.main import app, SecurityHeadersMiddleware


@pytest.fixture
def client():
    # We need to mock lifespan events to prevent real connections
    with patch("app.main.init_db", new_callable=AsyncMock) as mock_init_db, \
         patch("app.main.shutdown_db", new_callable=AsyncMock) as mock_shutdown_db, \
         patch("app.main.init_rfid_db", new_callable=MagicMock) as mock_init_rfid, \
         patch("app.main.rfid_reader_service") as mock_rfid, \
         patch("app.main.tag_listener_service") as mock_listener:
        
        # Setup mocks
        mock_rfid.connect = AsyncMock(return_value=True)
        mock_rfid.start_scanning = AsyncMock()
        mock_rfid.disconnect = AsyncMock()
        mock_listener.start = MagicMock()
        mock_listener.stop = MagicMock()
        
        # Create client with lifespan context
        with TestClient(app) as c:
            yield c

def test_root_endpoint(client):
    """Test root endpoint /."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "RFID MVP API", "docs": "/docs", "redoc": "/redoc"}

def test_healthz_endpoint(client):
    """Test health check /healthz."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_security_headers_middleware():
    """Test security headers are applied."""
    # Create simple app for testing middleware
    from fastapi import FastAPI, Request
    
    test_app = FastAPI()
    test_app.add_middleware(SecurityHeadersMiddleware)
    
    @test_app.get("/")
    def index():
        return {"ok": True}
        
    client = TestClient(test_app)
    
    # Needs settings.SECURITY_HEADERS = True
    with patch("app.main.settings") as mock_settings:
        mock_settings.SECURITY_HEADERS = True
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]

def test_security_headers_middleware_disabled():
    """Test security headers are NOT applied when disabled."""
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.add_middleware(SecurityHeadersMiddleware)
    
    @test_app.get("/")
    def index():
        return {"ok": True}
        
    client = TestClient(test_app)
    
    with patch("app.main.settings") as mock_settings:
        mock_settings.SECURITY_HEADERS = False
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Content-Type-Options" not in response.headers

@pytest.mark.asyncio
async def test_lifespan_startup_success():
    """Test successful startup sequence explicitly."""
    from app.main import lifespan
    
    app_mock = MagicMock()
    
    with patch("app.main.init_db", new_callable=AsyncMock) as mock_db, \
         patch("app.main.init_rfid_db") as mock_rfid_db, \
         patch("app.main.rfid_reader_service") as mock_reader, \
         patch("app.main.tag_listener_service") as mock_listener, \
         patch("app.main.setup_logging"):
         
         mock_reader.connect = AsyncMock(return_value=True)
         mock_reader.start_scanning = AsyncMock()
         mock_listener.start = MagicMock()
         
         async with lifespan(app_mock):
             mock_db.assert_awaited_once()
             mock_rfid_db.assert_called_once()
             mock_reader.connect.assert_awaited_once()
             mock_reader.start_scanning.assert_awaited_once()
             mock_listener.start.assert_called_once()

@pytest.mark.asyncio
async def test_lifespan_startup_failures_handled():
    """Test startup failures are logged and don't crash."""
    from app.main import lifespan
    app_mock = MagicMock()
    
    with patch("app.main.init_db", side_effect=Exception("DB Fail")) as mock_db, \
         patch("app.main.rfid_reader_service") as mock_reader, \
         patch("app.main.tag_listener_service"), \
         patch("app.main.setup_logging"):
         
         mock_reader.connect = AsyncMock(side_effect=Exception("Reader Fail"))
         
         # Should not raise exception
         async with lifespan(app_mock):
             pass

@pytest.mark.asyncio
async def test_lifespan_shutdown_failures_handled():
    """Test shutdown failures are logged."""
    from app.main import lifespan
    app_mock = MagicMock()
    
    with patch("app.main.init_db", new_callable=AsyncMock), \
         patch("app.main.shutdown_db", side_effect=Exception("DB Stop Fail")), \
         patch("app.main.rfid_reader_service") as mock_reader, \
         patch("app.main.tag_listener_service"), \
         patch("app.main.setup_logging"):
         
         mock_reader.connect.return_value = False # Skip start logic
         mock_reader.disconnect = AsyncMock(side_effect=Exception("Reader Stop Fail"))
         
         async with lifespan(app_mock):
             pass
         # If we exit context without error, test passes
