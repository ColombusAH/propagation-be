"""
SQLAlchemy database setup for RFID tracking system.
"""

from typing import Generator

from app.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

settings = get_settings()

# Create SQLAlchemy engine
# Note: For RFID system, we'll use a separate database URL if provided
# Otherwise, we'll use the same database with a different schema or connection
# Otherwise, we'll use the same database with a different schema or connection
RFID_DATABASE_URL = settings.RFID_DATABASE_URL or settings.DATABASE_URL

# Replace postgresql:// with postgresql+psycopg:// for SQLAlchemy if needed
if RFID_DATABASE_URL and RFID_DATABASE_URL.startswith("postgresql://"):
    RFID_DATABASE_URL = RFID_DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

engine = create_engine(
    RFID_DATABASE_URL,
    pool_pre_ping=True,
    echo=getattr(settings, "DEBUG", False),
    pool_size=getattr(settings, "DATABASE_POOL_SIZE", 5),
    max_overflow=getattr(settings, "DATABASE_MAX_OVERFLOW", 10),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency function to get database session.
    Use with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)
