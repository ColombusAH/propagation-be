"""
Unit tests for M200 protocol additional coverage.
"""

import pytest


@pytest.mark.unit
class TestM200CommandsDetailed:
    """Detailed tests for M200 commands."""

    def test_all_command_values(self):
        """Test all M200 command values exist."""
        from app.services.m200_protocol import M200Commands
        
        # Check known commands
        assert hasattr(M200Commands, 'RFM_INVENTORYISO_CONTINUE')
        assert hasattr(M200Commands, 'RFM_GET_DEVICE_INFO')
        assert hasattr(M200Commands, 'RFM_INVENTORY_STOP')

    def test_command_values_are_integers(self):
        """Test command values are integers."""
        from app.services.m200_protocol import M200Commands
        
        assert isinstance(M200Commands.RFM_INVENTORYISO_CONTINUE, int)
        assert isinstance(M200Commands.RFM_GET_DEVICE_INFO, int)


@pytest.mark.unit
class TestM200StatusDetailed:
    """Detailed tests for M200 status codes."""

    def test_all_status_values(self):
        """Test all M200 status values exist."""
        from app.services.m200_protocol import M200Status
        
        assert hasattr(M200Status, 'SUCCESS')
        assert M200Status.SUCCESS == 0x00

    def test_status_error_codes(self):
        """Test status error codes exist."""
        from app.services.m200_protocol import M200Status
        
        # Should have error codes defined
        members = [m for m in dir(M200Status) if not m.startswith('_')]
        assert len(members) > 0


@pytest.mark.unit
class TestM200CommandClass:
    """Tests for M200Command class."""

    def test_command_class_import(self):
        """Test M200Command can be imported."""
        from app.services.m200_protocol import M200Command
        
        assert M200Command is not None

    def test_command_class_instantiation(self):
        """Test M200Command can be instantiated."""
        from app.services.m200_protocol import M200Command, M200Commands
        
        cmd = M200Command(
            cmd=M200Commands.RFM_GET_DEVICE_INFO,
            data=b''
        )
        
        assert cmd is not None

    def test_command_has_cmd_attr(self):
        """Test M200Command has cmd attribute."""
        from app.services.m200_protocol import M200Command, M200Commands
        
        cmd = M200Command(
            cmd=M200Commands.RFM_GET_DEVICE_INFO,
            data=b''
        )
        
        assert hasattr(cmd, 'cmd')


@pytest.mark.unit
class TestCRC16:
    """Tests for CRC16 calculation."""

    def test_crc16_function_exists(self):
        """Test calculate_crc16 function exists."""
        from app.services.m200_protocol import calculate_crc16
        
        assert callable(calculate_crc16)

    def test_crc16_empty_data(self):
        """Test CRC16 on empty data."""
        from app.services.m200_protocol import calculate_crc16
        
        result = calculate_crc16(b'')
        
        assert isinstance(result, int)

    def test_crc16_simple_data(self):
        """Test CRC16 on simple data."""
        from app.services.m200_protocol import calculate_crc16
        
        result = calculate_crc16(b'\x00\x01\x02\x03')
        
        assert isinstance(result, int)
        assert result >= 0
        assert result <= 0xFFFF

    def test_crc16_consistent(self):
        """Test CRC16 is consistent for same data."""
        from app.services.m200_protocol import calculate_crc16
        
        data = b'\xAB\xCD\xEF\x01\x23'
        result1 = calculate_crc16(data)
        result2 = calculate_crc16(data)
        
        assert result1 == result2


@pytest.mark.unit
class TestM200CommandBuilders:
    """Tests for M200 command builder functions."""

    def test_build_get_device_info_command(self):
        """Test build_get_device_info_command function."""
        from app.services.m200_protocol import build_get_device_info_command
        
        cmd = build_get_device_info_command()
        
        assert cmd is not None

    def test_build_inventory_command(self):
        """Test build_inventory_command function."""
        from app.services.m200_protocol import build_inventory_command
        
        cmd = build_inventory_command()
        
        assert cmd is not None

    def test_build_stop_inventory_command(self):
        """Test build_stop_inventory_command function."""
        from app.services.m200_protocol import build_stop_inventory_command
        
        cmd = build_stop_inventory_command()
        
        assert cmd is not None


@pytest.mark.unit
class TestM200Parsers:
    """Tests for M200 response parser functions."""

    def test_parse_device_info_import(self):
        """Test parse_device_info can be imported."""
        from app.services.m200_protocol import parse_device_info
        
        assert parse_device_info is not None
        assert callable(parse_device_info)

    def test_parse_inventory_response_import(self):
        """Test parse_inventory_response can be imported."""
        from app.services.m200_protocol import parse_inventory_response
        
        assert parse_inventory_response is not None
        assert callable(parse_inventory_response)
