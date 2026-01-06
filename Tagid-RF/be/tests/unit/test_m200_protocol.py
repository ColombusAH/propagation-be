"""Unit tests for M200 protocol implementation."""

import pytest

from app.services.m200_protocol import (
    M200Command,
    M200Commands,
    M200ResponseParser,
    M200Status,
    build_get_device_info_command,
    build_inventory_command,
    build_stop_inventory_command,
    calculate_crc16,
)


@pytest.mark.unit
class TestCRC16:
    """Tests for CRC16 calculation."""

    def test_crc16_empty_bytes(self):
        """Test CRC16 with empty bytes."""
        result = calculate_crc16(b"")
        assert isinstance(result, int)

    def test_crc16_simple_bytes(self):
        """Test CRC16 with simple byte sequence."""
        result = calculate_crc16(b"\x01\x02\x03")
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_crc16_consistent(self):
        """Test CRC16 produces consistent results."""
        data = b"\xCF\xFF\x00\x70\x00"
        crc1 = calculate_crc16(data)
        crc2 = calculate_crc16(data)
        assert crc1 == crc2


@pytest.mark.unit
class TestM200Command:
    """Tests for M200Command class."""

    def test_command_initialization(self):
        """Test M200Command initialization."""
        cmd = M200Command(cmd=0x0070, data=b"", addr=0xFF)
        assert cmd.cmd == 0x0070
        assert cmd.addr == 0xFF
        assert cmd.data == b""

    def test_command_serialize(self):
        """Test command serialization produces valid bytes."""
        cmd = M200Command(cmd=0x0070, data=b"", addr=0xFF)
        serialized = cmd.serialize()

        assert isinstance(serialized, bytes)
        assert len(serialized) >= 7  # HEAD + ADDR + CMD(2) + LEN + CRC(2)
        assert serialized[0] == 0xCF  # HEAD byte

    def test_command_with_data(self):
        """Test command with data payload."""
        cmd = M200Command(cmd=0x0001, data=b"\x00\x01", addr=0xFF)
        serialized = cmd.serialize()

        assert len(serialized) == 9  # HEAD + ADDR + CMD(2) + LEN + DATA(2) + CRC(2)

    def test_command_repr(self):
        """Test command string representation."""
        cmd = M200Command(cmd=0x0070, data=b"", addr=0xFF)
        repr_str = repr(cmd)

        assert "M200Command" in repr_str
        assert "0xFF" in repr_str
        assert "0x0070" in repr_str


@pytest.mark.unit
class TestM200Status:
    """Tests for M200Status class."""

    def test_status_success(self):
        """Test SUCCESS status code."""
        assert M200Status.SUCCESS == 0x00

    def test_status_inventory_complete(self):
        """Test INVENTORY_COMPLETE status code."""
        assert M200Status.INVENTORY_COMPLETE == 0x12

    def test_get_description_known_status(self):
        """Test get_description for known status."""
        desc = M200Status.get_description(0x00)
        assert desc == "Success"

    def test_get_description_unknown_status(self):
        """Test get_description for unknown status."""
        desc = M200Status.get_description(0x99)
        assert "Unknown" in desc


@pytest.mark.unit
class TestM200CommandBuilders:
    """Tests for command builder functions."""

    def test_build_inventory_command(self):
        """Test building inventory command."""
        cmd = build_inventory_command(inv_type=0x00, inv_param=0)

        assert cmd.cmd == M200Commands.RFM_INVENTORYISO_CONTINUE
        assert len(cmd.data) == 2

    def test_build_stop_inventory_command(self):
        """Test building stop inventory command."""
        cmd = build_stop_inventory_command()

        assert cmd.cmd == M200Commands.RFM_INVENTORY_STOP
        assert cmd.data == b""

    def test_build_get_device_info_command(self):
        """Test building get device info command."""
        cmd = build_get_device_info_command()

        assert cmd.cmd == M200Commands.RFM_GET_DEVICE_INFO
        assert cmd.data == b""
        assert cmd.addr == 0xFF  # Broadcast address


@pytest.mark.unit
class TestM200Commands:
    """Tests for M200Commands constants."""

    def test_inventory_command_value(self):
        """Test inventory command value."""
        assert M200Commands.RFM_INVENTORYISO_CONTINUE == 0x0001

    def test_get_device_info_command_value(self):
        """Test get device info command value."""
        assert M200Commands.RFM_GET_DEVICE_INFO == 0x0070

    def test_stop_inventory_command_value(self):
        """Test stop inventory command value."""
        assert M200Commands.RFM_INVENTORY_STOP == 0x0028
