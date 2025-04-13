#!/bin/bash
set -e

# Configure uvicorn to listen on both IPv4 and IPv6
# The 0.0.0.0 host makes it listen on all IPv4 interfaces
# --workers 2 can be adjusted based on your needs

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 