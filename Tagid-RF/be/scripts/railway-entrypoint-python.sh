#!/bin/bash
# Enable verbose logging for debugging
set -x

# Set environment variables
export PYTHONHASHSEED=random
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONWARNINGS="ignore::DeprecationWarning"
export PORT=${PORT:-8002}

# Print system info
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
ls -la

# Configure network - check and print networking information for debugging
echo "Network configuration:"
ip addr || true
echo "---"

# Ensure the app directory structure is correct
mkdir -p /app/logs

echo "Generating Prisma client..."
if [ -f "prisma/schema.prisma" ]; then
  python -m prisma generate --schema=prisma/schema.prisma || echo "Prisma generation failed"
elif [ -f "app/prisma/schema.prisma" ]; then
  python -m prisma generate --schema=app/prisma/schema.prisma || echo "Prisma generation failed"
else
  # Fallback
  python -m prisma generate || echo "Prisma generation failed"
fi

# Skip blocking DB checks for now to verify app startup
# if [ -n "$DATABASE_URL" ]; then...

echo "Starting application immediately for debugging..."

# Start the application
echo "Starting application on port $PORT..."
# Bind to 0.0.0.0 explicitly, use python -m for safety, allow proxy headers
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*' 