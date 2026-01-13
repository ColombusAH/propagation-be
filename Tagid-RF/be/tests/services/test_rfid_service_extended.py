import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.rfid_reader import RFIDReaderService


@pytest.mark.asyncio
async def test_connect_wifi_failure():
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = "wifi"
    with patch("asyncio.open_connection", side_effect=Exception("Connection Refused")):
        result = await service.connect()
        assert result is False
        assert service.is_connected is False


@pytest.mark.asyncio
async def test_disconnect_full():
    service = RFIDReaderService()
    service.writer = AsyncMock()
    service.is_connected = True
    await service.disconnect()
    service.writer.close.assert_called()
    assert service.is_connected is False


@pytest.mark.asyncio
async def test_process_tag_new():
    service = RFIDReaderService()
    tag_data = {"epc": "NEW-TAG", "rssi": -70.0}
    with (
        patch("app.services.rfid_reader.SessionLocal") as mock_session_local,
        patch("app.routers.websocket.manager.broadcast", new_callable=AsyncMock),
    ):

        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query().filter().first.return_value = None  # New tag

        await service._process_tag(tag_data)

        assert mock_db.add.called
        assert mock_db.commit.called
