from prisma import Prisma
from prisma.errors import PrismaError
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

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
        try:
            await self.client.connect()
            logger.info("Successfully connected to the database")
        except PrismaError as e:
            logger.error(f"Failed to connect to the database: {e}")
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
        await prisma_client.connect()
        app.state.prisma = prisma_client
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