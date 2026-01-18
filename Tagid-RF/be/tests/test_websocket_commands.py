import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.routers.websocket import manager, websocket_endpoint


@pytest.mark.asyncio
async def test_websocket_subscribe_command():
    """Test WebSocket subscribe command."""
    mock_ws = AsyncMock()
    mock_ws.receive_text.side_effect = [
        json.dumps({"command": "subscribe"}),
        RuntimeError("StopLoop"),
    ]

    try:
        await websocket_endpoint(mock_ws)
    except RuntimeError:
        pass

    # Should have sent subscribed message
    calls = [str(c) for c in mock_ws.send_json.call_args_list]
    assert any("subscribed" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_websocket_unknown_command():
    """Test WebSocket unknown command."""
    mock_ws = AsyncMock()
    mock_ws.receive_text.side_effect = [
        json.dumps({"command": "unknown_cmd"}),
        RuntimeError("StopLoop"),
    ]

    try:
        await websocket_endpoint(mock_ws)
    except RuntimeError:
        pass

    # Should have sent error message
    calls = [str(c) for c in mock_ws.send_json.call_args_list]
    assert any("error" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_websocket_invalid_json():
    """Test WebSocket with invalid JSON."""
    mock_ws = AsyncMock()
    mock_ws.receive_text.side_effect = ["not valid json", RuntimeError("StopLoop")]

    try:
        await websocket_endpoint(mock_ws)
    except RuntimeError:
        pass

    # Should have sent error message about invalid JSON
    calls = [str(c) for c in mock_ws.send_json.call_args_list]
    assert any("invalid" in c.lower() or "error" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_manager_broadcast_error():
    """Test manager broadcast with connection error."""
    # Clear connections from previous tests
    manager.active_connections = []
    
    mock_ws = AsyncMock()
    mock_ws.send_json.side_effect = Exception("Connection lost")

    await manager.connect(mock_ws)
    await manager.broadcast({"test": "message"})

    # Should have removed the failed connection
    assert mock_ws not in manager.active_connections

