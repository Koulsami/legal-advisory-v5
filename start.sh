#!/bin/bash
# Legal Advisory System - Railway Startup Script

set -e

echo "========================================="
echo "Legal Advisory System v5.0"
echo "Starting application..."
echo "========================================="
echo ""

# Show environment
echo "Environment Configuration:"
echo "  PORT: ${PORT:-8000}"
echo "  PYTHONPATH: ${PYTHONPATH:-/app}"
echo "  PWD: $(pwd)"
echo ""

# List application files
echo "Application Structure:"
ls -la
echo ""

# Check backend exists
if [ ! -d "backend" ]; then
    echo "ERROR: backend directory not found!"
    exit 1
fi

echo "Backend directory found:"
ls -la backend/
echo ""

# Start the application
echo "Starting uvicorn..."
echo "Command: uvicorn backend.api.routes:app --host 0.0.0.0 --port ${PORT:-8000}"
echo ""

exec uvicorn backend.api.routes:app --host 0.0.0.0 --port ${PORT:-8000}
