#!/bin/bash
set -e

# Print important environment info for debugging (private info redacted)
echo "===== Railway Environment Info ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo "PORT: $PORT"
echo "DATABASE_URL is set: $(if [ -n "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo "=================================="

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate
echo "Prisma client generated successfully!"

# Wait for database and apply migrations
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database to be ready..."
  
  # Configure max retries
  max_retries=15
  retry_count=0
  retry_delay=3
  
  # Try Prisma connection
  until npx prisma migrate status >/dev/null 2>&1; do
    retry_count=$((retry_count+1))
    
    if [ $retry_count -ge $max_retries ]; then
      echo "Warning: Database connection timed out after $max_retries attempts"
      echo "Will attempt to continue startup anyway..."
      break
    fi
    
    echo "Database not ready yet, retrying in ${retry_delay}s (attempt $retry_count/$max_retries)"
    sleep $retry_delay
  done
  
  # Deploy migrations if connection was successful
  if [ $retry_count -lt $max_retries ]; then
    echo "Database is ready, applying migrations..."
    npx prisma migrate deploy
    echo "Migrations applied successfully!"
  fi
else
  echo "Warning: DATABASE_URL environment variable is not set"
  echo "Skipping database migration steps"
fi

# Execute the main command
echo "Starting application on port $PORT..."
exec "$@" 