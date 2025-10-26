#!/bin/bash
#
# Legal Advisory System v5.0 - API Usage Examples
# Demonstrates how to interact with the REST API using curl
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
API_URL="${API_URL:-http://localhost:8000}"

echo "================================================================================"
echo "  Legal Advisory System v5.0 - API Examples"
echo "================================================================================"
echo ""
echo "API URL: $API_URL"
echo ""

# Example 1: Health Check
echo -e "${BLUE}Example 1: Health Check${NC}"
echo "GET /health"
echo ""
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Example 2: Create Session
echo -e "${BLUE}Example 2: Create Session${NC}"
echo "POST /sessions"
echo ""
SESSION_RESPONSE=$(curl -s -X POST "$API_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "example_user_123"}')

echo "$SESSION_RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo ""
echo -e "${GREEN}Session ID: $SESSION_ID${NC}"
echo ""
echo ""

# Example 3: Send Message - Simple Query
echo -e "${BLUE}Example 3: Send Message - Simple Query${NC}"
echo "POST /messages"
echo ""
curl -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"I need costs for a High Court default judgment for \\$50,000 liquidated claim\"
  }" | python3 -m json.tool
echo ""
echo ""

# Example 4: Get Session
echo -e "${BLUE}Example 4: Get Session${NC}"
echo "GET /sessions/{session_id}"
echo ""
curl -s "$API_URL/sessions/$SESSION_ID" | python3 -m json.tool
echo ""
echo ""

# Example 5: List Available Modules
echo -e "${BLUE}Example 5: List Available Modules${NC}"
echo "GET /modules"
echo ""
curl -s "$API_URL/modules" | python3 -m json.tool
echo ""
echo ""

# Example 6: Get Statistics
echo -e "${BLUE}Example 6: Get Statistics${NC}"
echo "GET /statistics"
echo ""
curl -s "$API_URL/statistics" | python3 -m json.tool
echo ""
echo ""

# Example 7: Conversational Flow
echo -e "${BLUE}Example 7: Conversational Flow (Multi-turn)${NC}"
echo "Creating new session for conversational demo..."
echo ""

CONV_SESSION=$(curl -s -X POST "$API_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "conversation_demo"}')

CONV_SESSION_ID=$(echo "$CONV_SESSION" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo -e "${GREEN}Session ID: $CONV_SESSION_ID${NC}"
echo ""

echo "Message 1: 'I need help with legal costs'"
curl -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$CONV_SESSION_ID\",
    \"message\": \"I need help with legal costs\"
  }" | python3 -m json.tool
echo ""
echo ""

echo "Message 2: 'It's for a default judgment'"
curl -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$CONV_SESSION_ID\",
    \"message\": \"It's for a default judgment\"
  }" | python3 -m json.tool
echo ""
echo ""

echo "Message 3: 'High Court, \\$75,000 liquidated'"
curl -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$CONV_SESSION_ID\",
    \"message\": \"High Court, \\$75,000 liquidated\"
  }" | python3 -m json.tool
echo ""
echo ""

echo "================================================================================"
echo "  API Examples Complete!"
echo "================================================================================"
echo ""
echo "You can now use these patterns to interact with the Legal Advisory System API."
echo ""
