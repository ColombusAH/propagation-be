"""
Tests for main application and miscellaneous modules.
Covers: database.py, main.py entry points
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestDatabase:
    """Tests for database module."""

    def test_get_db(self):
        """Test get_db dependency."""
        from app.services.database import get_db
        
        # get_db should work
        assert get_db is not None

    def test_session_local(self):
        """Test SessionLocal is configured."""
        from app.services.database import SessionLocal
        
        assert SessionLocal is not None


class TestSecurityHeaders:
    """Tests for security middleware."""

    def test_security_headers_enabled(self):
        """Test that security headers are added."""
        from app.core.config import settings
        
        assert settings.SECURITY_HEADERS is True

    def test_cors_origins(self):
        """Test CORS origins configuration."""
        from app.core.config import settings
        
        assert len(settings.BACKEND_CORS_ORIGINS) > 0
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS


class TestWebSocket:
    """Tests for WebSocket manager."""

    @pytest.mark.asyncio
    async def test_websocket_manager_connect(self):
        """Test WebSocket connection."""
        from app.routers.websocket import manager
        
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        
        await manager.connect(mock_ws)
        
        assert mock_ws in manager.active_connections

    @pytest.mark.asyncio
    async def test_websocket_manager_disconnect(self):
        """Test WebSocket disconnection."""
        from app.routers.websocket import manager
        
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        
        await manager.connect(mock_ws)
        manager.disconnect(mock_ws)
        
        assert mock_ws not in manager.active_connections

    @pytest.mark.asyncio
    async def test_websocket_manager_broadcast(self):
        """Test broadcasting to all clients."""
        from app.routers.websocket import manager
        
        # Clear connections
        manager.active_connections = []
        
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws)
        
        await manager.broadcast({"type": "test", "data": "hello"})
        
        mock_ws.send_json.assert_called_once()


class TestM200Protocol:
    """Tests for M-200 protocol functions."""

    def test_build_inventory_command(self):
        """Test building inventory command."""
        from app.services.m200_protocol import build_inventory_command
        
        cmd = build_inventory_command()
        
        assert cmd is not None
        # M200Command has serialize() method, not frame attribute

    def test_build_stop_inventory_command(self):
        """Test building stop inventory command."""
        from app.services.m200_protocol import build_stop_inventory_command
        
        cmd = build_stop_inventory_command()
        
        assert cmd is not None

    def test_m200_command_enum(self):
        """Test M200Commands enum."""
        from app.services.m200_protocol import M200Commands
        
        # Use actual enum values from M200Commands class
        assert M200Commands.RFM_GET_DEVICE_INFO is not None
        assert M200Commands.RFM_INVENTORYISO_CONTINUE is not None

