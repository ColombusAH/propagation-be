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
# Default value (ensure scheme and port)
FINAL_BACKEND_URL="http://backend:8002"
RAW_BACKEND_URL=""

# Check BACKEND_URL env var
if [ -n "$BACKEND_URL" ]; then
    RAW_BACKEND_URL="$BACKEND_URL"
    echo "Using BACKEND_URL from environment: $RAW_BACKEND_URL"
# Check Railway service name
elif [ "$RAILWAY_PRIVATE_NETWORK" == "true" ] && [ -n "$RAILWAY_SERVICE_BACKEND" ]; then
    # Railway service name usually doesn't include port
    RAW_BACKEND_URL="${RAILWAY_SERVICE_BACKEND}"
    echo "Using Railway service name: $RAW_BACKEND_URL"
fi

# If we have a raw URL/hostname, process it
if [ -n "$RAW_BACKEND_URL" ]; then
    TEMP_URL="$RAW_BACKEND_URL"
    
    # 1. Ensure Port (add :8002 if no port specified)
    # Check if the raw value contains a colon after the first character (indicating a port)
    if [[ ! "$TEMP_URL" =~ .*:[0-9]+$ ]]; then
        TEMP_URL="${TEMP_URL}:8002"
        echo "Appended default port :8002 -> $TEMP_URL"
    else
        echo "Port seems to be present in raw URL: $TEMP_URL"
    fi

    # 2. Ensure Scheme (add http:// if no scheme specified)
    if [[ "$TEMP_URL" != http://* ]] && [[ "$TEMP_URL" != https://* ]]; then
        FINAL_BACKEND_URL="http://$TEMP_URL"
        echo "Prepended http:// scheme: $FINAL_BACKEND_URL"
    else
        FINAL_BACKEND_URL="$TEMP_URL"
        echo "Scheme already present: $FINAL_BACKEND_URL"
    fi
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