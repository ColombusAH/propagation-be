"""
Extended tests for M200 Protocol - Command builders and parsers.
Simple import and structure tests.
"""
import pytest


class TestM200ProtocolImports:
    """Tests for M200 protocol imports."""
    
    def test_import_m200_protocol(self):
        """Test m200_protocol module imports."""
        from app.services import m200_protocol
        assert m200_protocol is not None
    
    def test_import_m200_command(self):
        """Test M200Command imports."""
        from app.services.m200_protocol import M200Command
        assert M200Command is not None
    
    def test_import_m200_commands(self):
        """Test M200Commands enum imports."""
        from app.services.m200_protocol import M200Commands
        assert M200Commands is not None
    
    def test_import_m200_status(self):
        """Test M200Status enum imports."""
        from app.services.m200_protocol import M200Status
        assert M200Status is not None
    
    def test_import_head_constant(self):
        """Test HEAD constant imports."""
        from app.services.m200_protocol import HEAD
        assert HEAD is not None
    
    def test_import_parse_functions(self):
        """Test parser functions import."""
        from app.services.m200_protocol import parse_inventory_response, parse_device_info
        assert parse_inventory_response is not None
        assert parse_device_info is not None


class TestM200CommandClass:
    """Tests for M200Command class."""
    
    def test_m200_command_init(self):
        """Test M200Command initialization."""
        from app.services.m200_protocol import M200Command
        
        cmd = M200Command(cmd=0x0003, data=b"")
        assert cmd is not None
    
    def test_m200_command_serialize(self):
        """Test M200Command serialization."""
        from app.services.m200_protocol import M200Command
        
        cmd = M200Command(cmd=0x0003, data=b"")
        data = cmd.serialize()
        
        assert isinstance(data, bytes)
        assert len(data) > 0


class TestM200Enums:
    """Tests for M200 enums."""
    
    def test_m200_status_success(self):
        """Test M200Status success value."""
        from app.services.m200_protocol import M200Status
        assert M200Status.SUCCESS == 0x00
    
    def test_m200_commands_has_values(self):
        """Test M200Commands has expected values."""
        from app.services.m200_protocol import M200Commands
        assert hasattr(M200Commands, 'RFM_READISO_TAG')


class TestM200Parsers:
    """Tests for M200 parsers."""
    
    def test_parse_inventory_empty(self):
        """Test parsing empty inventory."""
        from app.services.m200_protocol import parse_inventory_response
        
        result = parse_inventory_response(b"")
        assert result == []
    
    def test_parse_device_info_empty(self):
        """Test parsing empty device info."""
        from app.services.m200_protocol import parse_device_info
        
        result = parse_device_info(b"")
        # Should return default dict with empty strings/unknown
        assert isinstance(result, dict)
        assert "cp_hardware_version" in result or "cp_firmware_version" in result
