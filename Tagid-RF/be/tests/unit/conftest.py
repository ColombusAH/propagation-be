"""
Unit tests pytest configuration.
This conftest overrides the parent conftest to avoid loading
the full application which requires firebase_admin.
"""

import pytest


# Override the setup_test_database from parent conftest
@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Skip database setup for unit tests - they should use mocks."""
    yield


# Skip fixtures that require app imports
@pytest.fixture
def client():
    """Skip client fixture for unit tests."""
    pytest.skip("Use mocked clients for unit tests")


@pytest.fixture
async def async_client():
    """Skip async_client fixture for unit tests."""
    pytest.skip("Use mocked clients for unit tests")


@pytest.fixture
async def db():
    """Skip db fixture for unit tests."""
    pytest.skip("Use mocked database for unit tests")
