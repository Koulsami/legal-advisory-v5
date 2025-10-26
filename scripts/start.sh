#!/bin/bash
#
# Legal Advisory System v5.0 - Start Script
# Starts the API server using Gunicorn
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Legal Advisory System v5.0${NC}"
echo -e "${BLUE}  Starting API Server...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn..."
    pip install gunicorn
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Get configuration
WORKERS=${WORKERS:-4}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}

echo -e "${GREEN}✓ Configuration:${NC}"
echo "  Workers: $WORKERS"
echo "  Port: $PORT"
echo "  Log Level: $LOG_LEVEL"
echo ""

# Start server
echo -e "${GREEN}✓ Starting server...${NC}"
echo ""

gunicorn backend.api.routes:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level $LOG_LEVEL
