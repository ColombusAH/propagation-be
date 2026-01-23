"""
Tests for M200 Protocol - CRC calculation, command building, response parsing.
"""

import struct

import pytest

from app.services.m200_protocol import (
    BROADCAST_ADDR,
    HEAD,
    M200Command,
    M200Commands,
    M200Response,
    M200ResponseParser,
    M200Status,
    build_get_device_info_command,
    build_inventory_command,
    build_relay1_command,
    build_relay2_command,
    build_set_network_command,
    build_set_power_command,
    build_stop_inventory_command,
    calculate_crc16,
    parse_device_info,
    parse_inventory_response,
    parse_network_response,
)


class TestCRC16:
    """Test CRC16 calculation."""

    def test_crc_empty(self):
        """CRC of empty data."""
        crc = calculate_crc16(b"")
        assert crc == 0xFFFF  # Initial preset value

    def test_crc_known_value(self):
        """CRC of known test data should be consistent."""
        data = bytes([0xCF, 0xFF, 0x00, 0x70, 0x00])  # Get device info frame
        crc1 = calculate_crc16(data)
        crc2 = calculate_crc16(data)
        assert crc1 == crc2

    def test_crc_different_data(self):
        """Different data should produce different CRC."""
        crc1 = calculate_crc16(b"\x01\x02\x03")
        crc2 = calculate_crc16(b"\x01\x02\x04")
        assert crc1 != crc2


class TestM200Command:
    """Test command building."""

    def test_build_get_device_info(self):
        """Test get device info command structure."""
        cmd = build_get_device_info_command()

        assert cmd.cmd == M200Commands.RFM_GET_DEVICE_INFO
        assert cmd.addr == BROADCAST_ADDR
        assert len(cmd.data) == 0

    def test_command_serialize(self):
        """Test command serialization."""
        cmd = M200Command(cmd=0x0070, data=b"", addr=0xFF)
        frame = cmd.serialize()

        # Check header
        assert frame[0] == HEAD  # 0xCF
        assert frame[1] == 0xFF  # Broadcast addr
        # CMD is 2 bytes big-endian
        assert struct.unpack(">H", frame[2:4])[0] == 0x0070
        # LEN
        assert frame[4] == 0  # No data
        # CRC is last 2 bytes
        assert len(frame) == 7  # HEAD + ADDR + CMD(2) + LEN + CRC(2)

    def test_build_set_power(self):
        """Test set power command."""
        cmd = build_set_power_command(26)

        assert cmd.cmd == M200Commands.RFM_SET_PWR
        assert cmd.data == bytes([26])

    def test_build_inventory(self):
        """Test inventory command with parameters."""
        cmd = build_inventory_command(inv_type=0x01, inv_param=10)

        assert cmd.cmd == M200Commands.RFM_INVENTORYISO_CONTINUE
        assert cmd.data == bytes([0x01, 10])

    def test_build_relay_commands(self):
        """Test relay control commands."""
        cmd1 = build_relay1_command(close=True)
        cmd2 = build_relay2_command(close=False)

        assert cmd1.cmd == M200Commands.RFM_RELEASE_CLOSE_RELAY1
        assert cmd1.data == bytes([0x01])

        assert cmd2.cmd == M200Commands.RFM_RELEASE_CLOSE_RELAY2
        assert cmd2.data == bytes([0x00])


class TestM200ResponseParser:
    """Test response parsing."""

    def _build_frame(self, cmd: int, status: int, data: bytes) -> bytes:
        """Helper to build a valid frame."""
        addr = 0x00
        length = 1 + len(data)  # STATUS + DATA
        frame_body = struct.pack(">BBHB B", HEAD, addr, cmd, length, status) + data
        crc = calculate_crc16(frame_body)
        return frame_body + struct.pack(">H", crc)

    def test_parse_success_response(self):
        """Parse a simple success response."""
        frame = self._build_frame(M200Commands.RFM_GET_DEVICE_INFO, M200Status.SUCCESS, b"")

        response = M200ResponseParser.parse(frame, strict_crc=False)

        assert response.success is True
        assert response.status == M200Status.SUCCESS
        assert response.cmd == M200Commands.RFM_GET_DEVICE_INFO

    def test_parse_error_response(self):
        """Parse an error response."""
        frame = self._build_frame(0x0070, M200Status.COMMAND_FAILED, b"")

        response = M200ResponseParser.parse(frame, strict_crc=False)

        assert response.success is False
        assert response.status == M200Status.COMMAND_FAILED

    def test_parse_with_data(self):
        """Parse response with data payload."""
        test_data = b"HelloWorld"
        frame = self._build_frame(0x0070, M200Status.SUCCESS, test_data)

        response = M200ResponseParser.parse(frame, strict_crc=False)

        assert response.data == test_data

    def test_parse_invalid_header(self):
        """Invalid header should raise ValueError."""
        bad_frame = b"\x00\x00\x00\x70\x01\x00\xab\xcd"

        with pytest.raises(ValueError, match="Invalid HEAD"):
            M200ResponseParser.parse(bad_frame, strict_crc=False)

    def test_parse_too_short(self):
        """Too short frame should raise ValueError."""
        with pytest.raises(ValueError, match="too short"):
            M200ResponseParser.parse(b"\xcf\x00", strict_crc=False)


class TestDeviceInfoParsing:
    """Test device info response parsing."""

    def test_parse_full_device_info(self):
        """Parse complete device info (152 bytes)."""
        data = (
            b"HW_VER_TEST".ljust(32, b"\x00")
            + b"FW_VER_TEST".ljust(32, b"\x00")
            + b"SN123456".ljust(12, b"\x00")
            + b"RFID_HW_V1".ljust(32, b"\x00")
            + b"M-200-READER".ljust(32, b"\x00")
            + b"RFID_SN_ABC".ljust(12, b"\x00")
        )

        info = parse_device_info(data)

        assert info["cp_hardware_version"] == "HW_VER_TEST"
        assert info["cp_firmware_version"] == "FW_VER_TEST"
        assert info["cp_serial_number"] == "SN123456"
        assert info["rfid_module_name"] == "M-200-READER"


class TestInventoryParsing:
    """Test inventory response parsing."""

    def test_parse_single_tag(self):
        """Parse single tag from inventory."""
        # RSSI + ANT + PC(2) + LEN + EPC
        tag_data = bytes([60, 1, 0x30, 0x00, 4]) + bytes.fromhex("E2806810")

        tags = parse_inventory_response(tag_data)

        assert len(tags) == 1
        assert tags[0]["epc"] == "E2806810"
        assert tags[0]["rssi"] == -60  # Negated
        assert tags[0]["antenna_port"] == 1

    def test_parse_multiple_tags(self):
        """Parse multiple tags."""
        tag1 = bytes([50, 1, 0x30, 0x00, 2]) + bytes.fromhex("AAAA")
        tag2 = bytes([55, 2, 0x30, 0x00, 2]) + bytes.fromhex("BBBB")

        tags = parse_inventory_response(tag1 + tag2)

        assert len(tags) == 2
        assert tags[0]["epc"] == "AAAA"
        assert tags[1]["epc"] == "BBBB"

    def test_parse_empty_inventory(self):
        """Empty data should return empty list."""
        tags = parse_inventory_response(b"")
        assert tags == []


class TestNetworkConfig:
    """Test network configuration commands and parsing."""

    def test_build_set_network(self):
        """Test network config command building."""
        cmd = build_set_network_command(
            ip="192.168.1.100", subnet="255.255.255.0", gateway="192.168.1.1", port=4001
        )

        assert cmd.cmd == M200Commands.RFM_SET_GET_NETPARA
        assert len(cmd.data) > 0

    def test_parse_network_response(self):
        """Test network config response parsing."""
        # IP(4) + Subnet(4) + Gateway(4) + Port(2)
        data = bytes([192, 168, 1, 100, 255, 255, 255, 0, 192, 168, 1, 1]) + struct.pack(">H", 4001)

        config = parse_network_response(data)

        assert config["ip"] == "192.168.1.100"
        assert config["subnet"] == "255.255.255.0"
        assert config["gateway"] == "192.168.1.1"
        assert config["port"] == 4001
