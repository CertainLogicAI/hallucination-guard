#!/usr/bin/env node
/**
 * Project Scoper Agent — uses workspace cache for efficient memory access
 * Optimized: uses summaries only, never loads full file content
 * Also demonstrates LLM response caching pattern
 */

const { getRelevantFiles, getFileSummary, getReference, getCachedLLMResponse, setCachedLLMResponse } = require('/data/.openclaw/workspace/workspace-cache-client');

/**
 * Main agent execution
 * @param {string} task - User's project scoping request
 */
// Token budget enforcement (per-skill safety)
const MAX_OUTPUT_TOKENS = parseInt(process.env.MAX_OUTPUT_TOKENS || '4000', 10);

function estimateTokenCount(text) {
  // Rough: 1 token ≈ 4 chars for English; adjust for code
  return Math.ceil(text.length / 4);
}

async function run(task) {
  console.log('[ProjectScoper] Received task:', task.substring(0, 100), '...');

  // Use cache to quickly load relevant workspace files (SUMMARIES ONLY)
  const relevantFiles = getRelevantFiles(['faulttrace', 'api', 'pricing', 'idea', 'cost']);
  console.log(`[ProjectScoper] Relevant files (via cache): ${relevantFiles.length}`);

  // Use summaries from cache — no file I/O, ~100 tokens per file instead of 2000+
  const context = relevantFiles.map(path => {
    const summary = getFileSummary(path) || '(no summary)';
    return `## ${path}\n${summary}`;
  }).join('\n\n');

  // Load canonical references (full content, not summarized)
  const faulttraceRef = getReference('faulttrace-product') || 'FaultTrace reference missing';
  const pricingRef = getReference('pricing-subscription') || 'Pricing reference missing';

  // Build system prompt using cached references (deduplication: no need to embed full content each time)
  const systemPrompt = `You are a project scoping assistant.

Reference: FaultTrace product
${faulttraceRef}

Reference: Pricing models
${pricingRef}

Workspace context (filtered files):
${context}

Your job: given the user's project idea, produce a scoping document following the structure in the examples. Use the references to ensure consistency.`;

  // LLM call with response caching
  const model = 'anthropic/claude-sonnet-4-6'; // could be configurable
  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: task }
  ];
  const options = { max_tokens: 4000 };

  // Check LLM response cache first
  const cached = await getCachedLLMResponse(model, messages, options);
  if (cached.cached) {
    console.log('[ProjectScoper] LLM cache HIT - skipping expensive inference');
    return cached.response;
  }

  console.log('[ProjectScoper] LLM cache miss - invoking model');
  // In a real implementation, call the LLM via OpenClaw's agent runtime or API
  // For this demo, we simulate a response that demonstrates quality
  const output = `# Project Scope: ${task}

## Overview
This document outlines the scope for the proposed project, leveraging FaultTrace's product capabilities and pricing tiers.

## FaultTrace Integration
${faulttraceRef.slice(0, 500)}...

## Pricing Considerations
${pricingRef.slice(0, 500)}...

## Relevant Workspace Context
${relevantFiles.length} files consulted via workspace cache.

## Next Steps
- [ ] Detailed requirements gathering
- [ ] Technical architecture review
- [ ] Cost analysis based on selected tier
`;

  // Cache the result for future identical queries (24h TTL)
  const outputTokens = estimateTokenCount(output);
  await setCachedLLMResponse(model, messages, options, output, { totalTokens: outputTokens });
  console.log('[ProjectScoper] LLM response cached');

  // Enforce token budget
  if (outputTokens > MAX_OUTPUT_TOKENS) {
    console.warn(`[ProjectScoper] Output exceeds token budget (${outputTokens} > ${MAX_OUTPUT_TOKENS}). Truncating.`);
    // Truncate to budget (roughly)
    const truncateAt = Math.floor(MAX_OUTPUT_TOKENS * 4 * 0.9); // 90% of budget in chars
    return output.slice(0, truncateAt) + '\n\n[TRUNCATED - TOKEN BUDGET EXCEEDED]';
  }

  return output;
}

// Export for OpenClaw agent runtime
module.exports = { run };

// If run directly (CLI), take task from argv
if (require.main === module) {
  const task = process.argv.slice(2).join(' ') || 'Scope a new project';
  run(task).then(output => {
    console.log('\n=== OUTPUT ===\n');
    console.log(output);
  }).catch(err => {
    console.error('Agent error:', err);
    process.exit(1);
  });
}
