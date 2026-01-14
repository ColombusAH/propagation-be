import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_users_root(client: AsyncClient):
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == {"message": "Users endpoint"}

@pytest.mark.asyncio
async def test_shifts_root(client: AsyncClient):
    response = await client.get("/api/v1/shifts/")
    assert response.status_code == 200
    assert response.json() == {"message": "Shifts endpoint"}

@pytest.mark.asyncio
async def test_schedules_root(client: AsyncClient):
    response = await client.get("/api/v1/schedules/")
    assert response.status_code == 200
    assert response.json() == {"message": "Schedules endpoint"}
