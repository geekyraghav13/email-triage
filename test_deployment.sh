#!/bin/bash

# ========================================================================
# DEPLOYMENT TEST SCRIPT
# Tests all endpoints on deployed HuggingFace Space
# ========================================================================

BASE_URL="https://geekyraghav13-openenv-email-triage.hf.space"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     🧪 TESTING EMAIL TRIAGE OPENENV DEPLOYMENT                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Space URL: https://huggingface.co/spaces/geekyraghav13/openenv-email-triage"
echo "API URL:   $BASE_URL"
echo ""

# ========================================================================
# Test 1: Health Check
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 1: Health Check"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "GET $BASE_URL/health"
echo ""

HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)

if [ "$HEALTH" = "200" ]; then
    echo "✅ PASS - Health check returned 200"
    curl -s $BASE_URL/health | python3 -m json.tool
else
    echo "❌ FAIL - Health check returned $HEALTH (expected 200)"
    echo "   Space may still be building. Wait 1-2 minutes and try again."
fi

echo ""
sleep 2

# ========================================================================
# Test 2: Root Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 2: Root Endpoint (Metadata)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "GET $BASE_URL/"
echo ""

ROOT=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/)

if [ "$ROOT" = "200" ]; then
    echo "✅ PASS - Root endpoint returned 200"
    curl -s $BASE_URL/ | python3 -m json.tool | head -20
else
    echo "❌ FAIL - Root endpoint returned $ROOT"
fi

echo ""
sleep 2

# ========================================================================
# Test 3: Tasks Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 3: Tasks Endpoint"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "GET $BASE_URL/tasks"
echo ""

TASKS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/tasks)

if [ "$TASKS" = "200" ]; then
    echo "✅ PASS - Tasks endpoint returned 200"
    curl -s $BASE_URL/tasks | python3 -m json.tool | head -25
else
    echo "❌ FAIL - Tasks endpoint returned $TASKS"
fi

echo ""
sleep 2

# ========================================================================
# Test 4: Reset Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 4: Reset Endpoint (Easy Task)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "POST $BASE_URL/reset"
echo '{"task_id": "easy"}'
echo ""

RESET=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/reset \
    -H "Content-Type: application/json" \
    -d '{"task_id": "easy"}')

if [ "$RESET" = "200" ]; then
    echo "✅ PASS - Reset endpoint returned 200"
    curl -s -X POST $BASE_URL/reset \
        -H "Content-Type: application/json" \
        -d '{"task_id": "easy"}' | python3 -m json.tool | head -25
else
    echo "❌ FAIL - Reset endpoint returned $RESET"
fi

echo ""
sleep 2

# ========================================================================
# Test 5: Step Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 5: Step Endpoint (Classification Action)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "POST $BASE_URL/step"
echo '{"action": {"action_type": "classify", "category": "bug_report"}}'
echo ""

STEP=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/step \
    -H "Content-Type: application/json" \
    -d '{"action": {"action_type": "classify", "category": "bug_report", "reasoning": "Test classification"}}')

if [ "$STEP" = "200" ]; then
    echo "✅ PASS - Step endpoint returned 200"
    curl -s -X POST $BASE_URL/step \
        -H "Content-Type: application/json" \
        -d '{"action": {"action_type": "classify", "category": "bug_report", "reasoning": "Test"}}' \
        | python3 -m json.tool | head -30
else
    echo "❌ FAIL - Step endpoint returned $STEP"
fi

echo ""
sleep 2

# ========================================================================
# Test 6: State Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 6: State Endpoint"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "GET $BASE_URL/state"
echo ""

STATE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/state)

if [ "$STATE" = "200" ]; then
    echo "✅ PASS - State endpoint returned 200"
    curl -s $BASE_URL/state | python3 -m json.tool | head -20
else
    echo "❌ FAIL - State endpoint returned $STATE"
fi

echo ""
sleep 2

# ========================================================================
# Test 7: Baseline Endpoint
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "Test 7: Baseline Info Endpoint"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "GET $BASE_URL/baseline"
echo ""

BASELINE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/baseline)

if [ "$BASELINE" = "200" ]; then
    echo "✅ PASS - Baseline endpoint returned 200"
    curl -s $BASE_URL/baseline | python3 -m json.tool
else
    echo "❌ FAIL - Baseline endpoint returned $BASELINE"
fi

echo ""
sleep 2

# ========================================================================
# Summary
# ========================================================================

echo "════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

TOTAL=7
PASSED=0

[ "$HEALTH" = "200" ] && ((PASSED++))
[ "$ROOT" = "200" ] && ((PASSED++))
[ "$TASKS" = "200" ] && ((PASSED++))
[ "$RESET" = "200" ] && ((PASSED++))
[ "$STEP" = "200" ] && ((PASSED++))
[ "$STATE" = "200" ] && ((PASSED++))
[ "$BASELINE" = "200" ] && ((PASSED++))

echo "Tests Passed: $PASSED/$TOTAL"
echo ""

if [ "$PASSED" = "$TOTAL" ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "Your deployment is working perfectly!"
    echo ""
    echo "Next steps:"
    echo "  1. ✅ Add 'openenv' tag in Space settings"
    echo "  2. ✅ Submit your Space URL:"
    echo "     https://huggingface.co/spaces/geekyraghav13/openenv-email-triage"
    echo ""
else
    echo "⚠️  Some tests failed."
    echo ""
    echo "Common issues:"
    echo "  - Space still building (wait 5 minutes)"
    echo "  - Check build logs in Space"
    echo "  - Verify Dockerfile and requirements.txt"
    echo ""
fi

echo "════════════════════════════════════════════════════════════════"
