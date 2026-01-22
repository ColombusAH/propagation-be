"""
Mock-based tests for cart endpoints (no DB required).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import deps
from tests.mock_utils import MockModel

# Import USER_CARTS to manipulate it directly if needed for setup
from app.api.v1.endpoints.cart import USER_CARTS

client = TestClient(app)


def override_user(user):
    app.dependency_overrides[deps.get_current_active_user] = lambda: user


class TestCartEndpointsMock:
    """Tests for cart endpoints using mocks."""

    def setup_method(self):
        # Clear cart before each test
        USER_CARTS.clear()

    def teardown_method(self):
        app.dependency_overrides.clear()
        USER_CARTS.clear()

    def test_view_cart_empty(self):
        """Test viewing an empty cart."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        response = client.get("/api/v1/cart/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 0
        assert data["items"] == []

    @patch("app.services.tag_encryption.get_encryption_service")
    @patch("app.api.v1.endpoints.cart.prisma_client")
    def test_add_to_cart_valid_epc(self, mock_prisma_wrapper, mock_get_enc_svc):
        """Test adding item by straight EPC."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        # Mock encryption to fail (trigger fallback)
        mock_svc = MagicMock()
        mock_svc.decrypt_qr.side_effect = Exception("Decryption failed")
        mock_get_enc_svc.return_value = mock_svc

        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        # Tag exists, not paid
        tag = MockModel(epc="E123", isPaid=False, productDescription="Test Item", productId="SKU1")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        response = client.post("/api/v1/cart/add", json={"qr_data": "E123"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 1
        assert data["items"][0]["epc"] == "E123"

    @patch("app.services.tag_encryption.get_encryption_service")
    @patch("app.api.v1.endpoints.cart.prisma_client")
    def test_add_to_cart_paid_item(self, mock_prisma_wrapper, mock_get_enc_svc):
        """Test adding a paid item fails."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        # Mock encryption to fail
        mock_svc = MagicMock()
        mock_svc.decrypt_qr.side_effect = Exception("Decryption failed")
        mock_get_enc_svc.return_value = mock_svc

        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        tag = MockModel(epc="E123", isPaid=True)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        response = client.post("/api/v1/cart/add", json={"qr_data": "E123"})
        assert response.status_code == 400
        assert "already been paid" in response.json()["detail"]

    @patch("app.services.tag_encryption.get_encryption_service")
    @patch("app.api.v1.endpoints.cart.prisma_client")
    def test_add_to_cart_encrypted_qr(self, mock_prisma_wrapper, mock_get_enc_svc):
        """Test adding item by Encrypted QR."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        # Mock encryption
        mock_svc = MagicMock()
        mock_svc.decrypt_qr.return_value = "E999"
        mock_get_enc_svc.return_value = mock_svc

        # Mock DB
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        tag = MockModel(epc="E999", isPaid=False, productDescription="Encrypted Item")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)

        response = client.post("/api/v1/cart/add", json={"qr_data": "ENCRYPTED_DATA"})
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["epc"] == "E999"

    @patch("app.api.v1.endpoints.cart.prisma_client")
    def test_sync_bath_cart(self, mock_prisma_wrapper):
        """Test syncing bath cart with multiple items."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        tag1 = MockModel(epc="E1", isPaid=False, productDescription="Item 1")
        tag2 = MockModel(epc="E2", isPaid=True)  # Should be ignored/logged warning

        async def mock_find_unique(where):
            epc = where.get("epc")
            if epc == "E1":
                return tag1
            if epc == "E2":
                return tag2
            return None

        mock_db.rfidtag.find_unique = AsyncMock(side_effect=mock_find_unique)

        response = client.post("/api/v1/cart/sync-bath", json=["E1", "E2", "E3"])
        assert response.status_code == 200
        data = response.json()
        # Only E1 should be added
        assert data["total_items"] == 1
        assert data["items"][0]["epc"] == "E1"

    def test_clear_cart(self):
        """Test clearing the cart."""
        mock_user = MockModel(id="u1", isActive=True)
        override_user(mock_user)

        # Pre-populate cart
        from app.schemas.cart import CartItem

        USER_CARTS["u1"] = [CartItem(epc="E1", product_name="P1", product_sku="S1", price_cents=0)]

        response = client.delete("/api/v1/cart/clear")
        assert response.status_code == 200
        assert len(USER_CARTS["u1"]) == 0
