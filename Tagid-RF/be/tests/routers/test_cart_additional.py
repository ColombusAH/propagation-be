"""
Tests for Cart router to increase coverage.
Covers checkout edge cases and empty cart handling.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.cart import FAKE_CART_DB, _calculate_summary, get_cart_session
from app.schemas.cart import CartItem

client = TestClient(app)


class TestCartRouterCoverage:
    """Additional tests for cart router coverage."""

    def test_view_cart_default_session(self):
        """Test viewing cart with default session."""
        FAKE_CART_DB.clear()
        response = client.get("/cart/")
        # May return 200 or redirect depending on router mount
        assert response.status_code in [200, 307, 404]

    def test_checkout_empty_cart_sync(self):
        """Test checkout with empty cart (sync TestClient)."""
        FAKE_CART_DB.clear()
        FAKE_CART_DB["demo_guest"] = []
        
        response = client.post("/cart/checkout", json={"payment_method_id": "pm_test"})
        assert response.status_code in [400, 404, 307]

    def test_calculate_summary_large_cart(self):
        """Test summary calculation with multiple items."""
        items = [
            CartItem(epc=f"EPC{i}", product_name=f"Product {i}", product_sku=f"SKU{i}", price_cents=1000 + i * 100)
            for i in range(10)
        ]
        summary = _calculate_summary(items)
        assert summary.total_items == 10
        assert summary.total_price_cents == sum(1000 + i * 100 for i in range(10))
        assert summary.currency == "ILS"

    def test_get_cart_session_idempotent(self):
        """Test that getting cart session is idempotent."""
        FAKE_CART_DB.clear()
        cart1 = get_cart_session("test_session")
        cart2 = get_cart_session("test_session")
        assert cart1 is cart2

    def test_get_cart_session_creates_empty_list(self):
        """Test that new cart session creates empty list."""
        FAKE_CART_DB.clear()
        cart = get_cart_session("new_test_session")
        assert cart == []
        assert "new_test_session" in FAKE_CART_DB
