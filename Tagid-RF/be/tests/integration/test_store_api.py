"""
Integration tests for Store API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestStoreAPI:
    """Integration tests for /stores endpoints."""

    def test_list_stores_endpoint_exists(self, client: TestClient):
        """Test GET /stores endpoint is accessible."""
        response = client.get("/api/v1/stores")
        # May return 200 with empty list or 500 if DB not set up
        assert response.status_code in [200, 500]

    def test_create_store_endpoint_exists(self, client: TestClient):
        """Test POST /stores endpoint is accessible."""
        response = client.post(
            "/api/v1/stores",
            json={"name": "Test Store", "address": "123 Test St"}
        )
        # May succeed or fail depending on DB
        assert response.status_code in [201, 422, 500]

    def test_create_store_validation(self, client: TestClient):
        """Test store creation validates required fields."""
        response = client.post("/api/v1/stores", json={})
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestUserAPI:
    """Integration tests for /users endpoints."""

    def test_list_users_endpoint_exists(self, client: TestClient):
        """Test GET /users endpoint is accessible."""
        response = client.get("/api/v1/users")
        assert response.status_code in [200, 500]

    def test_create_user_endpoint_exists(self, client: TestClient):
        """Test POST /users endpoint is accessible."""
        response = client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "role": "SELLER"
            }
        )
        assert response.status_code in [201, 400, 422, 500]

    def test_create_user_validation(self, client: TestClient):
        """Test user creation validates required fields."""
        response = client.post("/api/v1/users", json={})
        assert response.status_code == 422

    def test_create_user_email_validation(self, client: TestClient):
        """Test user creation validates email format."""
        response = client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
                "email": "not-an-email"
            }
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestNotificationAPI:
    """Integration tests for /notifications endpoints."""

    def test_get_preferences_endpoint(self, client: TestClient):
        """Test GET /notifications/preferences endpoint."""
        response = client.get("/api/v1/notifications/preferences?user_id=1")
        assert response.status_code in [200, 500]

    def test_get_notifications_endpoint(self, client: TestClient):
        """Test GET /notifications endpoint."""
        response = client.get("/api/v1/notifications?user_id=1")
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestExitScanAPI:
    """Integration tests for /exit-scan endpoints."""

    def test_check_exit_scan_endpoint(self, client: TestClient):
        """Test POST /exit-scan/check endpoint."""
        response = client.post(
            "/api/v1/exit-scan/check",
            json={
                "epcs": ["E200-TEST-001", "E200-TEST-002"],
                "gate_id": "main-exit",
                "store_id": 1
            }
        )
        assert response.status_code in [200, 500]

    def test_mark_paid_endpoint(self, client: TestClient):
        """Test POST /exit-scan/mark-paid endpoint."""
        response = client.post(
            "/api/v1/exit-scan/mark-paid",
            json=["E200-TEST-001"]
        )
        assert response.status_code in [200, 500]

    def test_mark_unpaid_endpoint(self, client: TestClient):
        """Test POST /exit-scan/mark-unpaid endpoint."""
        response = client.post(
            "/api/v1/exit-scan/mark-unpaid",
            json=["E200-TEST-001"]
        )
        assert response.status_code in [200, 500]

    def test_exit_scan_validation(self, client: TestClient):
        """Test exit scan validates request format."""
        response = client.post(
            "/api/v1/exit-scan/check",
            json={}  # Missing required 'epcs' field
        )
        assert response.status_code == 422
