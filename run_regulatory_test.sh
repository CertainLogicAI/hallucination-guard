#!/bin/bash
set -euo pipefail

# Read prompts and run regulatory validation
while read -r prompt; do
  echo "Testing: $prompt"
  
  # Get LLM output
  llm_output=$(./deterministic_wrapper.sh "$prompt")
  echo "LLM output: $llm_output"
  
  # Validate output
  validation_result=$(./validate_llm_output.sh "$prompt" "$llm_output")
  echo "Validation: $validation_result"
  
  echo "---"
done < regulatory_prompts.txt
