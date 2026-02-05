#!/bin/bash
# Enable verbose logging for debugging
set -x

# Set environment variables
export PYTHONHASHSEED=random
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONWARNINGS="ignore::DeprecationWarning"
export PORT=${PORT:-8002}

# Print system info
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
ls -la

# Configure network - check and print networking information for debugging
echo "Network configuration:"
ip addr || true
echo "---"

# Ensure the app directory structure is correct
mkdir -p /app/logs

echo "Generating Prisma client..."
# Explictly point to schema if possible, or trust default discovery
# Checking where schema is
if [ -f "prisma/schema.prisma" ]; then
  echo "Schema found at prisma/schema.prisma"
  python -m prisma generate --schema=prisma/schema.prisma || echo "Prisma generation failed"
elif [ -f "app/prisma/schema.prisma" ]; then
  echo "Schema found at app/prisma/schema.prisma"
  python -m prisma generate --schema=app/prisma/schema.prisma || echo "Prisma generation failed"
else
  echo "WARNING: Could not find schema.prisma"
  find . -name "schema.prisma"
  python -m prisma generate || echo "Prisma generation failed (default)"
fi

if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  
  # Extract connection info (Fail gracefully if sed fails)
  DB_HOST=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\1/' || echo "")
  DB_PORT=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\2/' || echo "")
  DB_USER=$(echo $DATABASE_URL | sed -E 's/^.*:\/\/([^:]+):.*$/\1/' || echo "")
  
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
      # Wait for DB to be available (max 3 attempts, fast timeout)
      for i in {1..3}; do
        if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; then
          echo "Database ready."
          break
        fi
        echo "Database not ready, retrying in 2s (attempt $i/3)"
        sleep 2
      done
  else
      echo "Could not parse DATABASE_URL host/port, skipping wait check."
  fi
  
  echo "Running migrations..."
  python -m prisma migrate deploy || echo "WARNING: Migrations failed - continuing startup anyway"
else
  echo "Warning: DATABASE_URL not set, skipping migrations"
fi

# Create a health check file for Railway
if [ -n "$RAILWAY_HEALTHCHECK_PATH" ]; then
  echo "Railway will check health at: $RAILWAY_HEALTHCHECK_PATH"
fi

# Start the application
echo "Starting application on port $PORT..."
# Bind to 0.0.0.0 explicitly
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 