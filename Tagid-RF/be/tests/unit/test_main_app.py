"""
Unit tests for main app configuration and middleware.
"""

import pytest


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
class TestRouterRegistration:
    """Tests for router registration."""

    def test_stores_router_registered(self):
        """Test stores router is registered."""
        from app.main import app
        
        paths = [r.path for r in app.routes]
        
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


@pytest.mark.unit
class TestAppSettings:
    """Tests for app settings usage."""

    def test_settings_used_in_app(self):
        """Test settings are properly loaded."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert settings.API_V1_STR is not None

    def test_api_prefix_format(self):
        """Test API prefix is properly formatted."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert settings.API_V1_STR.startswith("/api")

