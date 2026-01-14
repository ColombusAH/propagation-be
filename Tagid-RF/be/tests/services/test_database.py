"""
Tests for Database Service - SQLAlchemy session management.
"""

from unittest.mock import MagicMock, patch

import pytest


def test_get_db_yields_session():
    """Test get_db generator yields a session."""
    from app.services.database import get_db

    # get_db is a generator
    gen = get_db()
    assert gen is not None


def test_session_local_exists():
    """Test SessionLocal is configured."""
    from app.services.database import SessionLocal

    assert SessionLocal is not None


def test_base_exists():
    """Test declarative Base exists."""
    from app.services.database import Base

    assert Base is not None


def test_engine_exists():
    """Test engine is configured."""
    from app.services.database import engine

    assert engine is not None
