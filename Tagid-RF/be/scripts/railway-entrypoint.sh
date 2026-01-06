#!/bin/bash
# DEPRECATED: Node.js version of the entrypoint script
# This project now uses Python-only implementation
# Please use railway-entrypoint-python.sh instead

echo "Warning: This Node.js entrypoint script is deprecated!"
echo "Please use railway-entrypoint-python.sh instead."
echo "Redirecting to Python entrypoint..."

# Pass all arguments to the Python entrypoint script
exec "$(dirname "$0")/railway-entrypoint-python.sh" "$@" 