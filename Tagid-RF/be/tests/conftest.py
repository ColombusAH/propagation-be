"""
Pytest configuration and fixtures for the Shifty RFID system tests.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest

# Only import these for integration tests
# This prevents loading firebase_admin during unit tests


def _get_app():
    """Lazy load the FastAPI app."""
    from app.main import app
    return app


def _get_prisma():
    """Lazy load the Prisma client."""
    from app.db.prisma import prisma_client
    return prisma_client


def _get_settings():
    """Lazy load settings."""
    from app.core.config import settings
    return settings


# Configure asyncio for tests
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Set up test environment variables at module level to ensure they are available
# during test collection, as some modules import config at module level.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_unit_tests")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_google_client_id")
os.environ.setdefault("RFID_DATABASE_URL", "postgresql://test:test@localhost:5432/test_rfid_db")


@pytest.fixture
def client() -> Generator:
    """Create a test client for synchronous tests."""
    from fastapi.testclient import TestClient
    app = _get_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Provide async HTTP client for testing."""
    from httpx import ASGITransport, AsyncClient
    app = _get_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=False)
async def setup_test_database():
    """Set up test database connection."""
    prisma_client = _get_prisma()
    await prisma_client.connect()
    yield
    await prisma_client.disconnect()


@pytest.fixture
async def db():
    """Provide database access for tests."""
    prisma_client = _get_prisma()
    yield prisma_client.client


@pytest.fixture
async def test_user(db):
    """Create a test user."""
    from app.core.security import get_password_hash

    user = await db.user.create(
        data={
            "email": "test@example.com",
            "hashedPassword": get_password_hash("testpassword123"),
            "fullName": "Test User",
            "role": "CUSTOMER",
            "phoneNumber": "+972501234567",
        }
    )
    yield user
    # Cleanup
    await db.user.delete(where={"id": user.id})


@pytest.fixture
async def test_manager(db):
    """Create a test manager user."""
    from app.core.security import get_password_hash

    manager = await db.user.create(
        data={
            "email": "manager@example.com",
            "hashedPassword": get_password_hash("managerpass123"),
            "fullName": "Test Manager",
            "role": "MANAGER",
            "phoneNumber": "+972501234568",
        }
    )
    yield manager
    # Cleanup
    await db.user.delete(where={"id": manager.id})


@pytest.fixture
async def test_admin(db):
    """Create a test admin user."""
    from app.core.security import get_password_hash

    admin = await db.user.create(
        data={
            "email": "admin@example.com",
            "hashedPassword": get_password_hash("adminpass123"),
            "fullName": "Test Admin",
            "role": "ADMIN",
            "phoneNumber": "+972501234569",
        }
    )
    yield admin
    # Cleanup
    await db.user.delete(where={"id": admin.id})


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    from app.core.security import create_access_token

    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_auth_headers(test_manager):
    """Get authentication headers for test manager."""
    from app.core.security import create_access_token

    token = create_access_token(subject=test_manager.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin):
    """Get authentication headers for test admin."""
    from app.core.security import create_access_token

    token = create_access_token(subject=test_admin.id)
    return {"Authorization": f"Bearer {token}"}
