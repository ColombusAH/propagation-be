# Railway deployment Dockerfile
# This is a wrapper that builds from the be directory

FROM python:3.12-slim

WORKDIR /app

# Copy the entire be directory into the container
COPY be/ .

# Install system dependencies including Node.js for Prisma
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    openssl \
    curl \
    gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g npm@latest

# Set up Python virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir prisma

# Install Prisma with specific version that works with Python
RUN npm install --production && \
    npm install prisma@5.17.0 @prisma/client@5.17.0

# Make entrypoint script executable
RUN chmod +x /app/scripts/railway-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /venv
USER appuser

# Railway will set DATABASE_URL and PORT automatically
ENTRYPOINT ["/app/scripts/railway-entrypoint.sh"]

# Start the app with default settings
# Railway will use PORT environment variable automatically
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"] 