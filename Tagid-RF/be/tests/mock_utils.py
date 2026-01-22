"""
Utilities for mocking database models in tests.
"""

from typing import Any


class MockModel:
    """A simple class to mock database models with attribute access."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, name: str) -> Any:
        # Return None for missing attributes to simulate database models
        # (or at least avoid MagicMock returning Mocks)
        return None
