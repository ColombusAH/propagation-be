"""
Tests for Products Router to increase coverage.
Covers QR generation for products.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.routers.products import router

@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router, prefix="/products")
    return app

@pytest.fixture
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_generate_product_qr_success(client: AsyncClient):
    """Test successful QR code generation for a SKU."""
    response = await client.get("/products/qr/SKU123")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

@pytest.mark.asyncio
async def test_generate_product_qr_empty_sku(client: AsyncClient):
    """
    Test edge cases for SKU. 
    Note: FastAPI path parameters won't match empty strings if the route is /qr/{sku}.
    We test the logic inside if we could, but here we test a valid SKU.
    """
    # Test with a very long SKU or special characters
    response = await client.get("/products/qr/special-@#$-123")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
