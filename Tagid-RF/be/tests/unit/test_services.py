"""
Unit tests for Service layer components.
Using actual imports from the codebase.
"""

import pytest


@pytest.mark.unit
class TestPaymentProviderImports:
    """Tests for payment provider imports."""

    def test_payment_provider_base_import(self):
        """Test PaymentProvider can be imported."""
        from app.services.payment_provider import PaymentProvider
        
        assert PaymentProvider is not None

    def test_stripe_provider_import(self):
        """Test StripeProvider can be imported."""
        from app.services.stripe_provider import StripeProvider
        
        assert StripeProvider is not None

    def test_cash_provider_import(self):
        """Test CashProvider can be imported."""
        from app.services.cash_provider import CashProvider
        
        assert CashProvider is not None

    def test_tranzila_provider_import(self):
        """Test TranzilaProvider can be imported."""
        from app.services.tranzila_provider import TranzilaProvider
        
        assert TranzilaProvider is not None


@pytest.mark.unit
class TestDatabaseService:
    """Tests for database service."""

    def test_base_import(self):
        """Test SQLAlchemy Base can be imported."""
        from app.services.database import Base
        
        assert Base is not None

    def test_get_db_import(self):
        """Test get_db function exists."""
        from app.services.database import get_db
        
        assert callable(get_db)

    def test_init_db_import(self):
        """Test init_db function exists."""
        from app.services.database import init_db
        
        assert callable(init_db)


@pytest.mark.unit
class TestTagEncryption:
    """Tests for tag encryption service."""

    def test_encryption_service_import(self):
        """Test tag encryption service can be imported."""
        from app.services import tag_encryption
        
        assert tag_encryption is not None


@pytest.mark.unit
class TestTheftDetection:
    """Tests for theft detection service."""

    def test_theft_detection_import(self):
        """Test theft detection service can be imported."""
        from app.services import theft_detection
        
        assert theft_detection is not None


@pytest.mark.unit
class TestPushNotifications:
    """Tests for push notification service."""

    def test_push_service_import(self):
        """Test push notification service can be imported."""
        from app.services import push_notifications
        
        assert push_notifications is not None


@pytest.mark.unit
class TestM200Protocol:
    """Tests for M200 protocol service."""

    def test_m200_commands_import(self):
        """Test M200 commands constants can be imported."""
        from app.services.m200_protocol import M200Commands
        
        assert M200Commands is not None

    def test_m200_status_import(self):
        """Test M200 status codes can be imported."""
        from app.services.m200_protocol import M200Status
        
        assert M200Status is not None

    def test_m200_command_class(self):
        """Test M200Command class can be imported."""
        from app.services.m200_protocol import M200Command
        
        assert M200Command is not None

    def test_crc16_function(self):
        """Test CRC16 calculation function exists."""
        from app.services.m200_protocol import calculate_crc16
        
        assert callable(calculate_crc16)


@pytest.mark.unit
class TestRFIDReader:
    """Tests for RFID reader service."""

    def test_rfid_reader_service_import(self):
        """Test RFID reader service can be imported."""
        from app.services.rfid_reader import rfid_reader_service
        
        assert rfid_reader_service is not None

    def test_rfid_reader_has_connect(self):
        """Test RFID reader has connect method."""
        from app.services.rfid_reader import rfid_reader_service
        
        assert hasattr(rfid_reader_service, 'connect')

    def test_rfid_reader_has_disconnect(self):
        """Test RFID reader has disconnect method."""
        from app.services.rfid_reader import rfid_reader_service
        
        assert hasattr(rfid_reader_service, 'disconnect')

    def test_rfid_reader_has_start_scan(self):
        """Test RFID reader has start_scanning method."""
        from app.services.rfid_reader import rfid_reader_service
        
        assert hasattr(rfid_reader_service, 'start_scanning')

    def test_rfid_reader_has_stop_scan(self):
        """Test RFID reader has stop_scanning method."""
        from app.services.rfid_reader import rfid_reader_service
        
        assert hasattr(rfid_reader_service, 'stop_scanning')


@pytest.mark.unit
class TestServiceConstants:
    """Tests for service constants and configurations."""

    def test_notification_types_defined(self):
        """Test notification types are defined."""
        from app.routers.notifications import NOTIFICATION_TYPES
        
        assert len(NOTIFICATION_TYPES) >= 7
        assert "UNPAID_EXIT" in NOTIFICATION_TYPES
        assert "SALE" in NOTIFICATION_TYPES

    def test_m200_command_values(self):
        """Test M200 command values are defined."""
        from app.services.m200_protocol import M200Commands
        
        assert hasattr(M200Commands, 'RFM_INVENTORYISO_CONTINUE')
        assert hasattr(M200Commands, 'RFM_GET_DEVICE_INFO')
        assert hasattr(M200Commands, 'RFM_INVENTORY_STOP')

    def test_m200_status_values(self):
        """Test M200 status values are defined."""
        from app.services.m200_protocol import M200Status
        
        assert hasattr(M200Status, 'SUCCESS')
        assert M200Status.SUCCESS == 0x00
