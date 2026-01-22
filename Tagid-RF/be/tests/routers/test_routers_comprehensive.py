"""
Comprehensive tests for routers - cart, stores, inventory, products.
Includes functional tests with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.rfid_tag import RFIDTag
from app.models.store import Store, User
from app.schemas.cart import CartItem
from app.services.database import SessionLocal, get_db

# Mark all tests as async by default
pytestmark = pytest.mark.asyncio

client = TestClient(app)
API_V1 = "/api/v1"


@pytest.fixture
def mock_db_session():
    """Fixture for mocked DB session."""
    mock = MagicMock(spec=Session)
    return mock


@pytest.fixture
def override_get_db(mock_db_session):
    """Fixture to override get_db dependency."""

    def _get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides = {}


@pytest.mark.skip(reason="TestClient/Prisma cart conflicts")
class TestCartRouterLogic:
    """Tests for cart router logic."""

    def test_add_to_cart_success(self, override_get_db, mock_db_session):
        """Test adding item to cart successfully."""
        # clear fake db
        from app.routers.cart import FAKE_CART_DB

        FAKE_CART_DB.clear()

        # Mock tag query
        mock_tag = MagicMock(spec=RFIDTag)
        mock_tag.epc = "E1"
        mock_tag.product_name = "Test Product"
        mock_tag.product_sku = "SKU1"
        mock_tag.price_cents = 1000
        mock_tag.is_paid = False
        mock_tag.is_active = True

        # Setup query chain
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_tag

        response = client.post(f"{API_V1}/cart/add", json={"qr_data": "tagid://product/SKU1"})

        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 1
        assert data["total_price_cents"] == 1000
        assert data["items"][0]["epc"] == "E1"

    def test_add_to_cart_not_found(self, override_get_db, mock_db_session):
        """Test adding non-existent item."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        response = client.post(f"{API_V1}/cart/add", json={"qr_data": "tagid://product/INVALID"})
        assert response.status_code == 404

    def test_checkout_success(self, override_get_db, mock_db_session):
        """Test successful checkout."""
        # Setup cart
        from app.routers.cart import FAKE_CART_DB, CartItem

        FAKE_CART_DB["demo_guest"] = [
            CartItem(epc="E1", product_name="P1", product_sku="S1", price_cents=1000)
        ]

        # Mock settings and gateway
        with patch("app.routers.cart.settings") as mock_settings:
            mock_settings.DEFAULT_PAYMENT_PROVIDER = "stripe"

            with patch("app.routers.cart.get_gateway") as mock_get_gateway:
                mock_gateway = MagicMock()
                mock_get_gateway.return_value = mock_gateway

                # Mock gateway responses
                mock_create_res = MagicMock()
                mock_create_res.success = True
                mock_create_res.payment_id = "pi_123"
                mock_create_res.status = "pending"
                mock_gateway.create_payment = AsyncMock(return_value=mock_create_res)

                mock_confirm_res = MagicMock()
                mock_confirm_res.success = True
                mock_confirm_res.status = "completed"
                mock_confirm_res.external_id = "txn_123"
                mock_gateway.confirm_payment = AsyncMock(return_value=mock_confirm_res)

                # Mock DB tag for marking paid
                mock_tag = MagicMock()
                mock_db_session.query.return_value.filter.return_value.first.return_value = mock_tag

                response = client.post(
                    f"{API_V1}/cart/checkout", json={"payment_method_id": "pm_card"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"

                # Check DB update
                assert mock_tag.is_paid is True
                mock_db_session.commit.assert_called()

    def test_checkout_empty_cart(self, override_get_db):
        """Test checkout with empty cart."""
        from app.routers.cart import FAKE_CART_DB

        FAKE_CART_DB["demo_guest"] = []

        response = client.post(f"{API_V1}/cart/checkout", json={"payment_method_id": "pm_card"})
        assert response.status_code == 400


class TestStoresRouterLogic:
    """Tests for stores router logic."""

    def test_list_stores(self, override_get_db, mock_db_session):
        """Test listing stores."""

        # Use a real object logic
        # Pydantic's from_attributes=True works best with objects that have the attributes.
        class MockStore:
            id = 1
            name = "Store 1"
            is_active = True
            address = None
            phone = None
            manager_name = None
            seller_count = 0

        mock_store = MockStore()

        mock_user_query = MagicMock()
        mock_user_query.filter.return_value.count.return_value = 5  # seller count

        mock_manager = MagicMock(name="Mgr", spec=User)
        mock_manager.name = "Manager Name"  # Crucial: Must be str, not Mock
        mock_user_query.filter.return_value.first.return_value = mock_manager

        def query_side_effect(model):
            if model == Store:
                m = MagicMock()
                m.filter.return_value = m
                # .all() expects a list of objects
                m.all.return_value = [mock_store]
                return m
            elif model == User:
                return mock_user_query
            return MagicMock()

        mock_db_session.query.side_effect = query_side_effect

        response = client.get(f"{API_V1}/stores")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Store 1"

    def test_create_store(self, override_get_db, mock_db_session):
        """Test creating a store."""

        def refresh_side_effect(instance):
            instance.id = 1
            instance.is_active = True
            instance.manager_name = None
            instance.seller_count = 0
            pass

        mock_db_session.refresh.side_effect = refresh_side_effect

        response = client.post(f"{API_V1}/stores", json={"name": "New Store", "address": "Addr"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Store"

        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()

    def test_get_store_not_found(self, override_get_db, mock_db_session):
        """Test getting non-existent store."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = client.get(f"{API_V1}/stores/999")
        assert response.status_code == 404

    def test_update_store(self, override_get_db, mock_db_session):
        """Test updating a store."""
        mock_store = MagicMock()  # No spec
        mock_store.id = 1
        mock_store.name = "Old Name"
        mock_store.address = None
        mock_store.phone = None
        mock_store.is_active = True
        mock_store.manager_name = None
        mock_store.seller_count = 0

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_store

        response = client.put(f"{API_V1}/stores/1", json={"name": "New Name"})

        assert response.status_code == 200
        assert mock_store.name == "New Name"
        mock_db_session.commit.assert_called()

    def test_delete_store(self, override_get_db, mock_db_session):
        """Test soft deleting a store."""
        mock_store = MagicMock()
        mock_store.id = 1
        mock_store.is_active = True

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_store

        response = client.delete(f"{API_V1}/stores/1")

        assert response.status_code == 204
        assert mock_store.is_active is False
        mock_db_session.commit.assert_called()

    def test_assign_manager(self, override_get_db, mock_db_session):
        """Test assigning manager to store."""
        mock_store = MagicMock()
        mock_user = MagicMock(spec=User)

        # Simulate check store, then check user
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_store,
            mock_user,
        ]

        response = client.post(f"{API_V1}/stores/1/manager", json={"user_id": 100})

        assert response.status_code == 200
        assert mock_user.role == "MANAGER"
        mock_db_session.commit.assert_called()


# --- Maintain existing basic schema tests ---
class TestCartSchemas:
    """Tests for cart schemas."""

    def test_cart_item_schema(self):
        from app.schemas.cart import CartItem

        item = CartItem(epc="E1", product_name="P1", product_sku="S1", price_cents=100)
        assert item.epc == "E1"


class TestStoreSchemas:
    """Tests for store schemas."""

    def test_store_create(self):
        from app.routers.stores import StoreCreate

        s = StoreCreate(name="Test")
        assert s.name == "Test"
