from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from app.api.v1.endpoints.payment import router
from app.api.dependencies.auth import get_current_user as auth_get_user
from app.core.deps import get_current_user as core_get_user
from app.schemas.payment import PaymentStatusEnum, PaymentProviderEnum
from app.services.payment.base import PaymentStatus
from datetime import datetime

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "user_123"
    user.email = "test@example.com"
    user.role = "SUPER_ADMIN"
    return user

@pytest.fixture
def test_app(mock_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[auth_get_user] = lambda: mock_user
    app.dependency_overrides[core_get_user] = lambda: mock_user
    return app

@pytest.fixture
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_gateway():
    gateway = MagicMock()
    gateway.create_payment = AsyncMock()
    gateway.confirm_payment = AsyncMock()
    gateway.refund_payment = AsyncMock()
    gateway.get_payment_status = AsyncMock()
    gateway.create_payment_intent = AsyncMock()
    return gateway

@pytest.mark.asyncio
async def test_create_payment_intent_nexi_success(client, mock_gateway):
    mock_gateway.create_payment_intent.return_value = {"external_id": "nexi_1", "client_secret": "s1"}
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        payment = MagicMock(); payment.id = "p1"
        mock_p.client.payment.create = AsyncMock(return_value=payment)
        with patch("app.api.v1.endpoints.payment.get_provider_gateway", return_value=mock_gateway):
            response = await client.post("/create-intent", json={"order_id": "o1", "amount": 100, "currency": "ILS", "payment_provider": "NEXI"})
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_payment_intent_stripe_success(client, mock_gateway):
    mock_res = MagicMock(spec=PaymentStatus)
    mock_res.success = True
    mock_res.payment_id = "s_pi_1"
    mock_gateway.create_payment.return_value = mock_res
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        payment = MagicMock(); payment.id = "p2"
        mock_p.client.payment.create = AsyncMock(return_value=payment)
        with patch("app.api.v1.endpoints.payment.get_provider_gateway", return_value=mock_gateway):
            response = await client.post("/create-intent", json={"order_id": "o2", "amount": 200, "currency": "ILS", "payment_provider": "STRIPE"})
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_confirm_payment_success(client, mock_gateway):
    mock_res = MagicMock(spec=PaymentStatus)
    mock_res.success = True
    mock_res.status = PaymentStatusEnum.COMPLETED
    mock_gateway.confirm_payment.return_value = mock_res
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        mock_payment = MagicMock()
        mock_payment.provider = PaymentProviderEnum.STRIPE
        mock_payment.orderId = "o4"
        mock_payment.id = "p4"
        mock_payment.externalId = "ext_confirm_1"
        mock_p.client.payment.find_unique = AsyncMock(return_value=mock_payment)
        mock_p.client.payment.update = AsyncMock(return_value=mock_payment)
        with patch("app.api.v1.endpoints.payment.get_provider_gateway", return_value=mock_gateway):
            with patch("app.api.v1.endpoints.payment.mark_order_tags_as_paid", new_callable=AsyncMock):
                response = await client.post("/confirm", json={"payment_id": "p4"})
                assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_cash_payment_success(client):
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        payment = MagicMock(); payment.id = "c1"
        mock_p.client.payment.create = AsyncMock(return_value=payment)
        with patch("app.api.v1.endpoints.payment.get_gateway") as mock_factory:
            res = MagicMock(); res.success = True; res.payment_id = "CASH_123"
            mock_factory.return_value.create_payment = AsyncMock(return_value=res)
            with patch("app.api.v1.endpoints.payment.mark_order_tags_as_paid", new_callable=AsyncMock):
                response = await client.post("/cash", json={"order_id": "o5", "amount": 500, "received_amount": 500})
                assert response.status_code == 200

@pytest.mark.asyncio
async def test_refund_payment_success(client, mock_gateway):
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        mock_payment = MagicMock()
        mock_payment.id = "p6"
        mock_payment.provider = PaymentProviderEnum.STRIPE
        mock_payment.externalId = "ext6"
        mock_payment.status = PaymentStatusEnum.COMPLETED
        mock_p.client.payment.find_unique = AsyncMock(return_value=mock_payment)
        mock_p.client.payment.update = AsyncMock()
        
        res = MagicMock(); res.success = True; res.refund_id = "r6"; res.amount = 500; res.status = PaymentStatusEnum.REFUNDED
        mock_gateway.refund_payment.return_value = res
        with patch("app.api.v1.endpoints.payment.get_provider_gateway", return_value=mock_gateway):
            with patch("app.api.v1.endpoints.payment.unmark_order_tags_as_paid", new_callable=AsyncMock):
                response = await client.post("/refund", json={"payment_id": "p6", "amount": 500})
                assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payment_status_details(client):
    with patch("app.api.v1.endpoints.payment.prisma_client") as mock_p:
        payment = MagicMock()
        payment.id = "p7"
        payment.status = PaymentStatusEnum.COMPLETED
        payment.amount = 100
        payment.currency = "ILS"
        payment.provider = PaymentProviderEnum.STRIPE
        payment.created_at = datetime.now()
        payment.paid_at = datetime.now()
        mock_p.client.payment.find_unique = AsyncMock(return_value=payment)
        # Corrected path from /status/p7 to /p7
        response = await client.get("/p7")
        assert response.status_code == 200
