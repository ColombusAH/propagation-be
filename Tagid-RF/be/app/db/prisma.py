import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prisma.errors import PrismaError, TableNotFoundError

from prisma import Prisma, register

logger = logging.getLogger(__name__)


class PrismaClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrismaClient, cls).__new__(cls)
        return cls._instance

    @property
    def client(self) -> Prisma:
        if self._client is None:
            self._client = Prisma()
        return self._client

    async def connect(self) -> None:
        """Connect to the database."""
        logger.info("PrismaClient.connect() called")
        try:
            if not self.client.is_connected():
                logger.info("Attempting to connect Prisma client...")
                await self.client.connect()
                register(self.client)
                logger.info("Successfully connected to the database")
            else:
                logger.info("Prisma client already connected")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {str(e)}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        try:
            if self._client:
                await self._client.disconnect()
                self._client = None
                logger.info("Successfully disconnected from the database")
        except PrismaError as e:
            logger.error(f"Error disconnecting from the database: {e}")
            raise

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[Prisma, None]:
        """Get a database connection with context management."""
        try:
            await self.connect()
            yield self.client
        finally:
            await self.disconnect()


prisma_client = PrismaClient()


async def init_db(app: FastAPI) -> None:
    """Initialize database connection on startup."""
    try:
        # Connect to database
        await prisma_client.connect()
        app.state.prisma = prisma_client

        # Verify tables exist by attempting a simple query
        # This will raise TableNotFoundError if tables don't exist
        try:
            await prisma_client.client.user.find_first()
            logger.info("Database connection verified and tables exist")
        except TableNotFoundError:
            logger.error(
                "Database tables not found. Please run migrations:\n"
                "  python scripts/db.py generate\n"
                "  python scripts/db.py deploy"
            )
            await prisma_client.disconnect()
            raise
        except Exception:
            # Other errors (like empty table) are fine, we just want to check if tables exist
            logger.info("Database connection verified")

    except TableNotFoundError:
        logger.error(
            "Database tables not found. Please run migrations:\n"
            "  python scripts/db.py generate\n"
            "  python scripts/db.py deploy"
        )
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def shutdown_db(app: FastAPI) -> None:
    """Close database connection on shutdown."""
    try:
        await prisma_client.disconnect()
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")
        raise
