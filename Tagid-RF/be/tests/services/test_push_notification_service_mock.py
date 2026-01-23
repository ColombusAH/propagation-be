"""
Mock-based tests for PushNotificationService.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.push_notification_service import PushNotificationService
from tests.mock_utils import MockModel


class TestPushNotificationServiceMock:

    def setup_method(self):
        self.mock_db = MagicMock()
        self.service = PushNotificationService(self.mock_db)

    async def test_check_gate_scan_not_gate(self):
        """Test scanning at a non-gate reader."""
        # Reader found, but type BATH
        reader = MockModel(id="r1", type="BATH")
        self.mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        result = await self.service.check_gate_scan("E123", "r1")
        assert result["status"] == "skipped"
        assert result["reason"] == "not_gate_reader"

    async def test_check_gate_scan_paid(self):
        """Test scanning a paid item at gate."""
        reader = MockModel(id="r1", type="GATE", location="Exit")
        self.mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        tag = MockModel(id="t1", epc="E123", isPaid=True)
        self.mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        self.mock_db.rfidtag.update = AsyncMock()

        result = await self.service.check_gate_scan("E123", "r1")
        assert result["status"] == "ok"
        assert "Paid item exiting" in result["message"]

        self.mock_db.rfidtag.update.assert_awaited_once()

    async def test_check_gate_scan_unpaid(self):
        """Test scanning an unpaid item at gate (Theft!)."""
        reader = MockModel(id="r1", type="GATE", location="Exit")
        self.mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        tag = MockModel(
            id="t1", epc="E123", isPaid=False, productDescription="Stolen Item"
        )
        self.mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        self.mock_db.rfidtag.update = AsyncMock()

        # Mocks for send_theft_alert internals
        alert = MockModel(id="alert1")
        self.mock_db.theftalert.create = AsyncMock(return_value=alert)
        self.mock_db.user.find_many = AsyncMock(
            return_value=[]
        )  # No users to notify to keep simple

        result = await self.service.check_gate_scan("E123", "r1")
        assert result["status"] == "alert"
        assert result["alert"]["tag_epc"] == "E123"

        # Verify tag status update to STOLEN
        self.mock_db.rfidtag.update.assert_awaited_once()

    async def test_check_gate_scan_unknown_tag(self):
        """Test scanning an unknown tag at gate."""
        reader = MockModel(id="r1", type="GATE", location="Exit")
        self.mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        # Tag not found
        self.mock_db.rfidtag.find_unique = AsyncMock(return_value=None)

        alert = MockModel(id="alert1")
        self.mock_db.theftalert.create = AsyncMock(return_value=alert)
        self.mock_db.user.find_many = AsyncMock(return_value=[])

        result = await self.service.check_gate_scan("E123", "r1")
        assert result["status"] == "alert"
        assert result["alert"]["product"] == "Unknown Product"

    async def test_send_theft_alert_notification_flow(self):
        """Test user notification flow in theft alert."""
        # Setup users who want alerts
        user1 = MockModel(id="u1", email="u1@test.com", receiveTheftAlerts=True)
        user2 = MockModel(id="u2", email="u2@test.com", receiveTheftAlerts=True)
        self.mock_db.user.find_many = AsyncMock(return_value=[user1, user2])

        tag = MockModel(id="t1", epc="E123", productDescription="Item")
        self.mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        alert = MockModel(id="alert1")
        self.mock_db.theftalert.create = AsyncMock(return_value=alert)
        self.mock_db.alertrecipient.create = AsyncMock()

        result = await self.service.send_theft_alert("t1", "E123")

        assert result["recipients_notified"] == 2
        assert self.mock_db.alertrecipient.create.await_count == 2
