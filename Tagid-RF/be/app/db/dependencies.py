import logging

from fastapi import HTTPException, Request, status
from prisma import Prisma

logger = logging.getLogger(__name__)


async def get_db(request: Request) -> Prisma:
    """
    FastAPI dependency to get the Prisma client instance.

    Retrieves the Prisma client attached to the application state during startup.
    Ensures the client is connected before returning it.
    """
    try:
        # Access the PrismaClient wrapper instance from app state
        prisma_client_wrapper = request.app.state.prisma
        if not prisma_client_wrapper or not hasattr(prisma_client_wrapper, "client"):
            logger.error("Prisma client wrapper not found in application state.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service is not configured correctly.",
            )

        # Get the actual Prisma client
        db = prisma_client_wrapper.client
        if not db.is_connected():
            logger.warning(
                "Database client was not connected. Attempting to reconnect."
            )
            try:
                await db.connect()
            except Exception as connect_error:
                logger.error(
                    f"Failed to reconnect database: {connect_error}", exc_info=True
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not connect to the database.",
                )
        return db
    except HTTPException:
        raise
    except AttributeError:
        logger.error(
            "State attribute missing, Prisma client likely not initialized.",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service initialization error.",
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while getting DB connection: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while accessing the database.",
        )
