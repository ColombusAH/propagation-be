"""
Tests for stores router to increase coverage.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from app.main import app
from app.models.store import Store
from app.services.database import get_db
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def mock_db():
    mock = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_db, None)


class TestStoresRouterCoverage:
    """Tests for stores router coverage."""

    def test_list_stores_empty(self, mock_db):
        """Test listing stores when none exist."""
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        response = client.get("/api/v1/stores")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_store_not_found(self, mock_db):
        """Test getting a non-existent store."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.get("/api/v1/stores/999")
        assert response.status_code == 404

    def test_delete_store_not_found(self, mock_db):
        """Test deleting a non-existent store."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.delete("/api/v1/stores/999")
        assert response.status_code == 404

    def test_update_store_not_found(self, mock_db):
        """Test updating a non-existent store."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.put("/api/v1/stores/999", json={"name": "New Name"})
        assert response.status_code == 404
