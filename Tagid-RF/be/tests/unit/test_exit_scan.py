"""
Unit tests for Exit Scan API and RFID payment status.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestRFIDTagPaymentFields:
    """Tests for RFID tag payment-related fields."""

    def test_rfid_tag_payment_fields(self):
        """Test RFIDTag model has payment fields."""
        from app.models.rfid_tag import RFIDTag
        
        tag = RFIDTag(
            epc="E200-TEST-001",
            is_paid=False,
            product_name="Test Product",
            product_sku="SKU-001",
            price_cents=1999,
            store_id=1
        )
        
        assert tag.epc == "E200-TEST-001"
        assert tag.is_paid is False
        assert tag.product_name == "Test Product"
        assert tag.product_sku == "SKU-001"
        assert tag.price_cents == 1999
        assert tag.store_id == 1

    def test_rfid_tag_default_payment_status(self):
        """Test RFIDTag is_paid column has default=False."""
        from app.models.rfid_tag import RFIDTag
        
        # Check the column definition has default=False
        is_paid_col = RFIDTag.__table__.c.is_paid
        assert is_paid_col.default.arg is False

    def test_rfid_tag_paid_at_field(self):
        """Test RFIDTag paid_at timestamp field."""
        from datetime import datetime, timezone
        from app.models.rfid_tag import RFIDTag
        
        now = datetime.now(timezone.utc)
        tag = RFIDTag(
            epc="E200-TEST-003",
            is_paid=True,
            paid_at=now
        )
        
        assert tag.is_paid is True
        assert tag.paid_at == now


@pytest.mark.unit
class TestExitScanSchemas:
    """Tests for Exit Scan Pydantic schemas."""

    def test_exit_scan_request(self):
        """Test ExitScanRequest schema."""
        from app.routers.exit_scan import ExitScanRequest
        
        data = ExitScanRequest(
            epcs=["E200-001", "E200-002", "E200-003"],
            gate_id="exit-1",
            store_id=1
        )
        
        assert len(data.epcs) == 3
        assert data.gate_id == "exit-1"
        assert data.store_id == 1

    def test_exit_scan_request_defaults(self):
        """Test ExitScanRequest default values."""
        from app.routers.exit_scan import ExitScanRequest
        
        data = ExitScanRequest(epcs=["E200-001"])
        
        assert data.gate_id == "main-exit"
        assert data.store_id is None

    def test_unpaid_item_alert(self):
        """Test UnpaidItemAlert schema."""
        from app.routers.exit_scan import UnpaidItemAlert
        
        alert = UnpaidItemAlert(
            epc="E200-TEST-001",
            product_name="Blue Shirt XL",
            product_sku="SHIRT-BLU-XL",
            price_cents=18900,
            price_display="₪189.00"
        )
        
        assert alert.epc == "E200-TEST-001"
        assert alert.product_name == "Blue Shirt XL"
        assert alert.price_cents == 18900
        assert alert.price_display == "₪189.00"

    def test_exit_scan_response(self):
        """Test ExitScanResponse schema."""
        from app.routers.exit_scan import ExitScanResponse, UnpaidItemAlert
        
        unpaid_item = UnpaidItemAlert(
            epc="E200-001",
            product_name="Test",
            product_sku=None,
            price_cents=1000,
            price_display="₪10.00"
        )
        
        response = ExitScanResponse(
            total_scanned=5,
            paid_count=4,
            unpaid_count=1,
            unpaid_items=[unpaid_item],
            alert_sent=True,
            alert_recipients=3
        )
        
        assert response.total_scanned == 5
        assert response.paid_count == 4
        assert response.unpaid_count == 1
        assert len(response.unpaid_items) == 1
        assert response.alert_sent is True
        assert response.alert_recipients == 3


@pytest.mark.unit
class TestPriceFormatting:
    """Tests for price formatting in exit scan."""

    def test_price_formatting_agorot_to_shekel(self):
        """Test price conversion from agorot to shekel."""
        price_cents = 18900
        price_display = f"₪{price_cents / 100:.2f}"
        
        assert price_display == "₪189.00"

    def test_price_formatting_small_amounts(self):
        """Test price formatting for small amounts."""
        price_cents = 50
        price_display = f"₪{price_cents / 100:.2f}"
        
        assert price_display == "₪0.50"

    def test_price_formatting_round_amounts(self):
        """Test price formatting for round amounts."""
        price_cents = 10000
        price_display = f"₪{price_cents / 100:.2f}"
        
        assert price_display == "₪100.00"


@pytest.mark.unit
class TestUnpaidItemDetection:
    """Tests for unpaid item detection logic."""

    def test_identify_unpaid_from_list(self):
        """Test identifying unpaid items from a list of tags."""
        # Simulate tag data
        tags = [
            {"epc": "E200-001", "is_paid": True},
            {"epc": "E200-002", "is_paid": False},
            {"epc": "E200-003", "is_paid": True},
            {"epc": "E200-004", "is_paid": False},
        ]
        
        unpaid = [t for t in tags if not t["is_paid"]]
        paid = [t for t in tags if t["is_paid"]]
        
        assert len(unpaid) == 2
        assert len(paid) == 2
        assert unpaid[0]["epc"] == "E200-002"
        assert unpaid[1]["epc"] == "E200-004"

    def test_all_items_paid(self):
        """Test scenario where all items are paid."""
        tags = [
            {"epc": "E200-001", "is_paid": True},
            {"epc": "E200-002", "is_paid": True},
        ]
        
        unpaid = [t for t in tags if not t["is_paid"]]
        
        assert len(unpaid) == 0

    def test_all_items_unpaid(self):
        """Test scenario where all items are unpaid."""
        tags = [
            {"epc": "E200-001", "is_paid": False},
            {"epc": "E200-002", "is_paid": False},
        ]
        
        unpaid = [t for t in tags if not t["is_paid"]]
        
        assert len(unpaid) == 2
