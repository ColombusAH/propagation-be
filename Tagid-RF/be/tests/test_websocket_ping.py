import json
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.websocket import websocket_endpoint


@pytest.mark.asyncio
async def test_websocket_ping():
    """Test WebSocket ping command logic with correct command key."""
    mock_ws = AsyncMock()
    # Mock receive_text to return JSON string with 'command' key
    mock_ws.receive_text.side_effect = [
        json.dumps({"command": "ping"}),
        RuntimeError("StopLoop"),
    ]

    try:
        await websocket_endpoint(mock_ws)
    except RuntimeError as e:
        if str(e) != "StopLoop":
            raise
    except Exception:
        pass

    # The endpoint should have sent a pong
    mock_ws.send_json.assert_any_call({"type": "pong", "timestamp": None})
