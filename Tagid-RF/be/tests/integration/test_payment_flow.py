import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from types import SimpleNamespace
from app.core.security import create_access_token
from app.schemas.payment import PaymentStatusEnum, PaymentProviderEnum

# Helper
def create_auth_headers(role: str = "CUSTOMER", user_id: str = "cust-1"):
    token = create_access_token(
        data={"sub": f"{role.lower()}@example.com", "user_id": user_id, "role": role, "business_id": "bus-1"}
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_payment_happy_path(async_client: AsyncClient):
    """
    Test a complete successful payment flow:
    1. Create Payment Intent
    2. Confirm Payment
    3. Verify Status
    """

    # Mock user for auth
    async def mock_get_user_by_id(db, user_id):
        return SimpleNamespace(
            id=user_id,
            email="cust@example.com",
            role="CUSTOMER",
            businessId="bus-1",
            is_active=True
        )

    # Mock Payment Gateway
    mock_gateway = MagicMock()
    mock_gateway.create_payment = AsyncMock(return_value=SimpleNamespace(
        success=True,
        payment_id="ext-pay-123",
        status="pending",
        error=None
    ))
    mock_gateway.confirm_payment = AsyncMock(return_value=SimpleNamespace(
        success=True,
        status="completed",
        error=None
    ))
    
    # Mock DB Payment creation
    # The endpoint creates a payment in DB. We need to mock prisma.payment.create, find_unique, update.
    # We can use the global prisma mock from conftest, but we need to ensure it returns objects we can use.
    
    # We will let the conftest mock handle the DB calls, but we need to ensure `create` returns an object with an ID.
    # The default mock in conftest returns a MagicMock/AsyncMock.
    
    with patch("app.api.dependencies.auth.get_user_by_id", side_effect=mock_get_user_by_id), \
         patch("app.api.v1.endpoints.payment.get_gateway", return_value=mock_gateway):

        # 1. Create Intent
        headers = create_auth_headers("CUSTOMER")
        payload = {
            "order_id": "order-1",
            "amount": 1000, # 10.00 ILS
            "currency": "ILS",
            "payment_provider": "STRIPE",
            "metadata": {"test": "true"}
        }
        
        # We need to mock prisma.payment.create to return a simpler object
        with patch("app.api.v1.endpoints.payment.prisma_client.client.payment.create", new_callable=AsyncMock) as mock_db_create:
            mock_db_create.return_value = SimpleNamespace(
                id="pay-db-1",
                orderId="order-1",
                amount=1000,
                currency="ILS",
                provider="STRIPE",
                externalId="ext-pay-123",
                status="PENDING",
                metadata={"test": "true"},
                createdAt="2023-01-01",
                paidAt=None
            )

            response = await async_client.post("/api/v1/payment/create-intent", json=payload, headers=headers)
            assert response.status_code == 200, f"Create intent failed: {response.text}"
            data = response.json()
            assert data["payment_id"] == "pay-db-1"
            assert data["external_id"] == "ext-pay-123"
            assert data["status"] == "PENDING"

        # 2. Confirm Payment
        confirm_payload = {
            "payment_id": "pay-db-1",
            "payment_method_id": "pm_card_test"
        }

        # Mock find_unique and update for confirmation
        with patch("app.api.v1.endpoints.payment.prisma_client.client.payment.find_unique", new_callable=AsyncMock) as mock_find, \
             patch("app.api.v1.endpoints.payment.prisma_client.client.payment.update", new_callable=AsyncMock) as mock_update, \
             patch("app.api.v1.endpoints.payment.mark_order_tags_as_paid", new_callable=AsyncMock) as mock_mark_tags:
            
            mock_find.return_value = SimpleNamespace(
                id="pay-db-1",
                externalId="ext-pay-123",
                orderId="order-1",
                provider="STRIPE",
                status="PENDING",
                amount=1000,
                currency="ILS"
            )
            
            mock_update.return_value = None # We don't verify return of update deeply here

            response = await async_client.post("/api/v1/payment/confirm", json=confirm_payload, headers=headers)
            assert response.status_code == 200, f"Confirm failed: {response.text}"
            data = response.json()
            assert data["status"] == "COMPLETED"
            
            # Verify mock calls
            mock_gateway.confirm_payment.assert_called_once()
            mock_mark_tags.assert_called_once_with("order-1", "pay-db-1")


@pytest.mark.asyncio
async def test_refund_flow(async_client: AsyncClient):
    """Test refund flow logic (permissions and status check)."""
    
    # Mock Manager Auth
    async def mock_get_user_by_id(db, user_id):
        return SimpleNamespace(
            id=user_id,
            email="mgr@example.com",
            role="STORE_MANAGER",
            businessId="bus-1",
            is_active=True
        )

    mock_gateway = MagicMock()
    mock_gateway.refund_payment = AsyncMock(return_value=SimpleNamespace(
        success=True,
        refund_id="ref-123",
        status="refunded",
        error=None
    ))

    with patch("app.api.dependencies.auth.get_user_by_id", side_effect=mock_get_user_by_id), \
         patch("app.api.v1.endpoints.payment.get_gateway", return_value=mock_gateway):
        
        headers = create_auth_headers("STORE_MANAGER", user_id="mgr-1")
        refund_payload = {
            "payment_id": "pay-db-1",
            "amount": 1000
        }

        with patch("app.api.v1.endpoints.payment.prisma_client.client.payment.find_unique", new_callable=AsyncMock) as mock_find, \
             patch("app.api.v1.endpoints.payment.prisma_client.client.payment.update", new_callable=AsyncMock) as mock_update, \
             patch("app.api.v1.endpoints.payment.unmark_order_tags_as_paid", new_callable=AsyncMock) as mock_unmark:
             
            # Test 1: Try to refund PENDING payment (Should Fail)
            mock_find.return_value = SimpleNamespace(id="pay-db-1", status="PENDING", provider="STRIPE")
            response = await async_client.post("/api/v1/payment/refund", json=refund_payload, headers=headers)
            assert response.status_code == 400
            assert "Cannot refund" in response.json()["detail"]

            # Test 2: Refund COMPLETED payment (Success)
            mock_find.return_value = SimpleNamespace(
                id="pay-db-1", 
                status="COMPLETED", 
                provider="STRIPE", 
                externalId="ext-pay-123",
                orderId="order-1"
            )
            
            response = await async_client.post("/api/v1/payment/refund", json=refund_payload, headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "REFUNDED"
            assert data["refund_id"] == "ref-123"
            
            mock_unmark.assert_called_once_with("order-1")
