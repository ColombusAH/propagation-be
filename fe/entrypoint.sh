#!/bin/bash
set -e

# Enable IPv6 private networking for Alpine in Railway
if [ "$ENABLE_ALPINE_PRIVATE_NETWORKING" = "true" ]; then
    echo "Enabling Alpine private networking for Railway.app..."
    # Create directory for IPv6 configuration if it doesn't exist
    mkdir -p /etc/network
    
    # Configure IPv6 networking
    cat > /etc/network/interfaces << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
    pre-up modprobe ipv6
    pre-up sysctl -w net.ipv6.conf.all.disable_ipv6=0
EOF

    # Try to set loopback interface up, but don't fail if we don't have permission
    # The interface is likely already up anyway in a managed container environment
    ip link set dev lo up 2>/dev/null || echo "Note: Could not set loopback interface up (permission issue) - this is usually OK"
    
    # Print network configuration for debugging
    echo "Network configuration:"
    ip addr
    echo "---"
fi

# Make environment variables available to nginx
if [ -n "$BACKEND_URL" ]; then
    echo "Setting BACKEND_URL to: $BACKEND_URL"
    export ENV_BACKEND_URL="$BACKEND_URL"
fi

# Configure nginx to use the PORT environment variable
PORT="${PORT:-80}"
echo "Using PORT: $PORT"

# Update the port in the nginx.conf file - more efficient search and replace
sed -i "s/listen 80 default_server;/listen ${PORT} default_server;/" /etc/nginx/nginx.conf
sed -i "s/listen \[::\]:80 default_server/listen \[::\]:${PORT} default_server/" /etc/nginx/nginx.conf

# Ensure healthcheck path exists and is populated
mkdir -p /usr/share/nginx/html/healthz
echo "ok" > /usr/share/nginx/html/healthz/index.html
chmod 644 /usr/share/nginx/html/healthz/index.html
echo "Healthcheck path created at /usr/share/nginx/html/healthz/index.html"

# Start nginx with less verbosity
exec "$@"