#!/bin/bash
set -e

# Print network configuration for debugging
echo "Network configuration:"
ip addr
echo "---"

# Set default backend URL if not provided
if [ -z "$BACKEND_URL" ]; then
  # Try different possible backend URLs
  echo "Testing backend connectivity..."
  
  # Define possible backend URLs to try based on Railway's private networking (IPv6)
  BACKENDS=(
    "http://[fd12:22b0:4b1c::]:8002"                  # Default IPv6 format from docs
    "http://anybotbe.railway.internal:8002"          # Railway internal DNS
    "http://[fd12:22b0:4b1c::anybotbe]:8002"         # IPv6 with hostname
  )
  
  for url in "${BACKENDS[@]}"; do
    echo "Trying backend at: $url"
    # Try both health endpoints
    if curl -s -f -m 1 -g "$url/health" &>/dev/null; then
      echo "Successfully connected to backend at: $url/health"
      export BACKEND_URL="$url"
      break
    elif curl -s -f -m 1 -g "$url/healthz" &>/dev/null; then
      echo "Successfully connected to backend at: $url/healthz"
      export BACKEND_URL="$url"
      break
    fi
  done
  
  # If no backend worked, default to the Railway IPv6 address
  if [ -z "$BACKEND_URL" ]; then
    echo "Warning: Could not connect to any backend, defaulting to IPv6 loopback"
    export BACKEND_URL="http://[fd12:22b0:4b1c::]:8002"
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