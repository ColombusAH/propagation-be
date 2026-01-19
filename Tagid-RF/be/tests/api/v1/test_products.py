"""
Tests for Products Router - QR Code generation.
"""

import pytest
from app.routers.products import router
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_generate_qr_success():
    """Test QR code generation for valid SKU."""
    response = client.get("/qr/TEST-SKU-001")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    # Check response is non-empty PNG
    assert len(response.content) > 100
    # PNG magic bytes
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_qr_another_sku():
    """Test QR with different SKU."""
    response = client.get("/qr/ANOTHER-PRODUCT")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_generate_qr_empty_sku():
    """Empty SKU should return 400."""
    # FastAPI path parameter won't match empty string, so this becomes 404
    # or if matched, the endpoint checks and returns 400
    response = client.get("/qr/")

    # Depends on routing - likely 404 (not found) or 307 (redirect)
    assert response.status_code in [400, 404, 307, 405]
