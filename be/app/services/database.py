"""
SQLAlchemy database setup for RFID tracking system.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings
from typing import Generator

settings = get_settings()

# Create SQLAlchemy engine
# Note: For RFID system, we'll use a separate database URL if provided
# Otherwise, we'll use the same database with a different schema or connection
RFID_DATABASE_URL = getattr(settings, 'RFID_DATABASE_URL', settings.DATABASE_URL)

# Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy if needed
if RFID_DATABASE_URL.startswith('postgresql://'):
    RFID_DATABASE_URL = RFID_DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)

engine = create_engine(
    RFID_DATABASE_URL,
    pool_pre_ping=True,
    echo=getattr(settings, 'DEBUG', False),
    pool_size=getattr(settings, 'DATABASE_POOL_SIZE', 5),
    max_overflow=getattr(settings, 'DATABASE_MAX_OVERFLOW', 10),
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


