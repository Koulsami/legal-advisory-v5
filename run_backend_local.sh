#!/bin/bash
# Start the backend API server locally for testing

echo "=========================================="
echo "Legal Advisory System - Local Backend"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/api/routes.py" ]; then
    echo "❌ Error: Please run this from the legal-advisory-v5 directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Set environment variables for local development
export PYTHONPATH=$(pwd)
export LOG_LEVEL=INFO
export LOG_COLORS=false

# Check if Anthropic API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set - running in MOCK mode"
    echo "   (Set it with: export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx)"
else
    echo "✅ ANTHROPIC_API_KEY is set"
fi

echo ""
echo "🚀 Starting backend server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/health"
echo ""
echo "📄 Open test_frontend.html in your browser to test!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Start the server
uvicorn backend.api.routes:app --host 0.0.0.0 --port 8000 --reload
