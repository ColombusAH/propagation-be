"""
Mock-based tests for tag registration endpoints (no DB required).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.dependencies import get_db
from tests.mock_utils import MockModel

client = TestClient(app)


class TestTagRegistrationEndpointsMock:
    """Tests for tag registration and product linking endpoints using mocks."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    @patch("app.api.v1.endpoints.tag_registration.generate_encrypted_qr_data")
    @patch("uuid.uuid4")
    def test_register_tag_new(self, mock_uuid, mock_gen_data, mock_gen_qr):
        """Test registering a new tag."""
        mock_uuid.return_value = "new-uuid"
        mock_gen_data.return_value = "RFID:HASH"
        mock_gen_qr.return_value = "img-data"

        mock_db = MagicMock()
        mock_db.rfidtag.find_unique = AsyncMock(return_value=None)

        new_tag = MockModel(
            id="new-uuid", epc="E123", status="UNREGISTERED", encryptedQr="RFID:HASH"
        )
        mock_db.rfidtag.create = AsyncMock(return_value=new_tag)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/tags/register", json={"epc": "E123"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "new-uuid"
        assert data["qr_code"] == "img-data"

        mock_db.rfidtag.create.assert_awaited_once()

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    def test_register_tag_existing(self, mock_gen_qr):
        """Test registering an existing tag."""
        mock_gen_qr.return_value = "img-data"

        mock_db = MagicMock()
        existing_tag = MockModel(
            id="t1", epc="E123", status="UNREGISTERED", encryptedQr="RFID:EXISTING"
        )
        mock_db.rfidtag.find_unique = AsyncMock(return_value=existing_tag)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/tags/register", json={"epc": "E123"})
        assert response.status_code == 200
        assert response.json()["id"] == "t1"

        mock_db.rfidtag.create.assert_not_called()

    def test_create_product(self):
        """Test creating a product."""
        mock_db = MagicMock()
        product = MockModel(
            id="p1", name="Prod 1", price=10.0, storeId="s1", sku="SKU1", category="Cat"
        )
        mock_db.product.create = AsyncMock(return_value=product)

        app.dependency_overrides[get_db] = lambda: mock_db

        payload = {
            "name": "Prod 1",
            "price": 10.0,
            "store_id": "s1",
            "sku": "SKU1",
            "category": "Cat",
        }
        response = client.post("/api/v1/tags/products", json=payload)
        assert response.status_code == 200
        assert response.json()["id"] == "p1"

    def test_list_products(self):
        """Test listing products for a store."""
        mock_db = MagicMock()
        products = [MockModel(id="p1", name="P1", price=10.0, sku="SKU1", category="C1")]
        mock_db.product.find_many = AsyncMock(return_value=products)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/products/store/s1")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_unregistered_tags(self):
        """Test listing unregistered tags."""
        mock_db = MagicMock()
        tags = [MockModel(id="t1", epc="E1", status="UNREGISTERED", productId=None, isPaid=False)]
        mock_db.rfidtag.find_many = AsyncMock(return_value=tags)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/unregistered")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    def test_link_tag_to_product(self, mock_gen_qr):
        """Test linking tag to product."""
        mock_gen_qr.return_value = "img"

        mock_db = MagicMock()
        tag = MockModel(id="t1", epc="E1", status="UNREGISTERED", encryptedQr="QR")
        product = MockModel(id="p1", name="Prod 1", price=10.0)

        mock_db.rfidtag.find_unique = AsyncMock(side_effect=[tag, None])  # call 1: find tag
        mock_db.product.find_unique = AsyncMock(return_value=product)

        updated_tag = MockModel(
            id="t1",
            epc="E1",
            status="REGISTERED",
            encryptedQr="QR",
            productId="p1",
            productDescription="Prod 1",
            isPaid=False,
        )
        mock_db.rfidtag.update = AsyncMock(return_value=updated_tag)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/tags/t1/link-product", json={"product_id": "p1"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REGISTERED"
        assert data["product_id"] == "p1"

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    def test_get_tag_qr(self, mock_gen_qr):
        """Test getting QR for a tag."""
        mock_gen_qr.return_value = "img"
        mock_db = MagicMock()
        tag = MockModel(id="t1", epc="E1", encryptedQr="QR")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/t1/qr")
        assert response.status_code == 200
        assert response.json()["qr_code"] == "img"

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    def test_get_tag_qr_missing_initially(self, mock_gen_qr):
        """Test getting QR for a tag that doesn't have it yet (triggers generation)."""
        mock_gen_qr.return_value = "img"
        mock_db = MagicMock()
        tag = MockModel(id="t1", epc="E1", encryptedQr=None)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        mock_db.rfidtag.update = AsyncMock()
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/t1/qr")
        assert response.status_code == 200
        mock_db.rfidtag.update.assert_awaited_once()

    @patch("app.api.v1.endpoints.tag_registration.generate_qr_code")
    def test_get_tag_details(self, mock_gen_qr):
        """Test getting tag details."""
        mock_gen_qr.return_value = "img"

        mock_db = MagicMock()
        tag = MockModel(
            id="t1", epc="E1", status="REGISTERED", encryptedQr="QR", productId="p1", isPaid=True
        )
        product = MockModel(id="p1", name="Prod 1", price=50.0)

        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        mock_db.product.find_unique = AsyncMock(return_value=product)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/t1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "t1"
        assert data["product_name"] == "Prod 1"

    def test_get_tag_not_found(self):
        """Test getting non-existent tag."""
        mock_db = MagicMock()
        mock_db.rfidtag.find_unique = AsyncMock(return_value=None)
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/tags/ghost")
        assert response.status_code == 404

    def test_link_tag_not_found(self):
        """Test linking non-existent tag."""
        mock_db = MagicMock()
        mock_db.rfidtag.find_unique = AsyncMock(return_value=None)
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/tags/ghost/link-product", json={"product_id": "p1"})
        assert response.status_code == 404

    def test_link_product_not_found(self):
        """Test linking to non-existent product."""
        mock_db = MagicMock()
        tag = MockModel(id="t1", epc="E1")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        mock_db.product.find_unique = AsyncMock(return_value=None)
        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.post("/api/v1/tags/t1/link-product", json={"product_id": "ghost"})
        assert response.status_code == 404

    def test_generate_qr_code_helper(self):
        """Test the actual generate_qr_code helper function execution."""
        from app.api.v1.endpoints.tag_registration import generate_qr_code

        qr_data = generate_qr_code("test-data")
        assert qr_data.startswith("data:image/png;base64,")
