#!/bin/bash
set -e

# Set environment variables
export PYTHONHASHSEED=random
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONWARNINGS="ignore::DeprecationWarning"
export PORT=${PORT:-8000}

# Configure network - check and print networking information for debugging
echo "Network configuration:"
ip addr
echo "---"

echo "Generating Prisma client..."
python -m prisma generate

if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  
  # Extract connection info
  DB_HOST=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\1/')
  DB_PORT=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\2/')
  DB_USER=$(echo $DATABASE_URL | sed -E 's/^.*:\/\/([^:]+):.*$/\1/')
  DB_NAME=$(echo $DATABASE_URL | sed -E 's/^.*\/(.*)$/\1/' | sed 's/?.*//')
  
  # Wait for DB to be available (max 5 attempts)
  for i in {1..5}; do
    if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; then
      break
    fi
    echo "Database not ready, retrying in 3s (attempt $i/5)"
    sleep 3
  done
  
  echo "Running migrations..."
  python -m prisma migrate deploy || true
else
  echo "Warning: DATABASE_URL not set, skipping migrations"
fi

echo "Starting application on port $PORT with host ${UVICORN_HOST:-0.0.0.0}..."
exec "$@" 