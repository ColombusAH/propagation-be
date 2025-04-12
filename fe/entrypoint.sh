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

# Update the listen port dynamically
PORT="${PORT:-8080}"
echo "Using PORT: $PORT"
sed -i "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"