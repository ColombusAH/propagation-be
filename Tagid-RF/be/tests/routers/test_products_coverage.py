"""
Tests for Products Router to increase coverage.
Covers QR code generation endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestProductsRouter:
    """Tests for products router."""

    def test_generate_product_qr_success(self):
        """Test successful QR code generation."""
        response = client.get("/api/v1/products/qr/SKU-123")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        # Check we get binary PNG data
        assert len(response.content) > 100

    def test_generate_product_qr_different_sku(self):
        """Test QR code generation with different SKU."""
        response = client.get("/api/v1/products/qr/ABC-456")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_generate_product_qr_special_chars(self):
        """Test QR code generation with special characters in SKU."""
        response = client.get("/api/v1/products/qr/SKU_123-ABC")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
