"""
Tests for Inventory Router to increase coverage.
Covers inventory summary aggregation.
"""

from unittest.mock import MagicMock

import pytest
from app.routers.inventory import router
from app.services.database import get_db
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router, prefix="/inventory")
    return app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    mock_query = MagicMock()
    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    return db, mock_query


@pytest.fixture
async def client(test_app, mock_db):
    test_app.dependency_overrides[get_db] = lambda: mock_db[0]
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac
    test_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_inventory_summary_empty(client: AsyncClient, mock_db):
    """Test summary when no tags exist."""
    db, mock_query = mock_db
    mock_query.all.return_value = []

    response = await client.get("/inventory/summary")
    assert response.status_code == 200
    assert response.json()["total_products"] == 0
    assert response.json()["total_value_cents"] == 0


@pytest.mark.asyncio
async def test_get_inventory_summary_with_data(client: AsyncClient, mock_db):
    """Test aggregation with mocked rows."""
    db, mock_query = mock_db

    # Mocked results row (keyed tuple)
    mock_row = MagicMock()
    mock_row.product_sku = "SKU1"
    mock_row.product_name = "Item 1"
    mock_row.price_cents = 1000
    mock_row.total = 5
    mock_row.available = 3
    mock_row.sold = 2

    mock_query.all.return_value = [mock_row]

    response = await client.get("/inventory/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products"] == 1
    assert data["products"][0]["available_items"] == 3
    assert data["total_value_cents"] == 3000  # 3 available * 1000 cents
