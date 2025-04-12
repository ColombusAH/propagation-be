# Railway deployment Dockerfile
# Simplified version using only Python Prisma client

FROM python:3.12-slim

WORKDIR /app

# Copy the entire be directory into the container
COPY . .

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    openssl \
    curl \
    postgresql-client \
    iputils-ping \
    iproute2 \
    netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir prisma

# Make entrypoint script executable
RUN chmod +x /app/scripts/railway-entrypoint-python.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random
ENV PYTHONWARNINGS="ignore::DeprecationWarning"
ENV PORT=8002
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
# Enable IPv6 support in FastAPI/Uvicorn - bind to all IPv6 addresses
ENV UVICORN_HOST="::"
# Enable private networking for Railway
ENV RAILWAY_PRIVATE_NETWORK=true
# Tell Railway which health check path to use (can be overridden)
ENV RAILWAY_HEALTHCHECK_PATH=/health

# Railway will set DATABASE_URL and PORT automatically
ENTRYPOINT ["/app/scripts/railway-entrypoint-python.sh"]

# Start the app with PORT from environment variable and explicit host configuration for both IPv4 and IPv6
CMD ["sh", "-c", "uvicorn app.main:app --host ${UVICORN_HOST:-::} --port ${PORT:-8002}"] 