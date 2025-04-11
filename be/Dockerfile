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
ENV PORT=8000
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1

# Railway will set DATABASE_URL and PORT automatically
ENTRYPOINT ["/app/scripts/railway-entrypoint-python.sh"]

# Start the app with PORT from environment variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"] 