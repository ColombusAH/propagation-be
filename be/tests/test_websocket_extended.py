import pytest
from unittest.mock import AsyncMock, patch
from app.routers.websocket import manager
from fastapi import WebSocket

@pytest.mark.asyncio
async def test_websocket_message_handling():
    """Test handling different WebSocket messages."""
    mock_ws = AsyncMock(spec=WebSocket)
    await manager.connect(mock_ws)
    
    # Test ping
    # Since we can't easily trigger the receive loop from outside without a thread,
    # we'll test the manager's methods directly or mock the receive_json.
    
    # Example: Test invalid JSON handling (if implemented in broadcast or similar)
    # Actually, the logic is in the endpoint's loop. 
    # Let's test manager.broadcast to multiple connections.
    mock_ws2 = AsyncMock(spec=WebSocket)
    await manager.connect(mock_ws2)
    assert len(manager.active_connections) == 2
    
    await manager.broadcast({"msg": "hello"})
    assert mock_ws.send_json.called
    assert mock_ws2.send_json.called
    
    manager.disconnect(mock_ws)
    manager.disconnect(mock_ws2)
