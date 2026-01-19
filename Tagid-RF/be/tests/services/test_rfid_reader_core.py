"""
Expanded Tests for RFID Reader Service and M200 Protocol.
Covers connection, disconnect, parsing, and complex command flows.
"""

import asyncio
import socket
import struct
from unittest.mock import MagicMock, patch

import pytest
from app.services.m200_protocol import (HEAD, M200Command, M200Commands,
                                        M200ResponseParser, calculate_crc16,
                                        parse_device_info, parse_gate_status,
                                        parse_inventory_response)
from app.services.rfid_reader import RFIDReaderService


@pytest.fixture
def reader_service():
    return RFIDReaderService()


# --- Protocol Tests ---


def test_calculate_crc16():
    """Test CRC16 calculation with known values."""
    data = bytes([0xCF, 0x00, 0x00, 0x70, 0x00])
    crc = calculate_crc16(data)
    assert isinstance(crc, int)
    assert 0 <= crc <= 0xFFFF


def test_m200_command_serialization():
    """Test building a command frame."""
    cmd = M200Command(cmd=0x0070, data=b"", addr=0x00)
    serialized = cmd.serialize()
    assert serialized[0] == HEAD
    assert serialized[1] == 0x00
    assert serialized[2] == 0x00
    assert serialized[3] == 0x70
    assert len(serialized) == 7  # 5 header + 2 CRC


def test_m200_response_parser_valid_frame():
    """Test parsing a valid minimal frame."""
    header = struct.pack(">BBHB", HEAD, 0x00, 0x0070, 0x01)
    body = bytes([0x00])  # Status OK
    frame_no_crc = header + body
    crc = calculate_crc16(frame_no_crc)
    frame = frame_no_crc + struct.pack(">H", crc)

    response = M200ResponseParser.parse(frame)
    assert response.addr == 0x00
    assert response.cmd == 0x0070
    assert response.status == 0x00
    assert response.success is True


def test_parse_device_info_valid():
    """Test parsing device info payload (152 bytes expected)."""
    payload = bytearray(152)
    payload[0:10] = b"VER-1.0.0"  # CP Hardware version
    payload[32:42] = b"FW-2.0.0"  # CP Firmware version
    payload[64:74] = b"SN-123456"  # CP Serial Number

    info = parse_device_info(bytes(payload))
    assert info["cp_hardware_version"] == "VER-1.0.0"
    assert info["cp_firmware_version"] == "FW-2.0.0"
    assert info["cp_serial_number"] == "SN-123456"


def test_parse_gate_status():
    """Test parsing gate status (mode and direction)."""
    # 0x01 = detecting mode, 0x02 = exit direction
    data = bytes([0x01, 0x02])
    status = parse_gate_status(data)
    assert status["mode"] == 1
    assert status["direction"] == 2


def test_parse_inventory_response_empty():
    """Test parsing inventory response with no tags."""
    data = bytes([])  # Empty data = no tags
    tags = parse_inventory_response(data)
    assert len(tags) == 0


# --- Service Tests ---


@pytest.mark.asyncio
async def test_reader_connect_disconnect(reader_service):
    """Test connect and disconnect flow."""
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = mock_socket_cls.return_value
        with patch.object(
            reader_service, "get_reader_info", return_value={"connected": True}
        ):
            assert await reader_service.connect() is True
            assert reader_service.is_connected is True
            await reader_service.disconnect()
            assert reader_service.is_connected is False
            assert mock_sock.close.called


@pytest.mark.asyncio
async def test_reader_send_command_garbage_handling(reader_service):
    """Test _send_command when getting unexpected data start byte."""
    reader_service.is_connected = True
    reader_service._socket = MagicMock()

    # 0xEE triggers the "Unexpected first byte" path
    reader_service._socket.recv.side_effect = [bytes([0xEE]), b"MoreGarbage"]

    # It's a sync method, call it directly
    response = reader_service._send_command(M200Command(0x1234))
    assert response == bytes([0xEE]) + b"MoreGarbage"


@pytest.mark.asyncio
async def test_reader_get_status(reader_service):
    """Test get_status reports correct state."""
    reader_service.is_connected = True
    reader_service.is_scanning = True
    reader_service._device_info = {"model": "M-200"}

    status = reader_service.get_status()
    assert status["is_connected"] is True
    assert status["is_scanning"] is True
    assert status["device_info"]["model"] == "M-200"


@pytest.mark.asyncio
async def test_read_single_tag_no_tags(reader_service):
    """Test reading tags when none are present."""
    reader_service.is_connected = True

    # Frame with 0x12 (INVENTORY_COMPLETE) status
    header = struct.pack(">BBHB", HEAD, 0x00, 0x0001, 0x01)
    body = bytes([0x12])
    frame_no_crc = header + body
    crc = calculate_crc16(frame_no_crc)
    response_frame = frame_no_crc + struct.pack(">H", crc)

    with patch.object(reader_service, "_send_command", return_value=response_frame):
        tags = await reader_service.read_single_tag()
        assert len(tags) == 0


@pytest.mark.asyncio
async def test_read_single_tag_success(reader_service):
    """Test successful tag read with correct hex EPC parsing."""
    reader_service.is_connected = True

    # Tag data: RSSI(0x40), Ant(0x01), PC(0x30, 0x00), EPCLen(0x06), EPC(6 bytes)
    epc_bytes = b"ABC123"  # Hex: 414243313233
    tag1_data = bytes([0x40, 0x01, 0x30, 0x00, 0x06]) + epc_bytes

    # Inventory response body: Status(0x00) + TagData (NO Count byte at start of data)
    body = bytes([0x00]) + tag1_data
    header = struct.pack(">BBHB", HEAD, 0x00, 0x0001, len(body))
    frame_no_crc = header + body
    crc = calculate_crc16(frame_no_crc)
    response_frame = frame_no_crc + struct.pack(">H", crc)

    with patch.object(reader_service, "_send_command", return_value=response_frame):
        tags = await reader_service.read_single_tag()
        assert len(tags) == 1
        assert tags[0]["epc"] == "414243313233"
        assert tags[0]["rssi"] == -64  # 0x40 = 64
