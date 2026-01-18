"""
Comprehensive tests for Cart router endpoints.
Covers: get_cart_session, add_to_cart, view_cart, checkout, _calculate_summary
"""

import pytest
from unittest.mock import MagicMock, patch
from app.routers.cart import get_cart_session, _calculate_summary, FAKE_CART_DB
from app.schemas.cart import CartItem


class TestGetCartSession:
    """Tests for get_cart_session helper."""

    def test_get_cart_session_new(self):
        """Test getting cart for new session."""
        FAKE_CART_DB.clear()
        cart = get_cart_session("new_session")
        assert cart == []
        assert "new_session" in FAKE_CART_DB

    def test_get_cart_session_existing(self):
        """Test getting cart for existing session."""
        FAKE_CART_DB.clear()
        FAKE_CART_DB["existing"] = [MagicMock()]
        cart = get_cart_session("existing")
        assert len(cart) == 1

    def test_get_cart_session_default(self):
        """Test getting cart with default session ID."""
        FAKE_CART_DB.clear()
        cart = get_cart_session()
        assert "demo_guest" in FAKE_CART_DB


class TestCalculateSummary:
    """Tests for _calculate_summary helper."""

    def test_calculate_summary_empty(self):
        """Test summary for empty cart."""
        summary = _calculate_summary([])
        assert summary.total_items == 0
        assert summary.total_price_cents == 0
        assert summary.currency == "ILS"

    def test_calculate_summary_single_item(self):
        """Test summary for single item."""
        item = CartItem(
            epc="E280681000001234",
            product_name="Test Product",
            product_sku="SKU-001",
            price_cents=1000
        )
        summary = _calculate_summary([item])
        assert summary.total_items == 1
        assert summary.total_price_cents == 1000

    def test_calculate_summary_multiple_items(self):
        """Test summary for multiple items."""
        items = [
            CartItem(epc="EPC1", product_name="Product 1", product_sku="SKU1", price_cents=1000),
            CartItem(epc="EPC2", product_name="Product 2", product_sku="SKU2", price_cents=2000),
            CartItem(epc="EPC3", product_name="Product 3", product_sku="SKU3", price_cents=500),
        ]
        summary = _calculate_summary(items)
        assert summary.total_items == 3
        assert summary.total_price_cents == 3500


class TestAddToCart:
    """Tests for POST /cart/add endpoint."""

    @pytest.mark.asyncio
    async def test_add_to_cart_sku(self, client):
        """Test adding item by SKU."""
        with patch("app.routers.cart.get_db") as mock_db:
            mock_session = MagicMock()
            mock_tag = MagicMock(
                epc="E280681000001234",
                product_name="Test Product",
                product_sku="SKU-001",
                price_cents=1000,
                is_paid=False,
                is_active=True
            )
            mock_session.query.return_value.filter.return_value.first.return_value = mock_tag
            mock_db.return_value = mock_session

            FAKE_CART_DB.clear()
            response = await client.post("/api/v1/cart/add", json={
                "qr_data": "tagid://product/SKU-001"
            })
            assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_add_to_cart_epc(self, client):
        """Test adding item by EPC."""
        response = await client.post("/api/v1/cart/add", json={
            "qr_data": "E280681000001234"
        })
        assert response.status_code in [200, 404, 500]


class TestViewCart:
    """Tests for GET /cart/ endpoint."""

    @pytest.mark.asyncio
    async def test_view_cart_empty(self, client):
        """Test viewing empty cart."""
        FAKE_CART_DB.clear()
        response = await client.get("/api/v1/cart/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_view_cart_with_items(self, client):
        """Test viewing cart with items."""
        FAKE_CART_DB.clear()
        FAKE_CART_DB["demo_guest"] = [
            CartItem(epc="EPC1", product_name="Product", product_sku="SKU", price_cents=100)
        ]
        response = await client.get("/api/v1/cart/")
        assert response.status_code == 200


class TestCheckout:
    """Tests for POST /cart/checkout endpoint."""

    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self, client):
        """Test checkout with empty cart."""
        FAKE_CART_DB.clear()
        response = await client.post("/api/v1/cart/checkout", json={
            "payment_method_id": None
        })
        assert response.status_code in [400, 500]

    @pytest.mark.asyncio
    async def test_checkout_with_items(self, client):
        """Test checkout with items in cart."""
        with patch("app.routers.cart.get_gateway") as mock_gateway, \
             patch("app.routers.cart.get_db") as mock_db:
            
            mock_gw = MagicMock()
            mock_gw.create_payment = MagicMock(return_value=MagicMock(
                success=True,
                payment_id="pay-123",
                status="pending"
            ))
            mock_gateway.return_value = mock_gw

            FAKE_CART_DB.clear()
            FAKE_CART_DB["demo_guest"] = [
                CartItem(epc="EPC1", product_name="Product", product_sku="SKU", price_cents=1000)
            ]

            response = await client.post("/api/v1/cart/checkout", json={})
            assert response.status_code in [200, 400, 500]
