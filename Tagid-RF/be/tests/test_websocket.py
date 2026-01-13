import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.websocket import manager


def test_websocket_connection():
    """Test WebSocket connection and welcome message."""
    with patch("app.db.prisma.prisma_client.connect", new_callable=AsyncMock) as mock_connect:
        with TestClient(app) as client:
            with client.websocket_connect("/ws/rfid") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "welcome"
                assert "Connected" in data["message"]


@pytest.mark.asyncio
async def test_websocket_broadcast():
    """Test broadcasting a message to a mock connection."""
    mock_ws = AsyncMock()
    await manager.connect(mock_ws)
    assert len(manager.active_connections) == 1

    test_msg = {"type": "test", "data": "hello"}
    await manager.broadcast(test_msg)

    mock_ws.send_json.assert_called_with(test_msg)

    manager.disconnect(mock_ws)
    assert len(manager.active_connections) == 0
