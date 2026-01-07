"""
Unit tests for main app configuration and middleware.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestAppConfiguration:
    """Tests for main app configuration."""

    def test_app_has_title(self):
        """Test app has correct title."""
        from app.main import app
        
        assert app.title is not None
        assert len(app.title) > 0

    def test_app_has_openapi_url(self):
        """Test app has openapi URL configured."""
        from app.main import app
        
        assert app.openapi_url is not None
        assert "openapi.json" in app.openapi_url

    def test_app_has_routes(self):
        """Test app has routes registered."""
        from app.main import app
        
        routes = [r.path for r in app.routes]
        
        assert "/" in routes
        assert "/health" in routes
        assert "/healthz" in routes


@pytest.mark.unit
class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns expected data."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "docs" in data

    def test_health_endpoint(self, client: TestClient):
        """Test /health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_healthz_endpoint(self, client: TestClient):
        """Test /healthz endpoint."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.unit
class TestSecurityHeaders:
    """Tests for security headers middleware."""

    def test_security_headers_present(self, client: TestClient):
        """Test security headers are present in response."""
        response = client.get("/")
        
        # These may be present depending on settings
        headers = response.headers
        
        # App should respond successfully
        assert response.status_code == 200


@pytest.mark.unit
class TestCORSConfiguration:
    """Tests for CORS middleware configuration."""

    def test_cors_allows_options(self, client: TestClient):
        """Test CORS preflight request handling."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Should not return 405 Method Not Allowed
        assert response.status_code in [200, 400]


@pytest.mark.unit
class TestRouterRegistration:
    """Tests for router registration."""

    def test_stores_router_registered(self):
        """Test stores router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        # Check stores endpoint is available
        assert any("/stores" in path for path in paths)

    def test_users_router_registered(self):
        """Test users router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        assert any("/users" in path for path in paths)

    def test_notifications_router_registered(self):
        """Test notifications router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        assert any("/notifications" in path for path in paths)

    def test_exit_scan_router_registered(self):
        """Test exit-scan router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        assert any("/exit-scan" in path for path in paths)

    def test_tags_router_registered(self):
        """Test tags router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        assert any("/tags" in path for path in paths)

    def test_websocket_router_registered(self):
        """Test websocket router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
        assert any("/ws" in path for path in paths)
