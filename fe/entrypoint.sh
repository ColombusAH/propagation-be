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

    # Start the networking service
    /etc/init.d/networking restart || true
    
    # Print network configuration for debugging
    echo "Network configuration:"
    ip addr
    echo "---"
fi

# Replace any environment variables in nginx.conf if needed
# envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Configure nginx to use the PORT environment variable
PORT="${PORT:-80}"
echo "Using PORT: $PORT"

# Update the port in the nginx.conf file - more efficient search and replace
sed -i "s/listen 80 default_server;/listen ${PORT} default_server;/" /etc/nginx/nginx.conf
sed -i "s/listen \[::\]:80 default_server/listen \[::\]:${PORT} default_server/" /etc/nginx/nginx.conf

# Create a healthcheck file to respond quickly - redundant but ensures it exists
echo "ok" > /usr/share/nginx/html/healthz/index.html

# Start nginx with less verbosity
exec "$@"