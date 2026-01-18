import pytest
import socket
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import M200Commands, M200Status


@pytest.fixture
def reader():
    return RFIDReaderService()


@pytest.mark.asyncio
async def test_get_reader_info_protocol_mismatch_json(reader):
    """Test reader info when device responds with JSON/HTTP instead of binary (line 327+)."""
    reader.is_connected = True
    json_response = b'Content-Length: 50\r\n\r\n{"type":"event", "info":"debugpy"}'

    with patch.object(reader, "_send_command", return_value=json_response):
        info = await reader.get_reader_info()
        assert info["protocol_detected"] == "JSON/HTTP"
        assert "Wrong protocol" in info["error"]


@pytest.mark.asyncio
async def test_get_reader_info_status_failure(reader):
    """Test reader info when device returns success=False (line 379+)."""
    reader.is_connected = True

    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse") as mock_parse,
    ):
        mock_res = MagicMock()
        mock_res.success = False
        mock_res.status = 0x01
        mock_parse.return_value = mock_res

        info = await reader.get_reader_info()
        assert "error" in info


@pytest.mark.asyncio
async def test_rfid_reader_config_methods(reader):
    """Test various configuration methods in RFID reader (line 708+)."""
    reader.is_connected = True
    mock_res = MagicMock(success=True, data=b"\x01\x02\x03\x04\x05\x06\x07\x08")

    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):

        # Network Config
        await reader.get_network_config()
        await reader.set_network_config("192.168.1.100")

        # RSSI & Params
        await reader.set_rssi_filter(1, 40)
        await reader.get_all_params()

        # GPIO
        await reader.get_gpio_levels()
        await reader.set_gpio(1, 1, 1)

        # Relay
        await reader.control_relay(1, True)
        await reader.control_relay(2, False)
        # Invalid relay test
        res = await reader.control_relay(3, True)
        assert res is False

        # Gate & Query
        await reader.get_gate_status()
        await reader.set_gate_config()
        await reader.set_query_params()
        await reader.select_tag("E123")


# TagStore is not exported from tag_listener_service, so we cannot test it here.
# The fallback logic is tested via the actual service behavior.
