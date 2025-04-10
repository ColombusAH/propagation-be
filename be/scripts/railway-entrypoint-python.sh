#!/bin/bash
set -e

# Print important environment info for debugging (private info redacted)
echo "===== Railway Environment Info ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "PORT: $PORT"
echo "DATABASE_URL is set: $(if [ -n "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo "=================================="

# Function to extract database name from DATABASE_URL
extract_db_info() {
  # Extract database connection parts
  DB_URL=$DATABASE_URL
  DB_HOST=$(echo $DB_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\1/')
  DB_PORT=$(echo $DB_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\2/')
  DB_USER=$(echo $DB_URL | sed -E 's/^.*:\/\/([^:]+):.*$/\1/')
  DB_PASS=$(echo $DB_URL | sed -E 's/^.*:\/\/[^:]+:([^@]+)@.*$/\1/')
  DB_NAME=$(echo $DB_URL | sed -E 's/^.*\/(.*)$/\1/' | sed 's/?.*//')
  
  echo "Database Host: $DB_HOST"
  echo "Database Port: $DB_PORT"
  echo "Database User: $DB_USER"
  echo "Database Name: $DB_NAME"
}

# Function to check if the database server is reachable using direct PostgreSQL connection
check_db_connection() {
  extract_db_info
  
  # Create a temporary .pgpass file for passwordless connection
  echo "$DB_HOST:$DB_PORT:postgres:$DB_USER:$DB_PASS" > ~/.pgpass
  chmod 600 ~/.pgpass
  
  # Try to connect to the PostgreSQL server using psql
  if PGPASSFILE=~/.pgpass psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "postgres" -c "SELECT 1" >/dev/null 2>&1; then
    echo "✅ Successfully connected to PostgreSQL server at $DB_HOST:$DB_PORT"
    rm ~/.pgpass
    return 0
  else
    echo "❌ Failed to connect to PostgreSQL server at $DB_HOST:$DB_PORT"
    rm ~/.pgpass
    return 1
  fi
}

# Function to create database if it doesn't exist
create_database_if_not_exists() {
  extract_db_info
  
  # Create a temporary .pgpass file for passwordless connection
  echo "$DB_HOST:$DB_PORT:postgres:$DB_USER:$DB_PASS" > ~/.pgpass
  echo "$DB_HOST:$DB_PORT:$DB_NAME:$DB_USER:$DB_PASS" >> ~/.pgpass
  chmod 600 ~/.pgpass
  
  echo "Checking if database '$DB_NAME' exists..."
  
  # Check if the database exists
  if PGPASSFILE=~/.pgpass psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "postgres" -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
    echo "Database '$DB_NAME' already exists."
  else
    echo "Database '$DB_NAME' does not exist. Creating it now..."
    PGPASSFILE=~/.pgpass psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "postgres" -c "CREATE DATABASE \"$DB_NAME\";"
    echo "Database '$DB_NAME' created successfully!"
  fi
  
  # Remove the temporary .pgpass file
  rm ~/.pgpass
}

# Generate Prisma client using Python - suppressing deprecation warnings
echo "Generating Prisma client using Python..."
export PYTHONWARNINGS="ignore::DeprecationWarning"
python -m prisma generate
unset PYTHONWARNINGS
echo "Prisma client generated successfully!"

# Set security hardening environment variables
export PYTHONHASHSEED=random  # Enhance DoS protection
export PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files
export PYTHONUNBUFFERED=1  # Disable output buffering

# Wait for database and apply migrations
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database server to be ready..."
  
  # Configure max retries
  max_retries=15
  retry_count=0
  retry_delay=3
  
  # Make sure PostgreSQL client is installed
  if ! command -v psql &> /dev/null; then
    echo "PostgreSQL client is not installed. Installing it now..."
    apt-get update && apt-get install -y --no-install-recommends postgresql-client
  fi
  
  # Try to connect to the database server directly
  until check_db_connection; do
    retry_count=$((retry_count+1))
    
    if [ $retry_count -ge $max_retries ]; then
      echo "Error: Database server connection timed out after $max_retries attempts"
      echo "Continuing anyway - Railway might still be setting up the connection..."
      break
    fi
    
    echo "Database server not ready yet, retrying in ${retry_delay}s (attempt $retry_count/$max_retries)"
    sleep $retry_delay
  done
  
  echo "Attempting to create database and run migrations..."
  
  # Try to create the database regardless of connection success
  # This is necessary for Railway which might have delayed network setup
  echo "Creating database if it doesn't exist..."
  create_database_if_not_exists || true
  
  echo "Running migrations with Python Prisma client..."
  python -m prisma migrate deploy || true
  echo "Migration step completed"
else
  echo "Warning: DATABASE_URL environment variable is not set"
  echo "Skipping database migration steps"
fi

# Make sure PORT is set
if [ -z "$PORT" ]; then
  echo "Warning: PORT environment variable is not set, using default 8000"
  export PORT=8000
fi
echo "Application will listen on port: $PORT"

# Execute the main command and store the process ID
echo "Starting application on port $PORT..."
exec "$@" &
APP_PID=$!

# Function to check application health
check_app_health() {
  local retry_count=0
  local max_retries=30
  local retry_delay=2
  local app_port=$PORT
  local url="http://localhost:${app_port}/health"
  
  echo "Waiting for application to be healthy at ${url}..."
  
  until curl -s "${url}" | grep -q "healthy"; do
    retry_count=$((retry_count+1))
    
    if [ $retry_count -ge $max_retries ]; then
      echo "Error: Application did not become healthy after $max_retries attempts"
      echo "Last curl output: $(curl -s -v "${url}" 2>&1)"
      return 1
    fi
    
    echo "Application not healthy yet, retrying in ${retry_delay}s (attempt $retry_count/$max_retries)"
    sleep $retry_delay
  done
  
  echo "✅ Application is healthy!"
  return 0
}

# Check if the application becomes healthy
check_app_health

# Wait for the application process to finish
wait $APP_PID 