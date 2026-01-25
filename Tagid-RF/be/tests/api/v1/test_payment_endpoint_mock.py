"""
Coverage tests for Payment API endpoints.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.core import deps
from app.schemas.payment import PaymentProviderEnum, PaymentStatusEnum
from app.services.payment.base import PaymentResult, PaymentStatus
from types import SimpleNamespace

from app.core.deps import get_current_user as get_current_user_core
from app.api.dependencies.auth import get_current_user as get_current_user_api

# Create a mock user
def create_mock_user(role="SUPER_ADMIN"):
    return SimpleNamespace(
        id="user-1",
        email="test@example.com",
        name="Test User",
        phone="000-000-0000",
        address="Test Address",
        role=role,
        businessId="biz-1",
        is_active=True,
        darkMode=False,
        createdAt=datetime.now(),
        updatedAt=datetime.now()
    )

@pytest.fixture
def auth_override():
    """Fixture to override auth dependencies."""
    mock_user = create_mock_user()
    app.dependency_overrides[get_current_user_core] = lambda: mock_user
    app.dependency_overrides[get_current_user_api] = lambda: mock_user
    yield
    app.dependency_overrides.clear()

class TestPaymentEndpointCoverage:

    @pytest.mark.asyncio
    async def test_create_intent_nexi(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.NexiProvider") as MockNexi,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_gateway = AsyncMock()
            MockNexi.return_value = mock_gateway
            mock_gateway.create_payment_intent.return_value = {
                "external_id": "nexi-123",
                "client_secret": "secret-123"
            }
            mock_prisma.client.payment.create = AsyncMock(return_value=SimpleNamespace(
                id="p1", businessId="b1", provider="NEXI", externalId="nexi-123",
                amount=1000, currency="ILS", createdAt=datetime.now(), paidAt=None,
                status="PENDING", orderId="o1", metadata={}
            ))

            payload = {
                "order_id": "order-1",
                "amount": 1000,
                "currency": "ILS",
                "payment_provider": "NEXI"
            }
            response = await client.post("/api/v1/payment/create-intent", json=payload)
            assert response.status_code == 200
            assert response.json()["payment_id"] == "p1"

    @pytest.mark.asyncio
    async def test_create_intent_factory(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.get_gateway") as mock_get_gateway,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_gateway = AsyncMock()
            mock_get_gateway.return_value = mock_gateway
            mock_gateway.create_payment.return_value = PaymentResult(
                success=True, payment_id="ext-456"
            )
            mock_prisma.client.payment.create = AsyncMock(return_value=SimpleNamespace(
                id="p2", provider="STRIPE", externalId="ext-456", amount=500,
                businessId="b1", currency="ILS", createdAt=datetime.now(), status="PENDING",
                orderId="o2", metadata={}
            ))

            payload = {
                "order_id": "order-2",
                "amount": 500,
                "currency": "ILS",
                "payment_provider": "STRIPE"
            }
            response = await client.post("/api/v1/payment/create-intent", json=payload)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_intent_factory_fail(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.get_gateway") as mock_get_gateway:
            mock_gateway = AsyncMock()
            mock_get_gateway.return_value = mock_gateway
            mock_gateway.create_payment.return_value = PaymentResult(
                success=False, error="Provider error", payment_id=""
            )

            payload = {
                "order_id": "order-3",
                "amount": 500,
                "currency": "ILS",
                "payment_provider": "STRIPE"
            }
            response = await client.post("/api/v1/payment/create-intent", json=payload)
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_confirm_payment_nexi(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.NexiProvider") as MockNexi,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=SimpleNamespace(
                id="p1", provider="NEXI", externalId="nexi-123", orderId="o1"
            ))
            mock_gateway = AsyncMock()
            MockNexi.return_value = mock_gateway
            mock_gateway.confirm_payment.return_value = {
                "status": PaymentStatusEnum.COMPLETED,
                "metadata": {"confirmed": True}
            }
            mock_prisma.client.payment.update = AsyncMock()
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            response = await client.post("/api/v1/payment/confirm", json={"payment_id": "p1"})
            assert response.status_code == 200
            assert response.json()["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_confirm_payment_factory_success(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.get_gateway") as mock_get_gateway,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=SimpleNamespace(
                id="p2", provider="STRIPE", externalId="stripe-123", orderId="o2"
            ))
            mock_gateway = AsyncMock()
            mock_get_gateway.return_value = mock_gateway
            mock_gateway.confirm_payment.return_value = PaymentResult(
                success=True, status=PaymentStatus.COMPLETED, payment_id="stripe-123"
            )
            mock_prisma.client.payment.update = AsyncMock()
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            response = await client.post("/api/v1/payment/confirm", json={"payment_id": "p2"})
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_cash_payment(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.get_gateway") as mock_get_gateway,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_gateway = AsyncMock()
            mock_get_gateway.return_value = mock_gateway
            mock_gateway.create_payment.return_value = PaymentResult(
                success=True, payment_id="cash-123"
            )
            mock_prisma.client.payment.create = AsyncMock(return_value=SimpleNamespace(
                id="p3", amount=100, provider="CASH", externalId="cash-123", currency="ILS",
                businessId="b1", createdAt=datetime.now(), status="PENDING", orderId="o3",
                metadata={"notes": "test"}
            ))

            payload = {"order_id": "o3", "amount": 100, "notes": "paid in cash"}
            response = await client.post("/api/v1/payment/cash", json=payload)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_refund_payment_nexi(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.payment.NexiProvider") as MockNexi,
            patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma
        ):
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=SimpleNamespace(
                id="p1", provider="NEXI", status="COMPLETED", externalId="nexi-123", orderId="o1"
            ))
            mock_gateway = AsyncMock()
            MockNexi.return_value = mock_gateway
            mock_gateway.refund_payment.return_value = {
                "refund_id": "ref-1",
                "amount": 500
            }
            mock_prisma.client.payment.update = AsyncMock()
            mock_prisma.client.tagmapping.update_many = AsyncMock()

            response = await client.post("/api/v1/payment/refund", json={"payment_id": "p1", "amount": 500})
            assert response.status_code == 200
            assert response.json()["status"] == "REFUNDED"

    @pytest.mark.asyncio
    async def test_create_intent_invalid_provider(self, client, auth_override):
        payload = {
            "order_id": "o-err",
            "amount": 1000,
            "currency": "ILS",
            "payment_provider": "INVALID" # Pydantic will catch this first if Enum, but if we bypass...
        }
        # Actually Pydantic will return 422. 
        # To hit lines 62-63, we need to mock get_provider_gateway to raise ValueError
        with patch("app.api.v1.endpoints.payment.get_provider_gateway") as mock_get:
            mock_get.side_effect = ValueError("Invalid")
            payload["payment_provider"] = "STRIPE"
            response = await client.post("/api/v1/payment/create-intent", json=payload)
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)
            response = await client.post("/api/v1/payment/confirm", json={"payment_id": "missing"})
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_confirm_payment_error(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(side_effect=Exception("DB Error"))
            response = await client.post("/api/v1/payment/confirm", json={"payment_id": "p1"})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_refund_payment_not_found(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)
            response = await client.post("/api/v1/payment/refund", json={"payment_id": "missing"})
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_refund_payment_not_completed(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=SimpleNamespace(
                id="p1", status="PENDING"
            ))
            response = await client.post("/api/v1/payment/refund", json={"payment_id": "p1"})
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_payment_status_success(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=SimpleNamespace(
                id="p1", status="COMPLETED", amount=100, currency="ILS", provider="CASH",
                createdAt=datetime.now(), paidAt=datetime.now()
            ))

            response = await client.get("/api/v1/payment/p1")
            assert response.status_code == 200
            assert response.json()["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_get_payment_status_not_found(self, client, auth_override):
        with patch("app.api.v1.endpoints.payment.prisma_client") as mock_prisma:
            mock_prisma.client.payment.find_unique = AsyncMock(return_value=None)
            response = await client.get("/api/v1/payment/missing")
            assert response.status_code == 404
