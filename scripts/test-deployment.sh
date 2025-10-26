#!/bin/bash
#
# Legal Advisory System v5.0 - Deployment Testing Script
# Tests the deployed system to ensure it's working correctly
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

test_passed() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

test_failed() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

test_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Start testing
print_header "Legal Advisory System v5.0 - Deployment Tests"

echo "Testing API at: $API_URL"
echo ""

# Test 1: Health Check
test_info "Test 1: Health Check"
if curl -f -s "$API_URL/health" | grep -q "healthy"; then
    test_passed "Health check endpoint responding"
else
    test_failed "Health check endpoint not responding"
fi

# Test 2: API Documentation
test_info "Test 2: API Documentation"
if curl -f -s "$API_URL/docs" | grep -q "swagger"; then
    test_passed "API documentation accessible"
else
    test_failed "API documentation not accessible"
fi

# Test 3: OpenAPI Schema
test_info "Test 3: OpenAPI Schema"
if curl -f -s "$API_URL/openapi.json" | grep -q "openapi"; then
    test_passed "OpenAPI schema available"
else
    test_failed "OpenAPI schema not available"
fi

# Test 4: Create Session
test_info "Test 4: Create Session"
SESSION_RESPONSE=$(curl -f -s -X POST "$API_URL/sessions" \
    -H "Content-Type: application/json" \
    -d '{"user_id": "test_user"}')

if echo "$SESSION_RESPONSE" | grep -q "session_id"; then
    test_passed "Session creation working"
    SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null || echo "")
else
    test_failed "Session creation failed"
    SESSION_ID=""
fi

# Test 5: Send Message (if session created)
if [ -n "$SESSION_ID" ]; then
    test_info "Test 5: Send Message"
    MESSAGE_RESPONSE=$(curl -f -s -X POST "$API_URL/messages" \
        -H "Content-Type: application/json" \
        -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"Test message\"}")

    if echo "$MESSAGE_RESPONSE" | grep -q "message"; then
        test_passed "Message processing working"
    else
        test_failed "Message processing failed"
    fi
else
    test_info "Test 5: Send Message - Skipped (no session)"
    test_failed "Cannot test message processing without session"
fi

# Test 6: Get Session
if [ -n "$SESSION_ID" ]; then
    test_info "Test 6: Get Session"
    if curl -f -s "$API_URL/sessions/$SESSION_ID" | grep -q "session_id"; then
        test_passed "Session retrieval working"
    else
        test_failed "Session retrieval failed"
    fi
else
    test_info "Test 6: Get Session - Skipped (no session)"
    test_failed "Cannot test session retrieval without session"
fi

# Test 7: List Modules
test_info "Test 7: List Modules"
if curl -f -s "$API_URL/modules" | grep -q "modules"; then
    test_passed "Module listing working"
else
    test_failed "Module listing failed"
fi

# Test 8: Get Statistics
test_info "Test 8: Get Statistics"
if curl -f -s "$API_URL/statistics" | grep -q "total_sessions"; then
    test_passed "Statistics endpoint working"
else
    test_failed "Statistics endpoint failed"
fi

# Test 9: Response Time
test_info "Test 9: Response Time Check"
START_TIME=$(date +%s%N)
curl -f -s "$API_URL/health" > /dev/null
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

if [ $RESPONSE_TIME -lt 1000 ]; then
    test_passed "Response time acceptable (${RESPONSE_TIME}ms)"
else
    test_failed "Response time too slow (${RESPONSE_TIME}ms)"
fi

# Test 10: Security Headers (if nginx is used)
test_info "Test 10: Security Headers"
HEADERS=$(curl -s -I "$API_URL/health")
if echo "$HEADERS" | grep -qi "x-frame-options"; then
    test_passed "Security headers present"
else
    echo -e "${YELLOW}⚠ Security headers not found (may be normal without nginx)${NC}"
    ((TOTAL_TESTS++))
fi

# Summary
print_header "Test Summary"

echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ALL TESTS PASSED! ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "The deployment is working correctly."
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  SOME TESTS FAILED! ✗${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Please check the logs and configuration."
    exit 1
fi
