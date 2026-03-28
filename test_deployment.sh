#!/bin/bash

# Deployment Test Script
# This script simulates the automated checks that will be run on your submission

echo "=========================================="
echo "OpenEnv Deployment Test"
echo "=========================================="

# Start server in background
echo ""
echo "Starting server..."
cd "$(dirname "$0")"
./venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 7860 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "✗ FAIL: Server failed to start"
    exit 1
fi

echo "✓ Server started (PID: $SERVER_PID)"
echo ""

# Test endpoints
BASE_URL="http://localhost:7860"

echo "=========================================="
echo "Running Automated Checks"
echo "=========================================="

# Test 1: Root endpoint
echo ""
echo "Test 1: GET / (root endpoint)"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Root endpoint returns 200"
else
    echo "✗ FAIL: Root endpoint returned $HTTP_CODE"
    echo "Response: $BODY"
fi

# Test 2: Health check
echo ""
echo "Test 2: GET /health"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Health check returns 200"
else
    echo "✗ FAIL: Health check returned $HTTP_CODE"
    echo "Response: $BODY"
fi

# Test 3: Reset with empty body (THIS IS THE CRITICAL TEST)
echo ""
echo "Test 3: POST /reset with empty body"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/reset" -H "Content-Type: application/json" -d '{}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Reset with empty body returns 200"
    echo "Response preview: ${BODY:0:100}..."
else
    echo "✗ FAIL: Reset with empty body returned $HTTP_CODE"
    echo "Response: $BODY"
fi

# Test 4: Reset with task_id
echo ""
echo "Test 4: POST /reset with task_id='medium'"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/reset" -H "Content-Type: application/json" -d '{"task_id":"medium"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Reset with task_id returns 200"
else
    echo "✗ FAIL: Reset with task_id returned $HTTP_CODE"
    echo "Response: $BODY"
fi

# Test 5: GET /tasks
echo ""
echo "Test 5: GET /tasks"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/tasks")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Tasks endpoint returns 200"
else
    echo "✗ FAIL: Tasks endpoint returned $HTTP_CODE"
fi

# Test 6: POST /step with action
echo ""
echo "Test 6: POST /step with action"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/step" -H "Content-Type: application/json" -d '{"action":{"action_type":"classify","category":"general_inquiry","reasoning":"test"}}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Step endpoint returns 200"
else
    echo "✗ FAIL: Step endpoint returned $HTTP_CODE"
    echo "Response: $BODY"
fi

# Cleanup
echo ""
echo "=========================================="
echo "Cleanup"
echo "=========================================="
echo "Stopping server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "If all tests passed, your environment is ready for submission!"
echo ""
