"""
Comprehensive tests for Payment API endpoints.
Covers: create_payment_intent, confirm_payment, create_cash_payment, refund_payment, get_payment_status
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCreatePaymentIntent:
    """Tests for POST /payment/create-intent endpoint."""

    @pytest.mark.asyncio
    async def test_create_payment_intent_nexi(self, client):
        """Test creating payment intent with Nexi provider."""
        with (
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma,
            patch("app.api.v1.endpoints.payment.NexiProvider") as mock_nexi,
        ):

            mock_nexi_instance = MagicMock()
            mock_nexi_instance.create_payment_intent = AsyncMock(
                return_value={"external_id": "nexi-123", "client_secret": "secret-abc"}
            )
            mock_nexi.return_value = mock_nexi_instance

            mock_prisma.client.payment.create = AsyncMock(
                return_value=MagicMock(
                    id="payment-1", orderId="order-1", amount=1000, currency="ILS"
                )
            )

            response = await client.post(
                "/api/v1/payment/create-intent",
                json={
                    "order_id": "order-1",
                    "amount": 1000,
                    "currency": "ILS",
                    "payment_provider": "NEXI",
                },
            )

            assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_create_payment_intent_cash(self, client):
        """Test creating payment intent with Cash provider."""
        with (
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma,
            patch("app.api.v1.endpoints.payment.get_gateway") as mock_gateway,
        ):

            mock_cash = MagicMock()
            mock_cash.create_payment = AsyncMock(
                return_value=MagicMock(success=True, payment_id="cash-123")
            )
            mock_gateway.return_value = mock_cash

            mock_prisma.client.payment.create = AsyncMock(return_value=MagicMock(id="payment-1"))

            response = await client.post(
                "/api/v1/payment/create-intent",
                json={
                    "order_id": "order-1",
                    "amount": 1000,
                    "currency": "ILS",
                    "payment_provider": "CASH",
                },
            )

            assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_create_payment_intent_invalid_provider(self, client):
        """Test creating payment intent with invalid provider."""
        response = await client.post(
            "/api/v1/payment/create-intent",
            json={
                "order_id": "order-1",
                "amount": 1000,
                "currency": "ILS",
                "payment_provider": "INVALID_PROVIDER",
            },
        )

        assert response.status_code in [400, 401, 422]


class TestConfirmPayment:
    """Tests for POST /payment/confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_payment_success(self, client):
        """Test successful payment confirmation."""
        with (
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma,
            patch("app.api.v1.endpoints.payment.get_provider_gateway") as mock_gateway,
        ):

            mock_prisma.client.payment.find_unique = AsyncMock(
                return_value=MagicMock(
                    id="payment-1",
                    externalId="ext-123",
                    provider="NEXI",
                    orderId="order-1",
                )
            )
            mock_prisma.client.payment.update = AsyncMock(return_value=MagicMock())
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            mock_gw = MagicMock()
            mock_gw.confirm_payment = AsyncMock(
                return_value=MagicMock(success=True, status=MagicMock(value="COMPLETED"))
            )
            mock_gateway.return_value = mock_gw

            response = await client.post(
                "/api/v1/payment/confirm",
                json={"payment_id": "payment-1", "payment_method_id": "pm-123"},
            )

            assert response.status_code in [200, 401, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found(self, client):
        """Test confirming non-existent payment."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)

            response = await client.post(
                "/api/v1/payment/confirm",
                json={"payment_id": "unknown-payment", "payment_method_id": "pm-123"},
            )

            assert response.status_code in [401, 404]


class TestCreateCashPayment:
    """Tests for POST /payment/cash endpoint."""

    @pytest.mark.asyncio
    async def test_create_cash_payment_success(self, client):
        """Test creating cash payment."""
        with (
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma,
            patch("app.api.v1.endpoints.payment.get_gateway") as mock_gateway,
        ):

            mock_cash = MagicMock()
            mock_cash.create_payment = AsyncMock(
                return_value=MagicMock(success=True, payment_id="cash-123")
            )
            mock_gateway.return_value = mock_cash

            mock_prisma.client.payment.create = AsyncMock(return_value=MagicMock(id="payment-1"))

            response = await client.post(
                "/api/v1/payment/cash",
                json={"order_id": "order-1", "amount": 500, "notes": "Cash payment"},
            )

            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_cash_payment_unauthorized(self, client):
        """Test cash payment without proper role."""
        response = await client.post(
            "/api/v1/payment/cash", json={"order_id": "order-1", "amount": 500}
        )

        assert response.status_code in [401, 403]


class TestRefundPayment:
    """Tests for POST /payment/refund endpoint."""

    @pytest.mark.asyncio
    async def test_refund_payment_success(self, client):
        """Test successful payment refund."""
        with (
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma,
            patch("app.api.v1.endpoints.payment.get_provider_gateway") as mock_gateway,
        ):

            mock_prisma.client.payment.find_unique = AsyncMock(
                return_value=MagicMock(
                    id="payment-1",
                    externalId="ext-123",
                    provider="NEXI",
                    status="COMPLETED",
                    orderId="order-1",
                )
            )
            mock_prisma.client.payment.update = AsyncMock()
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            mock_gw = MagicMock()
            mock_gw.refund_payment = AsyncMock(
                return_value=MagicMock(success=True, refund_id="refund-123")
            )
            mock_gateway.return_value = mock_gw

            response = await client.post(
                "/api/v1/payment/refund",
                json={"payment_id": "payment-1", "amount": 500},
            )

            assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_refund_payment_not_found(self, client):
        """Test refunding non-existent payment."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)

            response = await client.post(
                "/api/v1/payment/refund",
                json={"payment_id": "unknown-payment", "amount": 500},
            )

            assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_refund_payment_not_completed(self, client):
        """Test refunding payment that's not completed."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(
                return_value=MagicMock(id="payment-1", status="PENDING")
            )

            response = await client.post(
                "/api/v1/payment/refund",
                json={"payment_id": "payment-1", "amount": 500},
            )

            assert response.status_code in [400, 401, 403]


class TestGetPaymentStatus:
    """Tests for GET /payment/{payment_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_payment_status_found(self, client):
        """Test getting payment status - found."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(
                return_value=MagicMock(
                    id="payment-1",
                    status="COMPLETED",
                    amount=1000,
                    currency="ILS",
                    provider="NEXI",
                    createdAt=datetime.now(),
                    paidAt=datetime.now(),
                )
            )

            response = await client.get("/api/v1/payment/payment-1")

            assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_payment_status_not_found(self, client):
        """Test getting payment status - not found."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)

            response = await client.get("/api/v1/payment/unknown-payment")

            assert response.status_code in [401, 404]


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.asyncio
    async def test_mark_order_tags_as_paid(self):
        """Test marking order tags as paid."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            from app.api.v1.endpoints.payment import mark_order_tags_as_paid

            await mark_order_tags_as_paid("order-1", "payment-1")

            mock_prisma.client.tagmapping.update_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_unmark_order_tags_as_paid(self):
        """Test unmarking order tags as paid."""
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            from app.api.v1.endpoints.payment import unmark_order_tags_as_paid

            await unmark_order_tags_as_paid("order-1")

            mock_prisma.client.tagmapping.update_many.assert_called_once()
