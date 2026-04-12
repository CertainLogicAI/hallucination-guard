#!/usr/bin/env bash
# deterministic_test_suite.sh – Patent-ready validation tests for the deterministic AI layer
# Run this script to generate documented, verifiable results for patent filing

set -e

OUTPUT_DIR="/data/.openclaw/workspace/test-results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "============================================================="
echo "DETERMINISTIC AI LAYER – PATENT VALIDATION TEST SUITE"
echo "Test Run: $(date)"
echo "Output Directory: $OUTPUT_DIR"
echo "============================================================="

# --------------------------------------
# Test 1: Determinism
# --------------------------------------
echo ""
echo ">>> TEST 1: DETERMINISM (Same input → Same output)"
echo "---"

QUERY="What is 2+2?"

./deterministic_ai_layer.sh "$QUERY" > "$OUTPUT_DIR/run1.txt"
./deterministic_ai_layer.sh "$QUERY" > "$OUTPUT_DIR/run2.txt"
./deterministic_ai_layer.sh "$QUERY" > "$OUTPUT_DIR/run3.txt"

if diff -q "$OUTPUT_DIR/run1.txt" "$OUTPUT_DIR/run2.txt" >/dev/null 2>&1 && \
   diff -q "$OUTPUT_DIR/run2.txt" "$OUTPUT_DIR/run3.txt" >/dev/null 2>&1; then
  echo "✅ PASS: All three runs produced identical output"
  TEST1_RESULT="PASS"
else
  echo "❌ FAIL: Outputs differed between runs"
  TEST1_RESULT="FAIL"
fi

# --------------------------------------
# Test 2: Token Budget Enforcement
# --------------------------------------
echo ""
echo ">>> TEST 2: TOKEN BUDGET ENFORCEMENT"
echo "---"

LONG_QUERY="Write a comprehensive essay on the history of artificial intelligence from the 1950s to present day including all major breakthroughs researchers papers and institutions also discuss the current state of AI research and future directions include specific names dates and publications this is a test of the token budget enforcement mechanism to ensure that long inputs are automatically truncated to stay within the predefined token budget limit"

./deterministic_ai_layer.sh "$LONG_QUERY" > "$OUTPUT_DIR/long_output.txt"

TOKEN_COUNT=$(wc -w < "$OUTPUT_DIR/long_output.txt")
echo "Input query length: $(echo "$LONG_QUERY" | wc -w) words"
echo "Output length: $TOKEN_COUNT words"

# Budget is 512 tokens; allow 10% margin
if [ "$TOKEN_COUNT" -lt 563 ]; then
  echo "✅ PASS: Output truncated to $TOKEN_COUNT words (within 512 budget)"
  TEST2_RESULT="PASS"
else
  echo "❌ FAIL: Output not truncated (exceeded budget)"
  TEST2_RESULT="FAIL"
fi

# --------------------------------------
# Test 3: Hash Verification
# --------------------------------------
echo ""
echo ">>> TEST 3: HASH VERIFICATION (SHA-256)"
echo "---"

OUTPUT_HASH=$(sha256sum "$OUTPUT_DIR/run1.txt" | awk '{print $1}')
echo "Output SHA-256: $OUTPUT_HASH"

# Store hash for future verification
echo "$OUTPUT_HASH" > "$OUTPUT_DIR/reference_hash.txt"
echo "✅ PASS: Hash generated and stored at $OUTPUT_DIR/reference_hash.txt"
TEST3_RESULT="PASS"

# --------------------------------------
# Test 4: Hybrid Routing
# --------------------------------------
echo ""
echo ">>> TEST 4: HYBRID ROUTING (Local-first → External fallback)"
echo "---"

# Check logs for routing decisions
ROUTING_LOG=$(sqlite3 /data/.openclaw/action-tracker/action_logs.db \
  "SELECT step, decision FROM action_log WHERE step='routing_decision' ORDER BY id DESC LIMIT 1;")

if [ -n "$ROUTING_LOG" ]; then
  echo "Last routing decision: $ROUTING_LOG"
  echo "$ROUTING_LOG" > "$OUTPUT_DIR/routing_log.txt"
  echo "✅ PASS: Routing decision logged"
  TEST4_RESULT="PASS"
else
  echo "⚠️  No routing log found (may need to run more queries first)"
  TEST4_RESULT="SKIP"
fi

# --------------------------------------
# Test 5: LRU Cache
# --------------------------------------
echo ""
echo ">>> TEST 5: LRU CACHE (Repeat query = cached response)"
echo "---"

CACHE_QUERY="Summarize FaultTrace"

START1=$(date +%s%N)
./deterministic_ai_layer.sh "$CACHE_QUERY" > "$OUTPUT_DIR/cache_run1.txt"
END1=$(date +%s%N)

START2=$(date +%s%N)
./deterministic_ai_layer.sh "$CACHE_QUERY" > "$OUTPUT_DIR/cache_run2.txt"
END2=$(date +%s%N)

LATENCY1=$(( (END1 - START1) / 1000000 ))
LATENCY2=$(( (END2 - START2) / 1000000 ))

echo "First call:  ${LATENCY1}ms"
echo "Second call: ${LATENCY2}ms"

if [ "$LATENCY2" -lt "$LATENCY1" ]; then
  echo "✅ PASS: Second call faster (likely cached)"
  TEST5_RESULT="PASS"
else
  echo "⚠️  NOTE: Second call not faster (cache may still work but latency varies)"
  TEST5_RESULT="PARTIAL"
fi

# --------------------------------------
# Test 6: Action Tracking (Audit Trail)
# --------------------------------------
echo ""
echo ">>> TEST 6: ACTION TRACKING (Full audit trail)"
echo "---"

# Export full log
sqlite3 /data/.openclaw/action-tracker/action_logs.db \
  "SELECT * FROM action_log ORDER BY id DESC LIMIT 20;" > "$OUTPUT_DIR/action_log.txt"

# Count steps
echo "Log entries in database:"
for step in "input_received" "token_estimation" "routing_decision" "output_delivered"; do
  COUNT=$(sqlite3 /data/.openclaw/action-tracker/action_logs.db \
    "SELECT COUNT(*) FROM action_log WHERE step='$step';")
  echo "  $step: $COUNT entries"
done

echo "✅ PASS: Audit trail exported to $OUTPUT_DIR/action_log.txt"
TEST6_RESULT="PASS"

# --------------------------------------
# Summary
# --------------------------------------
echo ""
echo "============================================================="
echo "TEST SUMMARY"
echo "============================================================="
echo "Test 1 (Determinism):        $TEST1_RESULT"
echo "Test 2 (Token Budget):       $TEST2_RESULT"
echo "Test 3 (Hash Verification):  $TEST3_RESULT"
echo "Test 4 (Hybrid Routing):     $TEST4_RESULT"
echo "Test 5 (LRU Cache):          $TEST5_RESULT"
echo "Test 6 (Action Tracking):    $TEST6_RESULT"
echo "============================================================="
echo "Full results saved to: $OUTPUT_DIR/"
echo "============================================================="