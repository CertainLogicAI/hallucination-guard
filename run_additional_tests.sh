#!/bin/bash
set -e

echo "Running additional queries to populate routing logs and cache data..."

# Run 20 diverse queries to trigger different routing scenarios
QUERIES=(
  "Explain quantum entanglement"
  "What is the capital of France?"
  "How does a Kalman filter work?"
  "Write a Python function to reverse a linked list"
  "What are the side effects of metformin?"
  "Summarize the plot of Inception"
  "How to configure nginx as a reverse proxy?"
  "What is the French word for 'library'?"
  "Explain the Monty Hall problem"
  "List the Seven Deadly Sins"
  "What is 2+2?"
  "How to center a div in CSS?"
  "Explain TCP three-way handshake"
  "Write a SQL query to find duplicates"
  "What is the speed of light?"
  "How does backpropagation work?"
  "What is the capital of Japan?"
  "Describe the water cycle"
  "How to create a React component?"
  "What is the Pythagorean theorem?"
)

# Run each query twice to test cache
for QUERY in "${QUERIES[@]}"; do
  echo "Query: $QUERY"
  ./deterministic_ai_layer.sh "$QUERY" > /dev/null 2>&1
  ./deterministic_ai_layer.sh "$QUERY" > /dev/null 2>&1
done

echo "20 queries executed. Check action-tracker logs for routing decisions."

