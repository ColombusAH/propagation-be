#!/bin/sh
# entrypoint.sh

# Update the listen port dynamically
PORT="${PORT:-8080}"
echo "Using PORT: $PORT"
sed -i "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"