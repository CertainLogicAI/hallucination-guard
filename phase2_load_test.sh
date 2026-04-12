#!/bin/bash
#!/bin/bash
#!/bin/bash
#!/bin/bash
# Phase 2 Load Test with LLM Integration
# Simulates 1,000 log entries using OpenAI GPT-3.5-turbo
# Tracks latency, cost, hallucination rate, and validates via hallucination guard.
# Saves metrics to phase2_test/ directory.

set -euo pipefail

# Config
TOTAL_LOGS=1000
COMPLIANCE_TOPICS="/data/.openclaw/workspace/compliance_topics.txt"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "ERROR: OPENAI_API_KEY is not set" >&2
    exit 1
fi

VALIDATE_GUARD="/data/.openclaw/workspace/validate_llm_output.sh"
LOG_DIR="/data/.openclaw/workspace/conversation_logs"
METRICS_DIR="/data/.openclaw/workspace/phase2_test"
METRICS_FILE="${METRICS_DIR}/metrics.json"
LOG_DIR="${conversation_logs}"
mkdir -p "$METRICS_DIR"
echo "{\"total_logs\":0,\"hallucination_rate\":0,\"total_cost\":0,\"llm_calls\":0}" > "$METRICS_FILE"

# Function to calculate cost (USD) based on token count
calculate_cost() {
    local tokens=$1
    echo "scale=6; $tokens * 0.002 / 1000" | bc -l
}

# Function to select random compliance topic
get_random_topic() {
    shuf -n 1 "$COMPLIANCE_TOPICS"
}

# Initialize counters
LOG_CREATED=0
HALLUCINATION_COUNT=0
TOTAL_COST=0
LLM_CALLS=0

# Main loop
for ((i=1; i<=TOTAL_LOGS; i++)); do
    MSG_ID=$((9500 + i))
    PROMPT=$(shuf -n 1 "$COMPLIANCE_TOPICS")
    
    # Record start time
    START=$(date +%s.%N)
    
    # Call OpenAI API (simulate LLM response)
    RESPONSE=$(curl -s -X POST https://api.openai.com/v1/chat/completions \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"gpt-3.5-turbo\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}],
            \"max_tokens\": 150
        }")
    
    # Extract token count and calculate cost
    TOKEN_COUNT=$(echo "$RESPONSE" | jq -r '.usage.total_tokens' 2>/dev/null || echo 0)
    COST=$(calculate_cost $TOKEN_COUNT)
    END=$(date +%s.%N)
    LATENCY=$(echo "$END - $START" | bc -l)
    
    # Validate via hallucination guard
    if $VALIDATE_GUARD "compliance" "$RESPONSE"; then
        # Write log entry
        ./log_conversation.sh $MSG_ID "LLM Compliance" "compliance" "llm,test" "$RESPONSE"
        ((LOG_CREATED++))
    else
        ((HALLUCINATION_COUNT++))
        echo "Hallucination detected for msg_id $MSG_ID" >> "${METRICS_DIR}/hallucinations.log"
    fi
    
    # Record metrics
    END=$(date +%s.%N)
    LATENCY_SEC=$(echo "$END - $START" | bc -l)
    COST=$(calculate_cost $TOKEN_COUNT)
    TOTAL_COST=$(echo "$TOTAL_COST + $COST" | bc -l)
    
    # Save LLM response and metrics
    echo "$RESPONSE" > "${METRICS_DIR}/llm_output/${MSG_ID}.json"
    echo "{\"msg_id\":$MSG_ID,\"latency_seconds\":$LATENCY_SEC,\"token_count\":$TOKEN_COUNT,\"cost_usd\":$COST,\"timestamp\":\"$(date +%Y-%m-%dT%H:%M:%S%z)\"}" >> "${METRICS_DIR}/metrics_log.json"
    
    # Update metrics file
    TOKEN_COUNT=$(echo "$RESPONSE" | jq -r '.usage.total_tokens' 2>/dev/null || echo 0)
    UPDATE_COST=$(calculate_cost $TOKEN_COUNT)
    TOTAL_COST=$(echo "$TOTAL_COST + $UPDATE_COST" | bc -l)
    
    # Update JSON metrics (simple append of new entry)
    jq ".total_logs++ | .hallucination_rate=(($HALLUCINATION_COUNT/$TOTAL_LOGS*100)|scale=2) | .total_cost+=$UPDATE_COST" "$METRICS_FILE" > /tmp/metrics_tmp.json && mv /tmp/metrics_tmp.json "$METRICS_FILE"
    
    # Rate limiting (approx 42 logs/min => 1.4s per log)
    sleep 1.5
done
    
# Post-test: run integrity scan
if [[ -x /data/.openclaw/workspace/integrity_scan.sh ]]; then
    /data/.openclaw/workspace/integrity_scan.sh
fi
    
# Final summary
echo "=== PHASE 2 TEST SUMMARY ===" >> "${METRICS_DIR}/summary.log"
echo "Total Logs Created: $LOG_CREATED" >> "${METRICS_DIR}/summary.log"
echo "Hallucination Rate: $(echo "scale=2; $HALLUCINATION_COUNT / $TOTAL_LOGS * 100" | bc -l)%" >> "${METRICS_DIR}/summary.log"
echo "Total Cost (USD): $TOTAL_COST" >> "${METRICS_DIR}/summary.log"
echo "LLM Calls Made: $((LOG_CREATED + HALLUCINATION_COUNT))" >> "${METRICS_DIR}/summary.log"
echo "Finished at $(date)" >> "${METRICS_DIR}/summary.log"