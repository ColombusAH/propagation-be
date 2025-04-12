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
  getent hosts anybotbe.railway.internal || echo "Could not resolve anybotbe.railway.internal"
  
  # Try different possible backend URLs
  echo "Testing backend connectivity..."
  
  # Define possible backend URLs to try based on Railway's private networking
  BACKENDS=(
    "http://anybotbe:8002"                           # Short service name
    "http://anybotbe.railway.internal:8002"          # Railway internal DNS (full name)
    "http://10.250.12.29:8002"                       # IPv4 address from backend logs
    "http://[fd12:22b0:4b1c:0:1000:20:ebb5:9659]:8002" # IPv6 address from backend logs
  )
  
  for url in "${BACKENDS[@]}"; do
    echo "Trying backend at: $url"
    # Try both health endpoints
    if curl -s -f -m 2 -g "$url/" &>/dev/null; then
      echo "Successfully connected to backend at: $url/"
      export BACKEND_URL="$url"
      break
    elif curl -s -f -m 2 -g "$url/health" &>/dev/null; then
      echo "Successfully connected to backend at: $url/health"
      export BACKEND_URL="$url"
      break
    elif curl -s -f -m 2 -g "$url/healthz" &>/dev/null; then
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
    # If all fails, default to the API_URL if provided, or a simple default
    if [ -n "$API_URL" ]; then
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