import pytest
import socket
import json
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import M200Command, M200Status

@pytest.fixture
def reader():
    return RFIDReaderService()

@pytest.mark.asyncio
async def test_get_reader_info_http_protocol(reader):
    """Test get_reader_info detecting HTTP protocol mismatch."""
    reader.is_connected = True
    # Simulate an HTTP response
    http_response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Length: 45\r\n\r\n"
        b'{"type": "event", "event": "output", "data": "debugpy"}'
    )
    
    with patch.object(reader, "_send_command", return_value=http_response):
        info = await reader.get_reader_info()
        assert "Wrong protocol" in info["error"]
        assert info["protocol_detected"] == "JSON/HTTP"

@pytest.mark.asyncio
async def test_get_reader_info_json_content(reader):
    """Test get_reader_info parsing JSON from Content-Length header."""
    reader.is_connected = True
    # Simulate a JSON response with debugpy event
    json_response = (
        b"Content-Length: 60\r\n\r\n"
        b'{"type": "event", "body": {"category": "stdout", "output": "debugpy"}}'
    )
    
    with patch.object(reader, "_send_command", return_value=json_response):
        info = await reader.get_reader_info()
        assert "debugpy" in info["error"] or "Wrong protocol" in info["error"]

@pytest.mark.asyncio
async def test_get_reader_info_parsing_error(reader):
    """Test get_reader_info handling binary protocol parsing error (not HTTP)."""
    reader.is_connected = True
    # Random bytes that are not HTTP and fail M200 parsing
    random_bytes = b"\x00\x01\x02\x03\x04\x05"
    
    with patch.object(reader, "_send_command", return_value=random_bytes):
        info = await reader.get_reader_info()
        assert "connected" in info
        assert "raw_response_hex" in info

@pytest.mark.asyncio
async def test_get_reader_info_failure_status(reader):
    """Test get_reader_info when reader returns a failure status."""
    reader.is_connected = True
    mock_resp = MagicMock()
    mock_resp.success = False
    mock_resp.status = 0x01 # General error
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_resp):
        with patch.object(reader, "_send_command", return_value=b"\xcf..."):
            info = await reader.get_reader_info()
            assert "error" in info
            assert info["connected"] is True

@pytest.mark.asyncio
async def test_read_single_tag_various_errors(reader):
    """Test read_single_tag error cases."""
    reader.is_connected = True
    
    # 1. Not successful
    mock_resp = MagicMock()
    mock_resp.success = False
    mock_resp.status = 0x01
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_resp):
        with patch.object(reader, "_send_command", return_value=b"data"):
            tags = await reader.read_single_tag()
            assert tags == []
            
    # 2. Exception in scan
    with patch.object(reader, "_send_command", side_effect=Exception("Crash")):
        tags = await reader.read_single_tag()
        assert tags == []

@pytest.mark.asyncio
async def test_write_tag_not_implemented(reader):
    """Test write_tag returns False (current implementation)."""
    result = await reader.write_tag("EPC", {})
    assert result is False

@pytest.mark.asyncio
async def test_hardware_control_exceptions(reader):
    """Test hardware control methods when exceptions occur."""
    reader.is_connected = True
    with patch.object(reader, "_send_command", side_effect=Exception("Socket Fail")):
        assert await reader.initialize_device() is False
        assert await reader.set_power(20) is False
        assert await reader.read_tag_memory(1, 0, 1) is None
        assert (await reader.get_network_config())["error"] is not None
        assert await reader.set_network_config("1.1.1.1") is False
        assert await reader.set_rssi_filter(1, 50) is False
        assert (await reader.get_all_params())["error"] is not None
        assert await reader.get_gpio_levels() == {}
        assert await reader.set_gpio(1, 0) is False
        assert await reader.control_relay(1) is False

@pytest.mark.asyncio
async def test_get_status(reader):
    """Test get_status method."""
    reader.is_connected = True
    reader.is_scanning = True
    reader._device_info = {"model": "M-200"}
    status = reader.get_status()
    assert status["is_connected"] is True
    assert status["is_scanning"] is True
    assert status["device_info"]["model"] == "M-200"
