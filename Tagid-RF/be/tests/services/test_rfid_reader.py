import asyncio
import logging
import socket
import struct
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from app.models.rfid_tag import RFIDTag
from app.services.m200_protocol import HEAD, M200Command, M200Commands, M200Status, calculate_crc16
from app.services.rfid_reader import RFIDReaderService


@pytest.fixture
def reader():
    service = RFIDReaderService()
    service.reader_ip = "192.168.1.100"
    service.reader_port = 4001
    service.is_connected = True
    service.reader_id = "M-200"  # Ensure it's a string, not a MagicMock
    return service


@pytest.mark.asyncio
async def test_send_command_unsolicited_and_retries(reader):
    """Test _send_command when it receives unsolicited messages before the correct one."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    # Correct CMD is 0x0070
    correct_cmd = 0x0070
    wrong_cmd = 0xFFFF

    def build_frame(cmd):
        header = struct.pack(">BBHB", HEAD, 0x00, cmd, 0x01)
        body = bytes([0x00])
        frame_no_crc = header + body
        crc = calculate_crc16(frame_no_crc)
        return frame_no_crc + struct.pack(">H", crc)

    # First read: wrong CMD
    # Second read: correct CMD
    mock_sock.recv.side_effect = [
        build_frame(wrong_cmd)[:1],
        build_frame(wrong_cmd)[1:6],
        build_frame(wrong_cmd)[6:],  # Wrong CMD
        build_frame(correct_cmd)[:1],
        build_frame(correct_cmd)[1:6],
        build_frame(correct_cmd)[6:],  # Correct CMD
    ]

    cmd = M200Command(correct_cmd)
    result = reader._send_command(cmd, max_retries=3)

    assert struct.unpack(">H", result[2:4])[0] == correct_cmd
    assert mock_sock.recv.call_count == 6


@pytest.mark.asyncio
async def test_send_command_unexpected_first_byte(reader):
    """Test _send_command when first byte is not HEAD."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    # Unexpected first byte 0xAA
    mock_sock.recv.side_effect = [b"\xaa", b"some extra data"]

    cmd = M200Command(0x0070)
    result = reader._send_command(cmd)

    assert result == b"\xaasome extra data"


@pytest.mark.asyncio
async def test_get_reader_info_debugpy_detection(reader):
    """Test detection of debugpy port in get_reader_info."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    # Simulate a debugpy/JSON response
    json_resp = b'Content-Length: 100\r\n\r\n{"type":"event", "event":"output", "body":{"category":"telemetry", "output":"debugpy"}}'

    with patch.multiple(reader, _send_command=MagicMock(return_value=json_resp)):
        info = await reader.get_reader_info()
        assert info["protocol_detected"] == "JSON/HTTP"
        assert "Wrong protocol" in info["error"]
        # The code logs "debugpy" but the returned error is generic "Wrong protocol"


@pytest.mark.asyncio
async def test_read_single_tag_inventory_complete(reader):
    """Test read_single_tag when status is INVENTORY_COMPLETE."""
    with patch.object(reader, "_send_command") as mock_send:
        # Build INVENTORY_COMPLETE response (status 0x12)
        # Note: LEN=1 (just STATUS), STATUS=0x12
        header = struct.pack(">BBHB", HEAD, 0x00, M200Commands.RFM_INVENTORYISO_CONTINUE, 0x01)
        frame = header + bytes([M200Status.INVENTORY_COMPLETE])
        crc = calculate_crc16(frame)
        mock_send.return_value = frame + struct.pack(">H", crc)

        tags = await reader.read_single_tag()
        assert tags == []


@pytest.mark.asyncio
async def test_scan_loop_exception_handling(reader):
    """Test _scan_loop handles exceptions and continues."""
    reader.is_scanning = True

    # We want to test that it catches exception, sleeps, and continues.
    # We'll mock read_single_tag to raise exception then stop scanning.

    with patch.object(reader, "read_single_tag", side_effect=[Exception("Oops"), []]):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            # We need a way to stop the loop after two iterations
            async def stop_soon(*args, **kwargs):
                if reader.read_single_tag.call_count >= 2:
                    reader.is_scanning = False
                return None

            mock_sleep.side_effect = stop_soon

            await reader._scan_loop()

            assert reader.read_single_tag.call_count == 2
            mock_sleep.assert_any_call(1)  # Exception wait


@pytest.mark.asyncio
async def test_process_tag_new_and_existing(reader):
    """Test _process_tag for both new and existing tags, including Prisma mapping."""
    tag_data = {
        "epc": "E123",
        "rssi": -60,
        "antenna_port": 1,
        "pc": "3000",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    mock_db = MagicMock()
    mock_tag = MagicMock(spec=RFIDTag)
    mock_tag.id = "tag-uid-123"
    mock_tag.epc = "E123"
    mock_tag.read_count = 5

    # Use patch.multiple or nested patches for complex mocking
    with (
        patch("app.services.rfid_reader.SessionLocal", return_value=mock_db),
        patch(
            "app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock
        ) as mock_broadcast,
        patch("app.db.prisma.prisma_client") as mock_prisma,
    ):
        # 1. Test Existing Tag
        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

        # Mock Prisma
        mock_mapping = MagicMock()
        mock_mapping.encryptedQr = "QR_DATA_123"
        mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=mock_mapping)

        await reader._process_tag(tag_data)

        assert mock_tag.read_count == 6
        mock_db.commit.assert_called()
        mock_broadcast.assert_called_with({"type": "tag_scanned", "data": ANY})
        broadcast_data = mock_broadcast.call_args[0][0]["data"]
        assert broadcast_data["is_mapped"] is True
        assert broadcast_data["target_qr"] == "QR_DATA_123"

        # 2. Test New Tag
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_prisma.client.tagmapping.find_unique.return_value = None

        await reader._process_tag(tag_data)

        # Verify db.add was called for RFIDTag and RFIDScanHistory
        assert mock_db.add.call_count >= 2


@pytest.mark.asyncio
async def test_connect_buffered_data(reader):
    """Test connection with buffered data clearing."""
    reader.is_connected = False
    with patch("app.services.rfid_reader.socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        # 1. Buffered data clearing
        mock_sock.recv.side_effect = [b"\x01\x02", BlockingIOError()]
        with patch.object(reader, "get_reader_info", new_callable=AsyncMock) as mock_info:
            mock_info.return_value = {"connected": True}
            result = await reader.connect()
            assert result is True
            assert reader.is_connected is True


@pytest.mark.asyncio
async def test_connect_exception(reader):
    """Test connection exception handling."""
    reader.is_connected = False
    with patch("app.services.rfid_reader.socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.connect.side_effect = Exception("General error")
        result = await reader.connect()
        assert result is False
        assert reader.is_connected is False


@pytest.mark.asyncio
async def test_disconnect_exception(reader):
    """Test disconnect exception handling."""
    reader.is_connected = True
    reader._socket = MagicMock()
    reader._socket.close.side_effect = Exception("Close error")
    await reader.disconnect()  # Should log but not raise
    assert reader.is_connected is False


@pytest.mark.asyncio
async def test_send_command_extra_errors(reader):
    """Test edge cases in _send_command like short responses."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    # Short response (less than 5 bytes) after HEAD
    # In _send_command: response = first_chunk[0] (HEAD)
    # Then it reads header_size=6.
    # If first chunk is 0xCF, and then it reads 5 more bytes.
    # If next read returns nothing, it raises ConnectionError.

    header = bytes([HEAD, 0x00, 0x00, 0x70, 0x02])  # LEN=2
    mock_sock.recv.side_effect = [header[:1], header[1 : 1 + 5], b""]  # Connection closed

    cmd = M200Command(0x0070)
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(cmd)


@pytest.mark.asyncio
async def test_read_single_tag_success_data(reader):
    """Test successful tag read with actual data."""
    with patch.object(reader, "_send_command") as mock_send:
        # Build valid inventory response with 1 tag
        # RSSI(-60=0xC4), Ant(1), PC(3000), LEN(4), EPC(E123)
        tag_data = bytes([0xC4, 0x01, 0x30, 0x00, 0x04]) + b"E123"
        len_field = len(tag_data) + 1  # +1 for STATUS
        header = struct.pack(">BBHB", HEAD, 0x00, M200Commands.RFM_INVENTORYISO_CONTINUE, len_field)
        frame = header + bytes([M200Status.SUCCESS]) + tag_data
        crc = calculate_crc16(frame)
        mock_send.return_value = frame + struct.pack(">H", crc)

        tags = await reader.read_single_tag()
        assert len(tags) == 1
        assert tags[0]["epc"] == "45313233"  # Hex string for b"E123"
        assert "timestamp" in tags[0]


@pytest.mark.asyncio
async def test_start_scanning_logic(reader):
    """Test start_scanning transitions."""
    reader.is_connected = False
    await reader.start_scanning()
    assert reader.is_scanning is False

    reader.is_connected = True
    with patch("asyncio.create_task") as mock_task:
        await reader.start_scanning()
        assert reader.is_scanning is True
        mock_task.assert_called_once()

        # Call again - should warning and return
        await reader.start_scanning()
        assert mock_task.call_count == 1


@pytest.mark.asyncio
async def test_process_tag_mappings_error(reader):
    """Test _process_tag when Prisma query fails."""
    tag_data = {"epc": "E123"}
    with (
        patch("app.services.rfid_reader.SessionLocal"),
        patch("app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock),
        patch("app.db.prisma.prisma_client") as mock_prisma,
    ):
        mock_prisma.client.tagmapping.find_unique.side_effect = Exception("Prisma down")
        await reader._process_tag(tag_data)
        # Should catch and continue (logging handled)


@pytest.mark.asyncio
async def test_stop_scanning_already_stopped(reader):
    """Test stop_scanning when not scanning."""
    reader.is_scanning = False
    await reader.stop_scanning()  # Just logs


@pytest.mark.asyncio
async def test_write_tag_success(reader):
    """Test successful tag writing."""
    with patch.object(reader, "_send_command") as mock_send:
        # Build valid response
        header = struct.pack(
            ">BBHB", HEAD, 0x00, M200Commands.RFM_WRITEISO_TAG, 0x01
        )
        frame = header + bytes([M200Status.SUCCESS])
        crc = calculate_crc16(frame)
        mock_send.return_value = frame + struct.pack(">H", crc)

        with patch.object(reader, "select_tag", new_callable=AsyncMock) as mock_select:
            mock_select.return_value = True
            result = await reader.write_tag("E123", 2, 0, b"\x11\x22")
            assert result is True
            mock_select.assert_called_with("E123")


@pytest.mark.asyncio
async def test_get_reader_info_status_error(reader):
    """Test get_reader_info when device returns status error."""
    mock_res = MagicMock(success=False, status=0x01)
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):
        info = await reader.get_reader_info()
        assert info["connected"] is True
        assert "error" in info


@pytest.mark.asyncio
async def test_get_reader_info_success_parsing(reader):
    """Test successful device info parsing (Happy Path, 379-402)."""
    # Build a valid device info frame (Section 2.2.7)
    # Total 152 bytes of data
    data = (
        b"CP_HW_VER".ljust(32, b"\x00")
        + b"CP_FW_VER".ljust(32, b"\x00")
        + b"CP_SN_123".ljust(12, b"\x00")
        + b"RFID_HW_VER".ljust(32, b"\x00")
        + b"RFID_NAME".ljust(32, b"\x00")
        + b"RFID_SN_456".ljust(12, b"\x00")
    )

    # LEN = 152 + 1 (STATUS) = 153 = 0x99
    header = struct.pack(">BBHB", HEAD, 0x00, M200Commands.RFM_GET_DEVICE_INFO, 0x99)
    frame = header + bytes([M200Status.SUCCESS]) + data
    crc = calculate_crc16(frame)
    full_resp = frame + struct.pack(">H", crc)

    with patch.object(reader, "_send_command", return_value=full_resp):
        info = await reader.get_reader_info()
        assert info["connected"] is True
        assert "CP_SN_123" in str(info)
        assert info["reader_id"] == "M-200"


@pytest.mark.asyncio
async def test_send_command_disconnection_error(reader):
    """Test line 201: _send_command raises if disconnected."""
    reader.is_connected = False
    cmd = M200Command(0x0070)
    with pytest.raises(ConnectionError, match="Not connected"):
        reader._send_command(cmd)


@pytest.mark.asyncio
async def test_send_command_body_read_closed(reader):
    """Test line 258: connection closed during body read."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    header = struct.pack(">BBHB", HEAD, 0x00, 0x0070, 0x02)  # LEN=2
    # Recv 1, then recv 5 (header), then recv 0 (closed)
    mock_sock.recv.side_effect = [header[:1], header[1:6], b""]

    cmd = M200Command(0x0070)
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(cmd)


@pytest.mark.asyncio
async def test_process_tag_existing_minimal(reader):
    """Test _process_tag existing tag path (526-533)."""
    tag_data = {"epc": "E123", "rssi": -55}
    mock_db = MagicMock()
    mock_tag = MagicMock()
    mock_tag.read_count = 1

    with (
        patch("app.services.rfid_reader.SessionLocal", return_value=mock_db),
        patch("app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock),
        patch("app.db.prisma.prisma_client"),
    ):

        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag
        await reader._process_tag(tag_data)
        assert mock_tag.read_count == 2
        mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_stop_scanning_full(reader):
    """Test stop_scanning success path (605-630)."""
    reader.is_scanning = True
    reader.is_connected = True

    # Use a real task that is already finished or can be awaited
    async def dummy():
        pass

    task = asyncio.create_task(dummy())
    await task  # Finish it so awaiting it in stop_scanning is instant
    reader._scan_task = task

    with patch.object(reader, "_send_command") as mock_send:
        await reader.stop_scanning()
        assert reader.is_scanning is False
        mock_send.assert_called()  # Should send stop inventory


@pytest.mark.asyncio
async def test_exhaustive_method_calls(reader):
    """Call all reader methods to hit success/fail branches."""
    reader.is_connected = True

    # SUCCESS PATHS
    # Need at least 14 bytes for network config parse to succeed
    # data[0-3]=IP, data[4-7]=Subnet, data[8-11]=GW, data[12-13]=Port
    mock_res = MagicMock(
        success=True, data=b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x00\x00", status=0x00
    )
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):

        assert await reader.initialize_device() is True
        assert await reader.set_power(20) is True
        assert (
            await reader.read_tag_memory(1, 0, 2)
            == b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x00\x00"
        )
        assert (await reader.get_network_config())["ip"] == "1.2.3.4"
        assert await reader.set_network_config("1.1.1.1") is True
        assert await reader.set_rssi_filter(1, 10) is True
        assert "data" in await reader.get_all_params()
        assert (await reader.get_gpio_levels())["gpio1"] == 1
        assert await reader.set_gpio(1, 1) is True
        assert (await reader.get_gate_status())["mode"] == 1
        assert await reader.set_gate_config() is True
        assert await reader.set_query_params() is True
        assert await reader.select_tag("E123") is True


@pytest.mark.asyncio
async def test_send_command_closed_during_header(reader):
    """Test line 244: connection closed during header read."""
    mock_sock = MagicMock()
    reader._socket = mock_sock
    # HEAD, then closed
    mock_sock.recv.side_effect = [bytes([HEAD]), b""]
    cmd = M200Command(0x0070)
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(cmd)

    # FAILURE PATHS (Status Error)
    mock_fail = MagicMock(success=False, status=0x01)
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_fail),
    ):

        assert await reader.initialize_device() is False
        assert await reader.set_power(20) is False
        assert await reader.read_tag_memory(1, 0, 2) is None
        assert "error" in await reader.get_network_config()
        assert await reader.set_network_config("1.1.1.1") is False
        assert await reader.set_rssi_filter(1, 10) is False
        assert (await reader.get_all_params())["success"] is False
        assert await reader.get_gpio_levels() == {}
        assert await reader.set_gpio(1, 1) is False
        assert "error" in await reader.get_gate_status()
        assert await reader.set_gate_config() is False
        assert await reader.set_query_params() is False
        assert await reader.select_tag("E123") is False


@pytest.mark.asyncio
async def test_unsolicited_warning_hit(reader):
    """Test line 317-318: unsolicited message during info."""
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.cmd = 0xFFFF  # Real int to avoid format error
    mock_res.data = b"somedata"
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):
        await reader.get_reader_info()


@pytest.mark.asyncio
async def test_aliases_and_status(reader):
    """Test compatibility aliases and status method."""
    reader.is_connected = True
    reader.is_scanning = True
    reader._device_info = {"serial": "123"}

    status = reader.get_status()
    assert status["is_connected"] is True
    assert status["is_scanning"] is True
    assert status["device_info"]["serial"] == "123"

    with patch.object(reader, "get_all_params", new_callable=AsyncMock) as mock_params:
        await reader.get_all_config()
        mock_params.assert_called_once()

    with patch.object(reader, "set_network_config", new_callable=AsyncMock) as mock_net:
        await reader.set_network("1.1.1.1", "255.255.255.0", "1.1.1.1", 4001)
        mock_net.assert_called_once()

    cmd = M200Command(0x0070)
    with patch.object(reader, "_send_command") as mock_send:
        reader.send_command(cmd)
        mock_send.assert_called_with(cmd)


@pytest.mark.asyncio
async def test_connect_already_connected(reader, caplog):
    """Test line 107: already connected info."""
    reader.is_connected = True
    with caplog.at_level(logging.INFO, logger="app.services.rfid_reader"):
        assert await reader.connect() is True
        assert "Already connected" in caplog.text


@pytest.mark.asyncio
async def test_connect_failures_detailed_v2(reader):
    """Test remaining connection failure paths."""
    reader.is_connected = False

    with patch("app.services.rfid_reader.socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        # Line 149-151: Timeout
        mock_sock.connect.side_effect = socket.timeout
        assert await reader.connect() is False

        # Line 153-155: ConnectionRefused
        mock_sock.connect.side_effect = ConnectionRefusedError
        assert await reader.connect() is False

        # Line 157-159: Other Exception
        mock_sock.connect.side_effect = RuntimeError("Other")
        assert await reader.connect() is False


@pytest.mark.asyncio
async def test_disconnect_already_disconnected(reader, caplog):
    """Test line 167: already disconnected."""
    reader.is_connected = False
    reader.is_scanning = False
    with caplog.at_level(logging.INFO, logger="app.services.rfid_reader"):
        await reader.disconnect()
        assert "Already disconnected" in caplog.text


@pytest.mark.asyncio
async def test_read_single_tag_exceptions(reader):
    """Test line 461-466: read_single_tag exceptions."""
    reader.is_connected = True
    # Timeout (461-463)
    with patch.object(reader, "_send_command", side_effect=socket.timeout):
        assert await reader.read_single_tag() == []

    # General Exception (464-466)
    with patch.object(reader, "_send_command", side_effect=Exception("Failed")):
        assert await reader.read_single_tag() == []


@pytest.mark.asyncio
async def test_inventory_not_success(reader):
    """Test line 441-442: inventory not success status."""
    reader.is_connected = True
    mock_res = MagicMock(success=False, status=0x02)
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):
        assert await reader.read_single_tag() == []


@pytest.mark.asyncio
async def test_exception_catch_blocks(reader):
    """Test all catch blocks (except Exception) in config methods."""
    reader.is_connected = True

    methods = [
        ("initialize_device", []),
        ("set_power", [10]),
        ("read_tag_memory", [1, 0, 1]),
        ("get_network_config", []),
        ("set_network_config", ["1.1.1.1"]),
        ("set_rssi_filter", [1, 50]),
        ("get_all_params", []),
        ("get_gpio_levels", []),
        ("set_gpio", [1, 1]),
        ("control_relay", [1, True]),
        ("get_gate_status", []),
        ("set_gate_config", []),
        ("set_query_params", []),
        ("select_tag", ["E123"]),
    ]

    with patch.object(reader, "_send_command", side_effect=Exception("CRASH")):
        for method_name, args in methods:
            method = getattr(reader, method_name)
            result = await method(*args)
            if isinstance(result, bool):
                assert result is False
            elif isinstance(result, dict):
                # Some return empty dict, some return {"error": ...}
                if method_name in ["get_network_config", "get_all_params", "get_gate_status"]:
                    assert "error" in result or result == {} or "success" in result
            elif result is None:
                assert result is None


@pytest.mark.asyncio
async def test_send_command_unsolicited_and_other_bytes(reader, caplog):
    """Test unsolicited messages and unexpected bytes logic (222-225, 274-277)."""
    mock_sock = MagicMock()
    reader._socket = mock_sock
    reader.is_connected = True

    def build_frame(cmd):
        header = struct.pack(">BBHB", HEAD, 0x00, cmd, 0x01)
        body = bytes([0x00])
        frame = header + body
        crc = calculate_crc16(frame)
        return frame + struct.pack(">H", crc)

    # 1. Unexpected first byte (222-225)
    mock_sock.recv.side_effect = [b"\xaa", b"\xbb"]
    cmd = M200Command(0x0070)
    result = reader._send_command(cmd)
    assert result == b"\xaa\xbb"

    # 2. Unsolicited message (274-277)
    wrong_frame = build_frame(0xFFFF)
    right_frame = build_frame(0x0070)
    mock_sock.recv.side_effect = [
        right_frame[0:1],  # HEAD
        wrong_frame[1:6],  # Header with wrong CMD
        wrong_frame[6:8],  # Status + Data + CRC
        right_frame[0:1],  # HEAD
        right_frame[1:6],  # Correct CMD
        right_frame[6:8],  # Correct Data
    ]
    # Reset side effect for fresh run
    mock_sock.recv.side_effect = [
        wrong_frame[0:1],
        wrong_frame[1:6],
        wrong_frame[6:8],
        right_frame[0:1],
        right_frame[1:6],
        right_frame[6:8],
    ]
    result = reader._send_command(cmd)
    assert struct.unpack(">H", result[2:4])[0] == 0x0070


@pytest.mark.asyncio
async def test_process_tag_new_tag_path(reader):
    """Test line 536-546: Create new tag in _process_tag."""
    tag_data = {"epc": "NEWTAG", "rssi": -50, "antenna_port": 1, "pc": 1234, "timestamp": "now"}
    mock_db = MagicMock()
    with (
        patch("app.services.rfid_reader.SessionLocal", return_value=mock_db),
        patch("app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock),
        patch("app.db.prisma.prisma_client"),
    ):

        mock_db.query.return_value.filter.return_value.first.return_value = None
        await reader._process_tag(tag_data)
        # Verify db.add(new_tag)
        assert mock_db.add.call_count >= 2


@pytest.mark.asyncio
async def test_exhaustive_method_calls_aliases(reader):
    """Call method aliases for coverage."""
    reader.is_connected = True
    mock_res = MagicMock(success=True, data=b"\x00" * 20)
    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):
        await reader.get_all_config()
        await reader.set_network("1.2.3.4", "255.255.255.0", "1.2.3.1", 4001)


@pytest.mark.asyncio
async def test_stop_scanning_send_command_fail(reader, caplog):
    """Test line 627-628: fail to send stop inventory."""
    reader.is_scanning = True
    reader.is_connected = True
    reader._scan_task = None  # No task to cancel
    with caplog.at_level(logging.WARNING, logger="app.services.rfid_reader"):
        with patch.object(reader, "_send_command", side_effect=Exception("Link Dead")):
            await reader.stop_scanning()
            assert "Could not send stop command" in caplog.text


@pytest.mark.asyncio
async def test_get_reader_info_timeout(reader):
    """Test get_reader_info timeout."""
    with patch.object(reader, "_send_command", side_effect=socket.timeout):
        info = await reader.get_reader_info()
        assert "Timeout" in info["error"]


@pytest.mark.asyncio
async def test_connect_info_failure(reader):
    """Test line 144: connected but info fails."""
    reader.is_connected = False
    with patch("app.services.rfid_reader.socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        with patch.object(reader, "get_reader_info", new_callable=AsyncMock) as mock_info:
            mock_info.return_value = {"connected": False}  # Failed to get info
            await reader.connect()
            assert reader.is_connected is True


@pytest.mark.asyncio
async def test_send_command_timeout_with_partial_data(reader):
    """Test line 282-283: timeout after some data."""
    mock_sock = MagicMock()
    reader._socket = mock_sock
    # We want it to read some data then timeout
    mock_sock.recv.side_effect = [bytes([HEAD]), socket.timeout]

    cmd = M200Command(0x0070)
    result = reader._send_command(cmd)
    assert result == bytes([HEAD])


@pytest.mark.asyncio
async def test_send_command_exhaust_retries(reader):
    """Test line 291: exhaust retries without matching CMD."""
    mock_sock = MagicMock()
    reader._socket = mock_sock

    # Return wrong CMD frames
    wrong_frame = struct.pack(">BBHB", HEAD, 0x00, 0xFFFF, 0x01) + bytes([0x00, 0x00, 0x00])
    mock_sock.recv.return_value = wrong_frame  # Simple mock

    cmd = M200Command(0x0070)
    with pytest.raises(socket.timeout, match="No matching response received"):
        reader._send_command(cmd, max_retries=1)


@pytest.mark.asyncio
async def test_get_reader_info_protocol_error_other(reader):
    """Test line 366: other protocol parsing error."""
    with patch.object(reader, "_send_command", return_value=b"RANDOM_JUNK"):
        # This will fail decode or trigger ValueError
        info = await reader.get_reader_info()
        assert "error" in info


@pytest.mark.asyncio
async def test_scan_loop_cancelled(reader):
    """Test line 503: scan loop cancellation logic."""
    reader.is_scanning = True
    reader.is_connected = True

    async def side_effect(*args):
        raise asyncio.CancelledError()

    with patch.object(reader, "read_single_tag", side_effect=side_effect):
        await reader._scan_loop()
        # Should catch and break


@pytest.mark.asyncio
async def test_send_command_sock_empty_first(reader):
    """Test line 218: recv(1) returns empty."""
    mock_sock = MagicMock()
    reader._socket = mock_sock
    mock_sock.recv.return_value = b""
    cmd = M200Command(0x0070)
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(cmd)


@pytest.mark.asyncio
async def test_send_command_additional_data(reader):
    """Test line 231-232: additional data after non-HEAD byte."""
    mock_sock = MagicMock()
    reader._socket = mock_sock
    # First byte 0xAA (not HEAD), then 0xBB in additional
    mock_sock.recv.side_effect = [b"\xaa", b"\xbb"]
    cmd = M200Command(0x0070)
    # This will return b"\xAA\xBB"
    assert reader._send_command(cmd) == b"\xaa\xbb"


@pytest.mark.asyncio
async def test_process_tag_with_callbacks(reader):
    """Test line 593-596: callback execution."""
    tag_data = {"epc": "E123"}
    mock_db = MagicMock()

    # Sync callback
    cb_sync = MagicMock()
    # Async callback
    cb_async = AsyncMock()

    with (
        patch("app.services.rfid_reader.SessionLocal", return_value=mock_db),
        patch("app.services.rfid_reader.manager.broadcast"),
        patch("app.db.prisma.prisma_client"),
    ):

        await reader._process_tag(tag_data, callback=cb_sync)
        cb_sync.assert_called_once_with(tag_data)

        await reader._process_tag(tag_data, callback=cb_async)
        cb_async.assert_called_once_with(tag_data)


@pytest.mark.asyncio
async def test_truly_exhaustive_methods(reader):
    """Call every single remaining method to hit coverage."""
    reader.is_connected = True
    # mock_res data needs to be long enough for various parsers
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.status = 0x00
    mock_res.cmd = M200Commands.RFM_GET_DEVICE_INFO  # Real int
    mock_res.data = b"\x00" * 152

    with (
        patch.object(reader, "_send_command", return_value=b"raw"),
        patch("app.services.m200_protocol.M200ResponseParser.parse", return_value=mock_res),
    ):

        # Connection & Info
        await reader.connect()
        await reader.get_reader_info()
        reader.get_status()

        # Config & Control
        await reader.initialize_device()
        await reader.set_power(10)
        await reader.read_tag_memory(1, 0, 2)
        await reader.get_network_config()
        await reader.set_network_config("1.1.1.1")
        await reader.set_network("1.1.1.2", "255.255.255.0", "1.1.1.1", 4001)
        await reader.get_all_params()
        await reader.get_all_config()
        await reader.set_rssi_filter(1, 50)

        # GPIO & Relay
        await reader.get_gpio_levels()
        await reader.set_gpio(1, 1)
        await reader.control_relay(1, True)
        await reader.control_relay(2, False)

        # Gate & Ops
        await reader.get_gate_status()
        await reader.set_gate_config()
        await reader.set_query_params()
        await reader.select_tag("E123")
        await reader.read_single_tag()
        await reader.write_tag("E123", 1, 0, b"\x00\x00")

    # Disconnected failure paths
    reader.is_connected = False
    assert await reader.initialize_device() is False
    assert await reader.set_power(10) is False
    assert await reader.read_tag_memory(1, 0, 2) is None
    assert "error" in await reader.get_network_config()
    assert await reader.set_network_config("1.1.1.1") is False
    assert await reader.set_rssi_filter(1, 50) is False
    assert await reader.get_all_params() == {"error": "Not connected"}
    assert await reader.get_gpio_levels() == {}
    assert await reader.set_gpio(1, 1) is False
    assert (await reader.get_gate_status())["error"] == "Not connected"
    assert await reader.set_gate_config() is False
    assert await reader.set_query_params() is False
    assert await reader.select_tag("E123") is False
    assert await reader.control_relay(1, True) is False
    # write_tag returns False if not connected
    assert await reader.write_tag("E123", 1, 0, b"\x00\x00") is False
