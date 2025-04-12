#!/bin/bash
set -e

# Print network configuration for debugging
echo "Network configuration:"
ip addr
echo "---"

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