#!/bin/bash
set -e

# Print environment info for debugging
echo "Environment:"
echo "PORT: $PORT"
echo "RAILWAY_PRIVATE_NETWORK: $RAILWAY_PRIVATE_NETWORK"

# Try to resolve backend service name
echo "Attempting to resolve backend service..."
getent hosts backend || echo "Could not resolve 'backend' service"

# If BACKEND_URL is not set and we're on Railway, try to determine it
if [ -z "$BACKEND_URL" ] && [ "$RAILWAY_PRIVATE_NETWORK" == "true" ]; then
    # Find the service name from Railway environment
    if [ -n "$RAILWAY_SERVICE_BACKEND" ]; then
        export BACKEND_URL="http://${RAILWAY_SERVICE_BACKEND}:8002"
        echo "Setting BACKEND_URL to $BACKEND_URL based on Railway service name"
    else
        echo "Warning: BACKEND_URL not set and could not detect backend service name"
        # Use the default in nginx.conf
    fi
fi

# Make sure the BACKEND_URL is available in the Nginx runtime
if [ -n "$BACKEND_URL" ]; then
    # Write environment variable to /etc/nginx/conf.d/environment.conf
    echo "env BACKEND_URL=$BACKEND_URL;" > /etc/nginx/conf.d/environment.conf
    echo "Exported BACKEND_URL to Nginx environment: $BACKEND_URL"
fi

# Configure to listen on the PORT environment variable
if [ -n "$PORT" ]; then
    # Use specific pattern matching to ensure we only replace the port numbers
    sed -i.bak "s|listen 80 |listen $PORT |g" /etc/nginx/nginx.conf
    sed -i.bak "s|listen \[::\]:80 |listen \[::\]:$PORT |g" /etc/nginx/nginx.conf
    echo "Configured nginx to listen on port $PORT"
fi

# Execute the CMD
exec "$@"