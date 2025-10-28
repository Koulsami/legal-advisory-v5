#!/bin/bash
# Quick test to verify MCP server can run standalone

echo "========================================"
echo "Testing MCP Server Standalone"
echo "========================================"
echo ""

# Check Python
echo "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi
python3 --version
echo ""

# Check dependencies
echo "[2/4] Checking dependencies..."
python3 -c "import mcp; print('  ✓ mcp installed')" 2>/dev/null || echo "  ✗ mcp NOT installed"
python3 -c "import fastmcp; print('  ✓ fastmcp installed')" 2>/dev/null || echo "  ✗ fastmcp NOT installed"
python3 -c "import fastapi; print('  ✓ fastapi installed')" 2>/dev/null || echo "  ✗ fastapi NOT installed"
echo ""

# Check project structure
echo "[3/4] Checking project structure..."
if [ -f "backend/mcp/servers/legal_mcp_server.py" ]; then
    echo "  ✓ MCP server file found"
else
    echo "  ✗ MCP server file NOT found"
    echo "    Expected: backend/mcp/servers/legal_mcp_server.py"
    exit 1
fi
echo ""

# Try to import server
echo "[4/4] Testing server import..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
python3 -c "from backend.mcp.servers.legal_mcp_server import mcp; print('  ✓ Server imports successfully')" 2>&1 | head -5

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ MCP Server is ready!"
    echo "========================================"
    echo ""
    echo "You can now:"
    echo "1. Test with Claude Desktop (see CLAUDE_DESKTOP_SETUP.md)"
    echo "2. Test with MCP Inspector:"
    echo "   npx @modelcontextprotocol/inspector python3 -m backend.mcp.servers.legal_mcp_server"
    echo "3. Run full tests:"
    echo "   python3 test_mcp_server.py"
    echo ""
else
    echo ""
    echo "========================================"
    echo "✗ Server import failed"
    echo "========================================"
    echo ""
    echo "Please check error messages above and:"
    echo "1. Install dependencies: pip install -r requirements.txt"
    echo "2. Check PYTHONPATH is set correctly"
    echo "3. Verify all files are present"
    echo ""
    exit 1
fi
