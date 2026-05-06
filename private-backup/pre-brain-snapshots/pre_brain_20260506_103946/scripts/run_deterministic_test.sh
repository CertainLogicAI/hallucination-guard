#!/bin/bash
# /data/.openclaw/workspace/scripts/run_deterministic_test.sh

set -e

TEST_FILE="/data/.openclaw/workspace/test-queries/2026-03-29-stratified-2000-queries.txt"
SCRIPT_PATH="/data/.openclaw/workspace/scripts/memory-search.js"
OUTPUT_DIR="/data/.openclaw/workspace/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_JSON="${OUTPUT_DIR}/deterministic_test_${TIMESTAMP}.json"
STATS_CSV="${OUTPUT_DIR}/deterministic_stats_${TIMESTAMP}.csv"

echo "Starting deterministic AI test..."
echo "Test file: ${TEST_FILE}"
echo "Results will be saved to: ${RESULTS_JSON}"

# Initialize results tracking
TOTAL_QUERIES=0
HALLUCINATIONS=0
GUARDRAIL_ACTIVATIONS=0
CITATIONS_MISSING=0
TOTAL_TOKENS=0
TOTAL_LATENCY=0
CATEGORY_COUNTS=(0 0 0 0)  # Supported, Partial, Unsupported, Adversarial

# Create results JSON structure
cat > "${RESULTS_JSON}" << EOF
{
  "test_timestamp": "$(date -Iseconds)",
  "total_queries": 0,
  "categories": {
    "supported": 0,
    "partially_supported": 0,
    "unsupported": 0,
    "adversarial": 0
  },
  "metrics": {
    "hallucinations": 0,
    "guardrail_activations": 0,
    "citations_missing": 0,
    "total_tokens": 0,
    "avg_latency_ms": 0,
    "token_efficiency": 0
  },
  "detailed_results": []
}
EOF

# Read queries and run tests
QUERY_NUM=0
while IFS= read -r query || [[ -n "$query" ]]; do
    # Skip comments and empty lines
    [[ "$query" =~ ^# ]] && continue
    [[ -z "$query" ]] && continue
    
    QUERY_NUM=$((QUERY_NUM + 1))
    echo "Running query ${QUERY_NUM}: ${query:0:50}..."
    
    # Determine category based on preceding comment in test file
    # We'll do a simple approach: assume the file is ordered as we created it
    # In practice, we'd want to parse the file properly, but for now we'll use the known distribution
    if [[ $QUERY_NUM -le 800 ]]; then
        CATEGORY="supported"
    elif [[ $QUERY_NUM -le 1400 ]]; then
        CATEGORY="partially_supported"
    elif [[ $QUERY_NUM -le 1800 ]]; then
        CATEGORY="unsupported"
    else
        CATEGORY="adversarial"
    fi
    
    # Measure execution time
    START_MS=$(date +%s%3N)
    
    # Run memory search via node script directly
    RESPONSE=$(node "${SCRIPT_PATH}" "${query}" 2>/dev/null || echo "ERROR: command failed")
    
    END_MS=$(date +%s%3N)
    LATENCY=$((END_MS - START_MS))
    
    # Analyze response for hallucinations vs guardrails
    IS_HALLUCINATION=0
    IS_GUARDRAIL=0
    CITATION_COUNT=0
    
    # Check if response indicates no matches (potential guardrail)
    if [[ "${RESPONSE}" == *"Found 0 results"* ]] || [[ "${RESPONSE}" == *"No matches."* ]]; then
        # For unsupported/adversarial queries, this is expected guardrail
        if [[ "$CATEGORY" != "supported" ]]; then
            IS_GUARDRAIL=1
        else
            IS_HALLUCINATION=1  # supported query should have results
        fi
    elif [[ "${RESPONSE}" == *"Found"* ]]; then
        # Extract snippet lines to check for citations
        CITATION_COUNT=$(echo "${RESPONSE}" | grep -c "\.md:[0-9]*:")
        if [[ $CITATION_COUNT -eq 0 ]]; then
            CITATIONS_MISSING=1
        fi
    fi
    
    # Estimate token count (rough approximation: 4 chars per token)
    TOKENS_ESTIMATED=$(( ${#query} / 4 + ${#RESPONSE} / 4 ))
    
    # Update counters
    TOTAL_QUERIES=$QUERY_NUM
    TOTAL_TOKENS=$((TOTAL_TOKENS + TOKENS_ESTIMATED))
    TOTAL_LATENCY=$((TOTAL_LATENCY + LATENCY))
    
    if [[ $IS_HALLUCINATION -eq 1 ]]; then
        HALLUCINATIONS=$((HALLUCINATIONS + 1))
    fi
    if [[ $IS_GUARDRAIL -eq 1 ]]; then
        GUARDRAIL_ACTIVATIONS=$((GUARDRAIL_ACTIVATIONS + 1))
    fi
    if [[ $CITATIONS_MISSING -eq 1 ]]; then
        CITATIONS_MISSING=$((CITATIONS_MISSING + 1))
    fi
    
    # Append to detailed results (simplified)
    # In a real implementation, we would use jq to properly update JSON
    
done < "${TEST_FILE}"

# Calculate metrics
if [[ $TOTAL_QUERIES -gt 0 ]]; then
    AVG_LATENCY=$((TOTAL_LATENCY / TOTAL_QUERIES))
    AVG_TOKENS=$((TOTAL_TOKENS / TOTAL_QUERIES))
else
    AVG_LATENCY=0
    AVG_TOKENS=0
fi

echo "Test complete!"
echo "Total queries: ${TOTAL_QUERIES}"
echo "Hallucinations: ${HALLUCINATIONS}"
echo "Guardrail activations: ${GUARDRAIL_ACTIVATIONS}"
echo "Citations missing: ${CITATIONS_MISSING}"
echo "Average latency: ${AVG_LATENCY}ms"
echo "Average tokens per query: ${AVG_TOKENS}"

# Generate CSV stats
echo "metric,value" > "${STATS_CSV}"
echo "total_queries,${TOTAL_QUERIES}" >> "${STATS_CSV}"
echo "hallucinations,${HALLUCINATIONS}" >> "${STATS_CSV}"
echo "guardrail_activations,${GUARDRAIL_ACTIVATIONS}" >> "${STATS_CSV}"
echo "citations_missing,${CITATIONS_MISSING}" >> "${STATS_CSV}"
echo "avg_latency_ms,${AVG_LATENCY}" >> "${STATS_CSV}"
echo "avg_tokens_per_query,${AVG_TOKENS}" >> "${STATS_CSV}"

echo "Stats saved to: ${STATS_CSV}"
echo "Results JSON saved to: ${RESULTS_JSON}"