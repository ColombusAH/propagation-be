#!/bin/bash
set -e

# Print network configuration for debugging
echo "Network configuration:"
ip addr
echo "---"

# Set default backend URL if not provided
if [ -z "$BACKEND_URL" ]; then
  # Get IPv6 address of the backend from the railway.internal DNS
  echo "Resolving anybotbe.railway.internal..."
  IPV6_ADDRESS=$(getent hosts anybotbe.railway.internal | awk '{print $1}' || echo "")
  
  if [ -n "$IPV6_ADDRESS" ]; then
    echo "Resolved anybotbe.railway.internal to: $IPV6_ADDRESS"
    # Add the resolved address to our attempts
    RESOLVED_URL="http://[$IPV6_ADDRESS]:8002"
    echo "Will try resolved URL: $RESOLVED_URL"
  else
    echo "Could not resolve anybotbe.railway.internal"
  fi
  
  # Try different possible backend URLs
  echo "Testing backend connectivity..."
  
  # Define possible backend URLs to try based on Railway's private networking
  BACKENDS=(
    # Try the resolved address first if available
    "$RESOLVED_URL"
    "http://anybotbe:8002"                           # Short service name
    "http://anybotbe.railway.internal:8002"          # Railway internal DNS (full name)
  )
  
  # Remove empty entries (in case resolution failed)
  BACKENDS=( "${BACKENDS[@]/#$/}" )
  
  for url in "${BACKENDS[@]}"; do
    # Skip empty URLs
    if [ -z "$url" ]; then
      continue
    fi
    
    echo "Trying backend at: $url"
    # Try both health endpoints with longer timeout
    if curl -s -f -m 5 -g "$url/" &>/dev/null; then
      echo "Successfully connected to backend at: $url/"
      export BACKEND_URL="$url"
      break
    elif curl -s -f -m 5 -g "$url/health" &>/dev/null; then
      echo "Successfully connected to backend at: $url/health"
      export BACKEND_URL="$url"
      break
    elif curl -s -f -m 5 -g "$url/healthz" &>/dev/null; then
      echo "Successfully connected to backend at: $url/healthz"
      export BACKEND_URL="$url"
      break
    fi
  done
  
  # If no backend worked, check Railway's service variables
  if [ -z "$BACKEND_URL" ] && [ -n "$RAILWAY_SERVICE_ANYBOTBE_INTERNAL_URL" ]; then
    echo "Using Railway service variable: $RAILWAY_SERVICE_ANYBOTBE_INTERNAL_URL"
    export BACKEND_URL="$RAILWAY_SERVICE_ANYBOTBE_INTERNAL_URL"
  elif [ -z "$BACKEND_URL" ]; then
    # If all fails, use the resolved address if available, otherwise a default
    if [ -n "$RESOLVED_URL" ]; then
      echo "Using resolved URL as fallback: $RESOLVED_URL"
      export BACKEND_URL="$RESOLVED_URL"
    elif [ -n "$API_URL" ]; then
      echo "Using API_URL: $API_URL"
      export BACKEND_URL="$API_URL"
    else
      echo "Warning: Could not connect to any backend, defaulting to anybotbe:8002"
      export BACKEND_URL="http://anybotbe:8002"
    fi
  fi
fi

echo "Using BACKEND_URL: $BACKEND_URL"

# Configure nginx to use the PORT environment variable
PORT="${PORT:-80}"
echo "Using PORT: $PORT"

# Update the port in the nginx.conf file
sed -i "s/listen 80 default_server;/listen ${PORT} default_server;/" /etc/nginx/nginx.conf
sed -i "s/listen \[::\]:80 default_server/listen \[::\]:${PORT} default_server/" /etc/nginx/nginx.conf

# Ensure healthcheck path exists and is populated
mkdir -p /usr/share/nginx/html/healthz
echo "ok" > /usr/share/nginx/html/healthz/index.html
chmod 644 /usr/share/nginx/html/healthz/index.html
echo "Healthcheck path created at /usr/share/nginx/html/healthz/index.html"

# Start nginx
echo "Starting nginx..."
exec "$@"