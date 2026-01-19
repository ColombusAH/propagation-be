"""
Tests for Cart API - Simplified tests using TestClient with mocking.
"""

from unittest.mock import MagicMock, patch

import pytest
from app.routers.cart import FAKE_CART_DB, _calculate_summary, router
from app.schemas.cart import CartItem
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cart():
    """Clear fake cart before each test."""
    FAKE_CART_DB.clear()
    yield
    FAKE_CART_DB.clear()


def test_view_empty_cart():
    """Test viewing an empty cart."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 0
    assert data["total_price_cents"] == 0


def test_checkout_empty_cart():
    """Checkout with empty cart should fail."""
    response = client.post(
        "/checkout", json={"payment_method_id": "pm_test", "email": "test@example.com"}
    )

    assert response.status_code == 400
    assert "Cart is empty" in response.json()["detail"]


def test_calculate_summary():
    """Test cart summary calculation."""
    items = [
        CartItem(epc="E1", product_name="P1", product_sku="S1", price_cents=500),
        CartItem(epc="E2", product_name="P2", product_sku="S2", price_cents=1500),
    ]

    summary = _calculate_summary(items)

    assert summary.total_items == 2
    assert summary.total_price_cents == 2000
    assert summary.currency == "ILS"


def test_calculate_summary_empty():
    """Test empty cart summary."""
    summary = _calculate_summary([])

    assert summary.total_items == 0
    assert summary.total_price_cents == 0
