"""
Tests for TranzilaGateway payment integration.
Covers all methods of the Tranzila payment gateway.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTranzilaGateway:
    """Tests for TranzilaGateway."""

    @pytest.fixture
    def gateway(self):
        """Create TranzilaGateway instance."""
        from app.services.payment.tranzila import TranzilaGateway

        return TranzilaGateway(
            terminal_name="test_terminal", terminal_password="test_pass"
        )

    def test_provider_property(self, gateway):
        """Test provider property returns TRANZILA."""
        from app.services.payment.base import PaymentProvider

        assert gateway.provider == PaymentProvider.TRANZILA

    @pytest.mark.asyncio
    async def test_create_payment(self, gateway):
        """Test creating a Tranzila payment."""
        from app.services.payment.base import PaymentRequest

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Response=000"
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            request = PaymentRequest(order_id="order-123", amount=1000, currency="ILS")

            result = await gateway.create_payment(request)

            assert result is not None

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway):
        """Test confirming a Tranzila payment."""
        result = await gateway.confirm_payment("txn_12345")

        # Tranzila typically auto-confirms
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_payment_status(self, gateway):
        """Test getting Tranzila payment status."""
        result = await gateway.get_payment_status("txn_12345")

        assert result is not None

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway):
        """Test refunding a Tranzila payment."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Response=000"
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await gateway.refund_payment("txn_12345", 500)

            assert result is not None

    def test_currency_codes(self, gateway):
        """Test currency code mapping."""
        from app.services.payment.tranzila import TranzilaGateway

        assert TranzilaGateway.CURRENCY_CODES["ILS"] == "1"
        assert TranzilaGateway.CURRENCY_CODES["USD"] == "2"
        assert TranzilaGateway.CURRENCY_CODES["EUR"] == "3"

    def test_init_with_credentials(self):
        """Test initialization with credentials."""
        from app.services.payment.tranzila import TranzilaGateway

        gw = TranzilaGateway(terminal_name="my_terminal", terminal_password="my_pass")

        # The class stores terminal_name as 'terminal' attribute
        assert gw.terminal == "my_terminal"
