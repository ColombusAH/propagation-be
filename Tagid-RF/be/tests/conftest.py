import os
from datetime import datetime

# Set environment variables before any imports to satisfy Pydantic Settings
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["GOOGLE_CLIENT_ID"] = "test-google-id"

import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Mock create_engine before any imports to prevent DB driver loading issues
mock_engine = MagicMock()
patch("sqlalchemy.create_engine", return_value=mock_engine).start()

# Mock Settings and firebase_admin
mock_settings = MagicMock()
mock_settings.JWT_ALGORITHM = "HS256"  # Set this first!
mock_settings.SECRET_KEY = "test-secret"
mock_settings.PROJECT_NAME = "RFID Test"
mock_settings.API_V1_STR = "/api/v1"
mock_settings.FCM_PROJECT_ID = "test-project"
mock_settings.FCM_SERVER_KEY = "test-key"
mock_settings.GOOGLE_CLIENT_ID = "test-google-id"
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
mock_settings.SECURITY_HEADERS = False
mock_settings.BACKEND_CORS_ORIGINS = ["*"]

patch("app.core.config.get_settings", return_value=mock_settings).start()
patch("app.core.config.settings", mock_settings).start()

# Mock RFID and Tag Listener services to prevent hangs in lifespan
patch(
    "app.services.rfid_reader.rfid_reader_service.connect",
    new_callable=AsyncMock,
    return_value=True,
).start()
patch(
    "app.services.rfid_reader.rfid_reader_service.start_scanning",
    new_callable=AsyncMock,
).start()
patch("app.services.rfid_reader.rfid_reader_service.disconnect", new_callable=AsyncMock).start()
patch("app.services.tag_listener_service.tag_listener_service.start", return_value=None).start()
patch("app.services.tag_listener_service.tag_listener_service.stop", return_value=None).start()

# Mock DB initializations to prevent hangs in lifespan
# patch("app.db.prisma.init_db", new_callable=AsyncMock).start()
# patch("app.db.prisma.shutdown_db", new_callable=AsyncMock).start()
# patch("app.services.database.init_db", return_value=None).start()

# Mock firebase_admin
mock_firebase = MagicMock()
patch("firebase_admin.initialize_app", return_value=mock_firebase).start()
patch("firebase_admin.credentials.Certificate", return_value=MagicMock()).start()

# Global Prisma Mocking to prevent ANY real connection attempts
from prisma import Prisma

patch.object(Prisma, "connect", new_callable=AsyncMock).start()
patch.object(Prisma, "disconnect", new_callable=AsyncMock).start()

# Create a robust mock for the Prisma instance
mock_prisma_instance = MagicMock()
mock_prisma_instance.connect = AsyncMock()
mock_prisma_instance.disconnect = AsyncMock()
mock_prisma_instance.is_connected = MagicMock(return_value=True)

# Configure async context manager support (for `async with prisma_client.client as db:`)
async def async_enter():
    return mock_prisma_instance

async def async_exit(*args):
    pass

mock_prisma_instance.__aenter__ = AsyncMock(side_effect=async_enter)
mock_prisma_instance.__aexit__ = AsyncMock(side_effect=async_exit)

# Setup model mocks on the instance
for model_name in [
    "user",
    "business",
    "store",
    "rfidtag",
    "rfidreader",
    "inventorysnapshot",
    "theftalert",
    "notificationpreference",
    "alertrecipient",
]:
    model_mock = MagicMock()
    model_mock.create = AsyncMock()
    model_mock.update = AsyncMock()
    model_mock.delete = AsyncMock()
    model_mock.find_unique = AsyncMock()
    model_mock.find_first = AsyncMock()
    model_mock.find_many = AsyncMock(return_value=[])
    model_mock.upsert = AsyncMock()
    model_mock.count = AsyncMock(return_value=0)
    
    # Provide a default user if requested
    if model_name == "user":
        # Create a serializable default user
        default_user = SimpleNamespace(
            id="user-1",
            email="test@example.com",
            role="CUSTOMER",
            businessId="biz-1",
            is_active=True,
            password="hashedpassword",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            name="Test User",
            phone="000-000-0000",
            address="Test Address",
            verifiedBy="email"
        )
        model_mock.find_unique.return_value = default_user
        model_mock.find_first.return_value = default_user
        model_mock.create.return_value = default_user
    elif model_name == "business":
        default_biz = SimpleNamespace(id="biz-1", name="Dev Business", slug="dev-business")
        model_mock.find_first.return_value = default_biz
        model_mock.create.return_value = default_biz
    elif model_name == "rfidtag":
        default_tag = SimpleNamespace(
            id="tag-1",
            epc="EPC1234567890",
            productId="SKU-001",
            productDescription="Test Product",
            isPaid=False,
            status="ACTIVE",
            encryptedQr="qr-1"
        )
        model_mock.find_unique.return_value = default_tag
        model_mock.find_first.return_value = default_tag
        model_mock.create.return_value = default_tag

    setattr(mock_prisma_instance, model_name, model_mock)

# Patch the Prisma class to return our mock instance
patch("prisma.Prisma", return_value=mock_prisma_instance).start()

# Patch the PrismaClient.client property to always return our mock
from app.db.prisma import PrismaClient
patch.object(PrismaClient, "client", new_callable=lambda: property(lambda self: mock_prisma_instance)).start()

from app.db.prisma import prisma_client
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_setup():
    """Ensure Prisma client is mocked."""
    # Ensure prisma_client.client is also mocked if it's already instantiated
    if not hasattr(app.state, "prisma") or app.state.prisma is None:
        app.state.prisma = prisma_client

    # Force use of mock instance
    prisma_client._client = mock_prisma_instance

    yield prisma_client


@pytest_asyncio.fixture()
async def client(async_client):
    """Alias for async_client to support tests using 'client'."""
    yield async_client


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator:
    """Async test client for FastAPI."""
    from app.api import deps
    
    # Override get_db to yield our mock instance directly
    async def mock_get_db():
        yield mock_prisma_instance
    
    app.dependency_overrides[deps.get_db] = mock_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture()
def db_session():
    """Fixture for mocked Prisma client session."""
    return prisma_client


@pytest.fixture()
def normal_user_token_headers():
    """Fixture for authenticated user headers (mocked)."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": "test@example.com", "user_id": "user-1", "role": "CUSTOMER"})
    return {"Authorization": f"Bearer {token}"}
