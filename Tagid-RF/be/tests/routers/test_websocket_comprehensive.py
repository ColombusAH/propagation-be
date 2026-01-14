"""
Comprehensive tests for WebSocket router and ConnectionManager.
Covers connection, disconnection, broadcasting, and message handling.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.routers.websocket import ConnectionManager


# --- ConnectionManager Tests ---
def test_connection_manager_init():
    """Test ConnectionManager initialization."""
    manager = ConnectionManager()
    assert manager.active_connections == []


@pytest.mark.asyncio
async def test_connect():
    """Test connecting a WebSocket client."""
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()

    await manager.connect(mock_ws)

    mock_ws.accept.assert_called_once()
    assert mock_ws in manager.active_connections


def test_disconnect():
    """Test disconnecting a WebSocket client."""
    manager = ConnectionManager()
    mock_ws = MagicMock()
    manager.active_connections.append(mock_ws)

    manager.disconnect(mock_ws)

    assert mock_ws not in manager.active_connections


def test_disconnect_not_in_list():
    """Test disconnect handles websocket not in list gracefully."""
    manager = ConnectionManager()
    mock_ws = MagicMock()

    # Should not raise
    manager.disconnect(mock_ws)
    assert len(manager.active_connections) == 0


@pytest.mark.asyncio
async def test_broadcast_empty():
    """Test broadcast with no connections does nothing."""
    manager = ConnectionManager()
    # Should not raise
    await manager.broadcast({"type": "test"})


@pytest.mark.asyncio
async def test_broadcast_single():
    """Test broadcast to single connection."""
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.send_json = AsyncMock()
    manager.active_connections.append(mock_ws)

    await manager.broadcast({"type": "test", "data": "hello"})

    mock_ws.send_json.assert_called_once_with({"type": "test", "data": "hello"})


@pytest.mark.asyncio
async def test_broadcast_multiple():
    """Test broadcast to multiple connections."""
    manager = ConnectionManager()
    mock_ws1 = MagicMock()
    mock_ws1.send_json = AsyncMock()
    mock_ws2 = MagicMock()
    mock_ws2.send_json = AsyncMock()

    manager.active_connections.extend([mock_ws1, mock_ws2])

    await manager.broadcast({"type": "test"})

    mock_ws1.send_json.assert_called_once()
    mock_ws2.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_removes_disconnected():
    """Test broadcast removes clients that fail to receive."""
    manager = ConnectionManager()
    mock_ws1 = MagicMock()
    mock_ws1.send_json = AsyncMock()
    mock_ws2 = MagicMock()
    mock_ws2.send_json = AsyncMock(side_effect=Exception("Connection lost"))

    manager.active_connections.extend([mock_ws1, mock_ws2])

    await manager.broadcast({"type": "test"})

    # ws1 should remain, ws2 should be removed
    assert mock_ws1 in manager.active_connections
    assert mock_ws2 not in manager.active_connections


@pytest.mark.asyncio
async def test_send_personal_message():
    """Test sending message to specific client."""
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.send_json = AsyncMock()

    await manager.send_personal_message({"type": "welcome"}, mock_ws)

    mock_ws.send_json.assert_called_once_with({"type": "welcome"})


@pytest.mark.asyncio
async def test_send_personal_message_error():
    """Test send_personal_message handles error and disconnects."""
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.send_json = AsyncMock(side_effect=Exception("Send failed"))
    manager.active_connections.append(mock_ws)

    await manager.send_personal_message({"type": "test"}, mock_ws)

    # Should be disconnected due to error
    assert mock_ws not in manager.active_connections
