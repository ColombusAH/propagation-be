from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.prisma import init_db, shutdown_db
from app.api.v1.api import api_router
import logging
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)
settings = get_settings()

# Custom security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if settings.SECURITY_HEADERS:
            # Set security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Cache-Control"] = "no-store"
            response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), microphone=()"
        return response

# Rate limiting middleware - commented out as it requires redis
# To use this, install and configure redis and uncomment this code
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.middleware import SlowAPIMiddleware
# limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("Starting up application...")
    await init_db(app)
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await shutdown_db(app)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Uncomment to add rate limiting
# app.state.limiter = limiter
# app.add_middleware(SlowAPIMiddleware)

# Root endpoint - needed for Railway's default health check
@app.get("/")
async def root():
    """Root endpoint for Railway's default health check."""
    return {"status": "ok"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Root health check endpoint for Railway."""
    return {"status": "healthy"}

@app.get("/healthz")
async def healthz_check():
    """Health check endpoint for internal communication."""
    return {"status": "ok"}