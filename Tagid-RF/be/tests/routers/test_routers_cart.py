"""
Tests for Cart Router - shopping cart and checkout.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.rfid_tag import RFIDTag
from app.routers.cart import FAKE_CART_DB, router
from app.services.database import get_db
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    return db, mock_query


@pytest.fixture
async def client(test_app, mock_db):
    test_app.dependency_overrides[get_db] = lambda: mock_db[0]
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac
    test_app.dependency_overrides.clear()
    FAKE_CART_DB.clear()


def _create_mock_tag(
    epc="E200TEST", product_name="Test Product", product_sku="SKU123", price_cents=1999
):
    tag = MagicMock(spec=RFIDTag)
    tag.epc = epc
    tag.product_name = product_name
    tag.product_sku = product_sku
    tag.price_cents = price_cents
    tag.is_paid = False
    tag.is_active = True
    return tag


@pytest.mark.asyncio
async def test_view_empty_cart(client: AsyncClient):
    """Test viewing an empty cart."""
    # Clear the cart at start
    FAKE_CART_DB.clear()

    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 0
    assert data["total_price_cents"] == 0


@pytest.mark.asyncio
async def test_add_to_cart_via_sku(client: AsyncClient, mock_db):
    """Test adding item to cart via tagid:// deep link."""
    db, mock_query = mock_db
    tag = _create_mock_tag()
    mock_query.first.return_value = tag

    response = await client.post("/add", json={"qr_data": "tagid://product/SKU123"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["epc"] == "E200TEST"


@pytest.mark.asyncio
async def test_add_to_cart_via_epc(client: AsyncClient, mock_db):
    """Test adding item to cart via direct EPC."""
    db, mock_query = mock_db
    tag = _create_mock_tag(epc="E200DIRECT")
    mock_query.first.return_value = tag

    response = await client.post("/add", json={"qr_data": "E200DIRECT"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1


@pytest.mark.asyncio
async def test_add_to_cart_not_found(client: AsyncClient, mock_db):
    """Test adding non-existent product to cart."""
    db, mock_query = mock_db
    mock_query.first.return_value = None

    response = await client.post("/add", json={"qr_data": "tagid://product/NOTFOUND"})

    assert response.status_code == 404
    assert "not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_to_cart_duplicate(client: AsyncClient, mock_db):
    """Test adding duplicate item to cart."""
    db, mock_query = mock_db
    tag = _create_mock_tag(epc="E200DUP")
    mock_query.first.return_value = tag

    # Add first time
    await client.post("/add", json={"qr_data": "E200DUP"})

    # Add second time - should fail
    response = await client.post("/add", json={"qr_data": "E200DUP"})

    assert response.status_code == 400
    assert "already in cart" in response.json()["detail"]


@pytest.mark.asyncio
async def test_checkout_empty_cart(client: AsyncClient, mock_db):
    """Test checkout with empty cart."""
    response = await client.post("/checkout", json={"payment_method_id": "pm_test"})

    assert response.status_code == 400
    assert "Cart is empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_checkout_success(client: AsyncClient, mock_db):
    """Test successful checkout flow."""
    db, mock_query = mock_db
    tag = _create_mock_tag(price_cents=5000)
    mock_query.first.return_value = tag

    # Add item to cart first
    await client.post("/add", json={"qr_data": "tagid://product/SKU123"})

    # Mock Payment Gateway
    with patch("app.routers.cart.get_gateway") as mock_get_gateway:
        mock_gateway = MagicMock()
        mock_get_gateway.return_value = mock_gateway

        # Mock create_payment response
        mock_create_res = MagicMock()
        mock_create_res.success = True
        mock_create_res.payment_id = "pi_test123"
        mock_create_res.external_id = "pi_test123"
        mock_create_res.status = "pending"
        mock_gateway.create_payment = AsyncMock(return_value=mock_create_res)

        # Mock confirm_payment response
        mock_confirm_res = MagicMock()
        mock_confirm_res.success = True
        mock_confirm_res.status = "completed"
        mock_confirm_res.external_id = "pi_test123"
        mock_gateway.confirm_payment = AsyncMock(return_value=mock_confirm_res)

        response = await client.post("/checkout", json={"payment_method_id": "pm_test"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["transaction_id"] == "pi_test123"


@pytest.mark.asyncio
async def test_checkout_payment_failed(client: AsyncClient, mock_db):
    """Test checkout with failed payment."""
    db, mock_query = mock_db
    tag = _create_mock_tag(price_cents=5000)
    mock_query.first.return_value = tag

    # Add item to cart
    await client.post("/add", json={"qr_data": "tagid://product/SKU123"})

    # Mock settings to force Stripe
    with patch("app.routers.cart.settings") as mock_settings:
        mock_settings.DEFAULT_PAYMENT_PROVIDER = "stripe"

        with patch("app.routers.cart.get_gateway") as mock_get_gateway:
            mock_gateway = MagicMock()
            mock_get_gateway.return_value = mock_gateway

            # Mock create_payment success (pending confirmation)
            mock_create_res = MagicMock()
            mock_create_res.success = True
            mock_create_res.payment_id = "pi_test123"
            mock_create_res.status = "pending"
            mock_gateway.create_payment = AsyncMock(return_value=mock_create_res)

            mock_confirm_res = MagicMock()
            mock_confirm_res.success = False
            mock_confirm_res.status = "failed"
            mock_confirm_res.error = "Card declined"
            mock_gateway.confirm_payment = AsyncMock(return_value=mock_confirm_res)

            response = await client.post(
                "/checkout", json={"payment_method_id": "pm_test"}
            )

    assert response.status_code == 400
    assert "Payment failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_checkout_stripe_exception(client: AsyncClient, mock_db):
    """Test checkout with Stripe exception."""
    db, mock_query = mock_db
    tag = _create_mock_tag(price_cents=5000)
    mock_query.first.return_value = tag

    # Add item to cart
    await client.post("/add", json={"qr_data": "tagid://product/SKU123"})

    with patch("app.routers.cart.get_gateway") as mock_get_gateway:
        mock_gateway = MagicMock()
        mock_get_gateway.return_value = mock_gateway
        mock_gateway.create_payment = AsyncMock(side_effect=Exception("Stripe error"))

        response = await client.post("/checkout", json={"payment_method_id": "pm_test"})

    assert response.status_code == 500
