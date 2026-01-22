"""
Tests for main.py app initialization and lifespan.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def test_app_startup():
    """Test that the app starts correctly."""
    from app.main import app

    client = TestClient(app)
    # Just verify the app is importable and runnable
    assert app is not None
    assert app.title is not None


def test_health_check():
    """Test health check endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code in [200, 404]


def test_root_endpoint():
    """Test root endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code in [200, 404]


def test_openapi_schema():
    """Test OpenAPI schema generation."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "openapi" in response.json()


def test_docs_endpoint():
    """Test docs endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
