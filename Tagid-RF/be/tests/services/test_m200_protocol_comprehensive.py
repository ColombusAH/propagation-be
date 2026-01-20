"""
Comprehensive tests for M200 Protocol to improve code coverage.
"""

import struct

import pytest

from app.services.m200_protocol import (
    HEAD,
    POLYNOMIAL,
    PRESET_VALUE,
    M200Command,
    M200Commands,
    M200Response,
    M200ResponseParser,
    M200Status,
    build_get_all_params_command,
    build_get_device_info_command,
    build_get_eas_mask_command,
    build_get_gate_param_command,
    build_get_gate_status_command,
    build_get_gpio_levels_command,
    build_get_gpio_param_command,
    build_get_network_command,
    build_get_query_param_command,
    build_get_remote_server_command,
    build_get_rf_protocol_command,
    build_get_rssi_filter_command,
    build_get_select_param_command,
    build_inventory_command,
    build_module_init_command,
    build_read_tag_command,
    build_relay1_command,
    build_relay2_command,
    build_select_tag_command,
    build_set_all_params_command,
    build_set_eas_mask_command,
    build_set_gate_param_command,
    build_set_gpio_param_command,
    build_set_network_command,
    build_set_power_command,
    build_set_query_param_command,
    build_set_remote_server_command,
    build_set_rf_protocol_command,
    build_set_rssi_filter_command,
    build_set_select_param_command,
    build_set_wifi_command,
    build_stop_inventory_command,
    calculate_crc16,
    parse_device_info,
    parse_gate_status,
    parse_gpio_levels,
    parse_inventory_response,
    parse_network_response,
)


class TestCRC16:
    """Tests for CRC16 calculation."""

    def test_crc16_empty_bytes(self):
        """Test CRC16 with empty bytes."""
        result = calculate_crc16(b"")
        assert isinstance(result, int)
        assert result == PRESET_VALUE

    def test_crc16_single_byte(self):
        """Test CRC16 with single byte."""
        result = calculate_crc16(b"\x00")
        assert isinstance(result, int)

    def test_crc16_multiple_bytes(self):
        """Test CRC16 with multiple bytes."""
        result = calculate_crc16(b"\xcf\x00\x00\x70\x00")
        assert isinstance(result, int)


class TestM200Response:
    """Tests for M200Response dataclass."""

    def test_response_success_status_zero(self):
        """Test success property returns True for status 0."""
        response = M200Response(addr=0, cmd=0x0070, status=0, data=b"", crc=0)
        assert response.success is True

    def test_response_success_status_nonzero(self):
        """Test success property returns False for non-zero status."""
        response = M200Response(addr=0, cmd=0x0070, status=0x12, data=b"", crc=0)
        assert response.success is False


class TestM200Command:
    """Tests for M200Command class."""

    def test_command_serialize(self):
        """Test command serialization."""
        cmd = M200Command(cmd=0x0070, data=b"", addr=0xFF)
        serialized = cmd.serialize()
        assert serialized[0] == HEAD
        assert len(serialized) >= 7  # HEAD + ADDR + CMD(2) + LEN + CRC(2)

    def test_command_serialize_with_data(self):
        """Test command serialization with data."""
        cmd = M200Command(cmd=0x0053, data=b"\x1a", addr=0xFF)
        serialized = cmd.serialize()
        assert len(serialized) == 8  # HEAD + ADDR + CMD(2) + LEN + DATA(1) + CRC(2)

    def test_command_repr(self):
        """Test command string representation."""
        cmd = M200Command(cmd=0x0070, data=b"test", addr=0xFF)
        repr_str = repr(cmd)
        assert "M200Command" in repr_str
        assert "0xFF" in repr_str
        assert "0x0070" in repr_str

    def test_command_data_too_long(self):
        """Test command with data exceeding 255 bytes raises error."""
        cmd = M200Command(cmd=0x0070, data=b"x" * 256, addr=0xFF)
        with pytest.raises(ValueError, match="Data too long"):
            cmd.serialize()


class TestM200ResponseParser:
    """Tests for M200ResponseParser class."""

    def test_parse_valid_frame(self):
        """Test parsing a valid response frame."""
        # Build a valid frame manually
        # HEAD=0xCF, ADDR=0xFF, CMD=0x0070, LEN=0x01, STATUS=0x00, CRC
        frame_without_crc = struct.pack(">BBHBB", HEAD, 0xFF, 0x0070, 0x01, 0x00)
        crc = calculate_crc16(frame_without_crc)
        frame = frame_without_crc + struct.pack(">H", crc)

        response = M200ResponseParser.parse(frame)
        assert response.addr == 0xFF
        assert response.cmd == 0x0070
        assert response.status == 0x00
        assert response.success is True

    def test_parse_frame_too_short(self):
        """Test parsing frame that's too short."""
        with pytest.raises(ValueError, match="Frame too short"):
            M200ResponseParser.parse(b"\xcf\x00\x00")

    def test_parse_invalid_head(self):
        """Test parsing frame with invalid HEAD byte."""
        frame = b"\x00\xff\x00\x70\x01\x00\x00\x00"
        with pytest.raises(ValueError, match="Invalid HEAD"):
            M200ResponseParser.parse(frame)

    def test_parse_crc_mismatch_lenient(self):
        """Test parsing frame with CRC mismatch in lenient mode."""
        # Build frame with wrong CRC
        frame_without_crc = struct.pack(">BBHBB", HEAD, 0xFF, 0x0070, 0x01, 0x00)
        frame = frame_without_crc + b"\x00\x00"  # Wrong CRC

        # Should not raise, just log warning
        response = M200ResponseParser.parse(frame, strict_crc=False)
        assert response.status == 0x00

    def test_parse_crc_mismatch_strict(self):
        """Test parsing frame with CRC mismatch in strict mode."""
        frame_without_crc = struct.pack(">BBHBB", HEAD, 0xFF, 0x0070, 0x01, 0x00)
        frame = frame_without_crc + b"\x00\x00"  # Wrong CRC

        with pytest.raises(ValueError, match="CRC mismatch"):
            M200ResponseParser.parse(frame, strict_crc=True)

    def test_parse_invalid_length(self):
        """Test parsing frame with invalid length field."""
        # LEN says 5, but actual data is only 1 byte
        frame = struct.pack(">BBHBB", HEAD, 0xFF, 0x0070, 0x05, 0x00)
        frame += b"\x00\x00"  # Add some CRC bytes

        with pytest.raises(ValueError, match="Invalid frame length"):
            M200ResponseParser.parse(frame)


class TestM200Status:
    """Tests for M200Status class."""

    def test_get_description_success(self):
        """Test getting description for SUCCESS status."""
        desc = M200Status.get_description(M200Status.SUCCESS)
        assert desc == "Success"

    def test_get_description_inventory_complete(self):
        """Test getting description for INVENTORY_COMPLETE status."""
        desc = M200Status.get_description(M200Status.INVENTORY_COMPLETE)
        assert "Inventory" in desc or "complete" in desc.lower()

    def test_get_description_unknown(self):
        """Test getting description for unknown status."""
        desc = M200Status.get_description(0xAB)
        assert "Unknown" in desc or "0xAB" in desc.upper()


class TestParseDeviceInfo:
    """Tests for parse_device_info function."""

    def test_parse_full_device_info(self):
        """Test parsing full 152-byte device info."""
        # Create 152 bytes of device info
        data = b"CP_HW_VERSION".ljust(32, b"\x00")
        data += b"CP_FW_VERSION".ljust(32, b"\x00")
        data += b"CP_SERIAL".ljust(12, b"\x00")
        data += b"RFID_HW_VER".ljust(32, b"\x00")
        data += b"RFID_MODULE".ljust(32, b"\x00")
        data += b"RFID_SERIAL".ljust(12, b"\x00")

        info = parse_device_info(data)

        assert info["cp_hardware_version"] == "CP_HW_VERSION"
        assert info["cp_firmware_version"] == "CP_FW_VERSION"
        assert info["cp_serial_number"] == "CP_SERIAL"
        assert info["rfid_hardware_version"] == "RFID_HW_VER"
        assert info["rfid_module_name"] == "RFID_MODULE"
        assert info["rfid_serial_number"] == "RFID_SERIAL"
        assert info["model"] == "M-200"

    def test_parse_short_device_info(self):
        """Test parsing device info with less than expected bytes."""
        data = b"SHORT_DATA".ljust(50, b"\x00")
        info = parse_device_info(data)

        # Should still parse what it can
        assert "cp_hardware_version" in info


class TestParseInventoryResponse:
    """Tests for parse_inventory_response function."""

    def test_parse_empty_inventory(self):
        """Test parsing empty inventory response."""
        tags = parse_inventory_response(b"")
        assert tags == []

    def test_parse_single_tag(self):
        """Test parsing single tag in inventory."""
        # RSSI(1) + ANT(1) + PC(2) + EPC_LEN(1) + EPC(12)
        epc = bytes.fromhex("E20000001234567890AB")
        data = struct.pack(">BB", 50, 1)  # RSSI=50, Ant=1
        data += struct.pack(">H", 0x3000)  # PC
        data += bytes([len(epc)])  # EPC length
        data += epc

        tags = parse_inventory_response(data)

        assert len(tags) == 1
        assert tags[0]["rssi"] == -50
        assert tags[0]["antenna_port"] == 1

    def test_parse_multiple_tags(self):
        """Test parsing multiple tags in inventory."""
        epc1 = bytes.fromhex("E20000001111")
        epc2 = bytes.fromhex("E20000002222")

        data = b""
        for epc in [epc1, epc2]:
            data += struct.pack(">BB", 45, 1)  # RSSI, Ant
            data += struct.pack(">H", 0x3000)  # PC
            data += bytes([len(epc)])
            data += epc

        tags = parse_inventory_response(data)
        assert len(tags) == 2

    def test_parse_truncated_inventory(self):
        """Test parsing inventory with truncated data."""
        # Only partial data - should handle gracefully
        data = struct.pack(">BB", 50, 1)  # RSSI and Ant only
        data += struct.pack(">H", 0x3000)  # PC
        data += bytes([20])  # EPC length says 20 bytes but no data follows

        tags = parse_inventory_response(data)
        # Should stop parsing without crashing
        assert isinstance(tags, list)


class TestParseNetworkResponse:
    """Tests for parse_network_response function."""

    def test_parse_valid_network_response(self):
        """Test parsing valid network response."""
        # IP + Subnet + Gateway + Port
        data = bytes([192, 168, 1, 100])  # IP
        data += bytes([255, 255, 255, 0])  # Subnet
        data += bytes([192, 168, 1, 1])  # Gateway
        data += struct.pack(">H", 4001)  # Port

        config = parse_network_response(data)

        assert config["ip"] == "192.168.1.100"
        assert config["subnet"] == "255.255.255.0"
        assert config["gateway"] == "192.168.1.1"
        assert config["port"] == 4001

    def test_parse_short_network_response(self):
        """Test parsing network response that's too short."""
        config = parse_network_response(b"\x00\x00\x00")
        assert "error" in config


class TestParseGpioLevels:
    """Tests for parse_gpio_levels function."""

    def test_parse_gpio_levels(self):
        """Test parsing GPIO levels."""
        data = bytes([1, 0, 1, 0])  # GPIO1=HIGH, GPIO2=LOW, etc.
        levels = parse_gpio_levels(data)

        assert levels["gpio1"] == 1
        assert levels["gpio2"] == 0
        assert levels["gpio3"] == 1
        assert levels["gpio4"] == 0

    def test_parse_short_gpio_levels(self):
        """Test parsing GPIO levels with short data."""
        levels = parse_gpio_levels(b"\x00\x01")
        assert levels == {}


class TestParseGateStatus:
    """Tests for parse_gate_status function."""

    def test_parse_gate_status(self):
        """Test parsing gate status."""
        data = bytes([0x01, 0x02])  # Mode=detecting, Direction=exit
        status = parse_gate_status(data)

        assert status["mode"] == 0x01
        assert status["direction"] == 0x02

    def test_parse_short_gate_status(self):
        """Test parsing gate status with short data."""
        status = parse_gate_status(b"\x00")
        assert "error" in status


class TestBuildCommands:
    """Tests for command building functions."""

    def test_build_stop_inventory_command(self):
        """Test building stop inventory command."""
        cmd = build_stop_inventory_command()
        assert cmd.cmd == M200Commands.RFM_INVENTORY_STOP

    def test_build_read_tag_command(self):
        """Test building read tag command."""
        cmd = build_read_tag_command(mem_bank=2, start_addr=0, word_count=6)
        assert cmd.cmd == M200Commands.RFM_READISO_TAG
        assert len(cmd.data) == 3

    def test_build_get_all_params_command(self):
        """Test building get all params command."""
        cmd = build_get_all_params_command()
        assert cmd.cmd == M200Commands.RFM_GET_ALL_PARAM

    def test_build_module_init_command(self):
        """Test building module init command."""
        cmd = build_module_init_command()
        assert cmd.cmd == M200Commands.RFM_MODULE_INT

    def test_build_set_rf_protocol_command(self):
        """Test building set RF protocol command."""
        cmd = build_set_rf_protocol_command(protocol=0x04)
        assert cmd.cmd == M200Commands.RFM_SET_GET_RFID_PRO
        assert cmd.data[0] == 0x01  # Set mode

    def test_build_get_rf_protocol_command(self):
        """Test building get RF protocol command."""
        cmd = build_get_rf_protocol_command()
        assert cmd.cmd == M200Commands.RFM_SET_GET_RFID_PRO
        assert cmd.data[0] == 0x02  # Get mode

    def test_build_set_network_command(self):
        """Test building set network command."""
        cmd = build_set_network_command("192.168.1.100", "255.255.255.0", "192.168.1.1", 4001)
        assert cmd.cmd == M200Commands.RFM_SET_GET_NETPARA
        assert cmd.data[0] == 0x01  # Set mode

    def test_build_get_network_command(self):
        """Test building get network command."""
        cmd = build_get_network_command()
        assert cmd.cmd == M200Commands.RFM_SET_GET_NETPARA
        assert cmd.data[0] == 0x02  # Get mode

    def test_build_set_rssi_filter_command(self):
        """Test building set RSSI filter command."""
        cmd = build_set_rssi_filter_command(antenna=1, rssi_threshold=50)
        assert cmd.cmd == M200Commands.RFM_SET_GET_AntN_RSSI_Filter

    def test_build_get_rssi_filter_command(self):
        """Test building get RSSI filter command."""
        cmd = build_get_rssi_filter_command(antenna=1)
        assert cmd.cmd == M200Commands.RFM_SET_GET_AntN_RSSI_Filter

    def test_build_set_all_params_command(self):
        """Test building set all params command."""
        config = {"power": 26, "antenna": 0x0F}
        cmd = build_set_all_params_command(config)
        assert cmd.cmd == M200Commands.RFM_SET_ALL_PARAM

    def test_build_select_tag_command(self):
        """Test building select tag command."""
        cmd = build_select_tag_command(epc_mask="E20000001234")
        assert cmd.cmd == M200Commands.RFM_SETISO_SELECTMASK

    def test_build_set_query_param_command(self):
        """Test building set query param command."""
        cmd = build_set_query_param_command(q_value=4, session=0, target=0)
        assert cmd.cmd == M200Commands.RFM_SET_QUERY_PARAM

    def test_build_get_query_param_command(self):
        """Test building get query param command."""
        cmd = build_get_query_param_command()
        assert cmd.cmd == M200Commands.RFM_GET_QUERY_PARAM

    def test_build_set_select_param_command(self):
        """Test building set select param command."""
        cmd = build_set_select_param_command(select_flag=0, truncate=0)
        assert cmd.cmd == M200Commands.RFM_SET_SELPRM

    def test_build_get_select_param_command(self):
        """Test building get select param command."""
        cmd = build_get_select_param_command()
        assert cmd.cmd == M200Commands.RFM_GET_SELPRM

    def test_build_set_gpio_param_command(self):
        """Test building set GPIO param command."""
        cmd = build_set_gpio_param_command(pin=1, direction=0x01, level=0x01)
        assert cmd.cmd == M200Commands.RFM_SET_GET_G_PIO_WORKPARAM
        assert len(cmd.data) >= 3

    def test_build_get_gpio_param_command(self):
        """Test building get GPIO param command."""
        cmd = build_get_gpio_param_command(pin=1)
        assert cmd.cmd == M200Commands.RFM_SET_GET_G_PIO_WORKPARAM
        assert len(cmd.data) >= 2

    def test_build_get_gpio_levels_command(self):
        """Test building get GPIO levels command."""
        cmd = build_get_gpio_levels_command()
        assert cmd.cmd == M200Commands.RFM_GET_G_PIO_LEVEL

    def test_build_relay1_command_close(self):
        """Test building relay1 close command."""
        cmd = build_relay1_command(close=True)
        assert cmd.cmd == M200Commands.RFM_RELEASE_CLOSE_RELAY1
        assert cmd.data[0] == 0x01

    def test_build_relay1_command_open(self):
        """Test building relay1 open command."""
        cmd = build_relay1_command(close=False)
        assert cmd.data[0] == 0x00

    def test_build_relay2_command(self):
        """Test building relay2 command."""
        cmd = build_relay2_command(close=True)
        assert cmd.cmd == M200Commands.RFM_RELEASE_CLOSE_RELAY2

    def test_build_get_gate_status_command(self):
        """Test building get gate status command."""
        cmd = build_get_gate_status_command()
        assert cmd.cmd == M200Commands.RFM_GET_GATE_STATUS

    def test_build_set_gate_param_command(self):
        """Test building set gate param command."""
        cmd = build_set_gate_param_command(mode=0x01, sensitivity=0x50, direction_detect=True)
        assert cmd.cmd == M200Commands.RFM_SET_GET_GATE_PARAM
        assert len(cmd.data) >= 4

    def test_build_get_gate_param_command(self):
        """Test building get gate param command."""
        cmd = build_get_gate_param_command()
        assert cmd.cmd == M200Commands.RFM_SET_GET_GATE_PARAM
        assert cmd.data[0] == 0x02  # Get mode

    def test_build_set_eas_mask_command(self):
        """Test building set EAS mask command."""
        cmd = build_set_eas_mask_command(eas_data=b"\x01\x02\x03")
        assert cmd.data[0] == 0x01  # Set mode

    def test_build_get_eas_mask_command(self):
        """Test building get EAS mask command."""
        cmd = build_get_eas_mask_command()
        assert cmd.data[0] == 0x02  # Get mode

    def test_build_set_remote_server_command(self):
        """Test building set remote server command."""
        cmd = build_set_remote_server_command(ip="192.168.1.100", port=4001, enable=True)
        assert cmd.cmd == M200Commands.RFM_SET_GET_REMOTE_NETPARA

    def test_build_get_remote_server_command(self):
        """Test building get remote server command."""
        cmd = build_get_remote_server_command()
        assert cmd.cmd == M200Commands.RFM_SET_GET_REMOTE_NETPARA

    def test_build_set_wifi_command(self):
        """Test building set WiFi command."""
        cmd = build_set_wifi_command(ssid="MyNetwork", password="secret123", security=0x03)
        assert cmd.cmd == M200Commands.RFM_SET_GET_WiFi_PARAM
