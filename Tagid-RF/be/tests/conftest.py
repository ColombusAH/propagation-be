import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.prisma import prisma_client
import pytest_asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_setup():
    """Ensure Prisma client is connected and app state is initialized."""
    try:
        if not prisma_client.client.is_connected():
            await prisma_client.connect()
    except Exception:
        # Ignore already connected or other connection errors in setup
        pass
    
    # Initialize app state if not already set (needed for dependencies)
    if not hasattr(app.state, "prisma") or app.state.prisma is None:
        app.state.prisma = prisma_client
        
    yield prisma_client
    # Optionally disconnect at the very end
    # await prisma_client.disconnect()

@pytest_asyncio.fixture()
async def client() -> AsyncGenerator:
    """Async test client for FastAPI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
