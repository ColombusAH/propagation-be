#!/bin/bash
set -e

# Function to check if PostgreSQL is up (without using nc)
check_postgres_connection() {
  local host=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\1/')
  local port=$(echo $DATABASE_URL | sed -E 's/^.*@([^:]+):([0-9]+)\/.*$/\2/')
  local user=$(echo $DATABASE_URL | sed -E 's/^.*:\/\/([^:]+):.*$/\1/')
  local db=$(echo $DATABASE_URL | sed -E 's/^.*\/(.*)$/\1/')

  echo "Testing PostgreSQL connection to $host:$port as $user..."
  
  # Try to connect using /dev/tcp bash feature instead of nc
  if (</dev/tcp/$host/$port) 2>/dev/null; then
    echo "✓ Successfully connected to PostgreSQL server at $host:$port"
    return 0
  else
    echo "✗ Failed to connect to PostgreSQL server at $host:$port"
    return 1
  fi
}

# Function to wait for the database to be ready
wait_for_db() {
  echo "Waiting for database to be ready..."
  
  # Configure max retries and delay
  local max_retries=30
  local retry_count=0
  local retry_delay=3
  
  # Skip direct connection test and go straight to Prisma
  echo "Trying Prisma connection..."
  
  until npx prisma migrate status > /dev/null 2>&1; do
    retry_count=$((retry_count+1))
    
    if [ $retry_count -ge $max_retries ]; then
      echo "Error: Maximum retry attempts ($max_retries) reached. Prisma can't connect to the database."
      echo "Database connection URL: ${DATABASE_URL//:*:*@/:***@}"  # Mask password
      echo "Troubleshooting:"
      echo "1. Check if DB container is running: docker ps | grep postgres"
      echo "2. Check if the DATABASE_URL environment variable is correct"
      echo "3. Check network connectivity between containers"
      exit 1
    fi
    
    echo "Prisma can't connect yet - sleeping for ${retry_delay}s (attempt $retry_count/$max_retries)"
    sleep $retry_delay
  done
  
  echo "Database is up and Prisma can connect - continuing"
}

# Print important environment info for debugging
debug_info() {
  echo "===== Environment Debug Info ====="
  echo "DATABASE_URL: ${DATABASE_URL//:*:*@/:***@}"  # Mask password
  echo "Current directory: $(pwd)"
  echo "Contents of current directory: $(ls -la)"
  echo "Environment variables:"
  env | grep -v PASSWORD | sort
  echo "Network info:"
  getent hosts db || echo "Cannot resolve DB host"
  echo "=================================="
}

# Apply database migrations
apply_migrations() {
  echo "Applying database migrations..."
  # First check if prisma directory exists
  if [ ! -d "prisma" ]; then
    echo "Prisma directory not found in $(pwd)"
    echo "Contents of current directory: $(ls -la)"
    echo "Trying to find prisma directory..."
    find / -name "schema.prisma" -type f 2>/dev/null || echo "No schema.prisma found"
  fi
  
  npx prisma migrate deploy
  echo "Migrations applied successfully!"
}

# Generate Prisma client if needed
generate_client() {
  echo "Generating Prisma client..."
  npx prisma generate
  echo "Prisma client generated successfully!"
}

# Main execution
echo "Starting entrypoint script..."

# Print debug info
debug_info

# Wait for database to be ready
wait_for_db

# Apply migrations
apply_migrations

# Generate client
generate_client

# Execute the main command
echo "Starting application..."
exec "$@" 