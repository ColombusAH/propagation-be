#!/bin/bash
set -e

# Print environment info for debugging
echo "Environment:"
echo "PORT: $PORT"
echo "RAILWAY_PRIVATE_NETWORK: $RAILWAY_PRIVATE_NETWORK"

# Try to resolve backend service name
echo "Attempting to resolve backend service..."
getent hosts backend || echo "Could not resolve 'backend' service"

# Determine the Backend URL
# Default value
FINAL_BACKEND_URL="http://backend:8002"

# If BACKEND_URL env var is set and not empty, use it
if [ -n "$BACKEND_URL" ]; then
    FINAL_BACKEND_URL="$BACKEND_URL"
    echo "Using BACKEND_URL from environment: $FINAL_BACKEND_URL"
# Else if on Railway, try to detect service name
elif [ "$RAILWAY_PRIVATE_NETWORK" == "true" ] && [ -n "$RAILWAY_SERVICE_BACKEND" ]; then
    FINAL_BACKEND_URL="http://${RAILWAY_SERVICE_BACKEND}:8002"
    echo "Using Railway service name for backend URL: $FINAL_BACKEND_URL"
else
    echo "Using default backend URL: $FINAL_BACKEND_URL"
fi

# Substitute the placeholder in nginx.conf
# Use a different delimiter for sed to avoid issues with URLs containing slashes
PLACEHOLDER="__BACKEND_PLACEHOLDER__"
echo "Substituting $PLACEHOLDER with $FINAL_BACKEND_URL in /etc/nginx/nginx.conf"
sed -i.bak "s|$PLACEHOLDER|$FINAL_BACKEND_URL|g" /etc/nginx/nginx.conf

# Configure to listen on the PORT environment variable
if [ -n "$PORT" ]; then
    # Use specific pattern matching to ensure we only replace the port numbers
    sed -i.bak "s|listen 80 |listen $PORT |g" /etc/nginx/nginx.conf
    sed -i.bak "s|listen \[::\]:80 |listen \[::\]:$PORT |g" /etc/nginx/nginx.conf
    echo "Configured nginx to listen on port $PORT"
fi

# Execute the CMD
echo "Starting Nginx..."
exec "$@"