import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the /health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root (/) endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "RFID MVP API" in response.json()["message"]


@pytest.mark.asyncio
async def test_healthz_check(client: AsyncClient):
    """Test the /healthz endpoint."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
