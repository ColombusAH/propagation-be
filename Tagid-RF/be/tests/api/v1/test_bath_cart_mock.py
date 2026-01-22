"""
Mock-based tests for Bath Cart endpoints (no DB required).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.bath_cart import _bath_carts
from app.db.dependencies import get_db
from app.main import app
from tests.mock_utils import MockModel

client = TestClient(app)


class TestBathCartEndpointsMock:
    """Tests for bath cart endpoints using mocks."""

    def setup_method(self):
        _bath_carts.clear()

    def teardown_method(self):
        app.dependency_overrides.clear()
        _bath_carts.clear()

    def test_scan_tag_to_cart_success(self):
        """Test scanning a tag into the bath cart."""
        mock_db = MagicMock()

        # Reader exists and is BATH
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        # Tag exists and not paid
        tag = MockModel(id="t1", epc="E1", isPaid=False, productId="p1")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        mock_db.rfidtag.update = AsyncMock()

        # Product info
        product = MockModel(id="p1", name="Product 1", price=100.0)
        mock_db.product.find_unique = AsyncMock(return_value=product)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/b1/scan", json={"epc": "E1"})
        assert response.status_code == 200
        data = response.json()
        assert data["tag_id"] == "t1"
        assert data["product_name"] == "Product 1"
        assert "t1" in _bath_carts["b1"]
        mock_db.rfidtag.update.assert_awaited_once()

    def test_scan_tag_wrong_reader_type(self):
        """Test scanning into a non-bath reader."""
        mock_db = MagicMock()
        reader = MockModel(id="r1", type="GATE")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/r1/scan", json={"epc": "E1"})
        assert response.status_code == 404
        assert "Bath reader not found" in response.json()["detail"]

    def test_scan_tag_already_paid(self):
        """Test scanning a paid tag."""
        mock_db = MagicMock()
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        tag = MockModel(id="t1", epc="E1", isPaid=True)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/b1/scan", json={"epc": "E1"})
        assert response.status_code == 400
        assert "already paid" in response.json()["detail"]

    def test_get_cart_contents(self):
        """Test retrieving bath cart contents."""
        mock_db = MagicMock()
        reader = MockModel(id="b1", name="Bath 1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        # Pre-fill cart
        _bath_carts["b1"] = ["t1", "t2"]

        tag1 = MockModel(id="t1", epc="E1", productId="p1")
        tag2 = MockModel(id="t2", epc="E2", productId=None, productDescription="Loose Item")

        async def mock_find_tag(where):
            if where["id"] == "t1":
                return tag1
            if where["id"] == "t2":
                return tag2
            return None

        mock_db.rfidtag.find_unique.side_effect = mock_find_tag

        product = MockModel(id="p1", name="P1", price=50.0)
        mock_db.product.find_unique = AsyncMock(return_value=product)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/bath/b1/cart")
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 2
        assert data["total_price"] == 50.0  # Only tag1 has a product with price

    def test_remove_from_cart(self):
        """Test removing an item from the bath cart."""
        mock_db = MagicMock()
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)
        mock_db.rfidtag.update = AsyncMock()

        _bath_carts["b1"] = ["t1"]

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.delete("/api/v1/bath/b1/cart/t1")
        assert response.status_code == 200
        assert "removed" in response.json()["message"]
        assert "t1" not in _bath_carts["b1"]
        mock_db.rfidtag.update.assert_awaited_once()

    @patch("uuid.uuid4")
    def test_checkout_success(self, mock_uuid):
        """Test successful checkout."""
        mock_uuid.return_value = MagicMock(hex="ABCDEF12")
        mock_db = MagicMock()
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        _bath_carts["b1"] = ["t1"]
        tag = MockModel(id="t1", epc="E1", productId="p1")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        product = MockModel(id="p1", price=150.0)
        mock_db.product.find_unique = AsyncMock(return_value=product)
        mock_db.rfidtag.update = AsyncMock()

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/b1/checkout", json={"payment_method": "card"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_price"] == 150.0
        assert data["order_id"] == "ORD-ABCDEF12"
        assert "t1" not in _bath_carts["b1"]
        mock_db.rfidtag.update.assert_awaited_once()

    def test_checkout_empty_cart(self):
        """Test checkout with an empty cart."""
        mock_db = MagicMock()
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/b1/checkout", json={})
        assert response.status_code == 400
        assert "Cart is empty" in response.json()["detail"]

    def test_clear_cart_endpoint(self):
        """Test clearing the cart endpoint."""
        mock_db = MagicMock()
        reader = MockModel(id="b1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)
        mock_db.rfidtag.update = AsyncMock()

        _bath_carts["b1"] = ["t1", "t2"]

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/bath/b1/clear")
        assert response.status_code == 200
        assert len(_bath_carts["b1"]) == 0
        assert mock_db.rfidtag.update.await_count == 2
