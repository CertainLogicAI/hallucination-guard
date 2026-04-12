#!/usr/bin/env node
/**
 * Demonstrate LLM response cache effectiveness
 */

const { getRelevantFiles, getFileSummary, getReference, getCachedLLMResponse, setCachedLLMResponse } = require('/data/.openclaw/workspace/workspace-cache-client');

async function simulateLLMCall(task, systemPrompt) {
  const model = 'anthropic/claude-sonnet-4-6';
  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: task }
  ];
  const options = { max_tokens: 4000 };

  const cached = await getCachedLLMResponse(model, messages, options);
  if (cached.cached) {
    console.log('✅ LLM CACHE HIT - zero API cost, instant response');
    return cached.response;
  }

  console.log('❌ LLM cache miss - would call API now');
  // Simulate expensive LLM call
  await new Promise(r => setTimeout(r, 500)); // simulate latency
  const response = `Simulated LLM response for: ${task}\n\nBased on FaultTrace capabilities...`;
  await setCachedLLMResponse(model, messages, options, response, { totalTokens: 150 });
  console.log('💾 Response cached');
  return response;
}

async function main() {
  const task = "Scope a plugin system for FaultTrace that lets users write custom L5X rules in JavaScript";

  // Build system prompt (using cache for references)
  const faulttraceRef = getReference('faulttrace-product') || 'missing';
  const pricingRef = getReference('pricing-subscription') || 'missing';
  const relevantFiles = getRelevantFiles(['faulttrace', 'api', 'pricing']);
  const context = relevantFiles.map(p => `## ${p}\n${getFileSummary(p) || ''}`).join('\n\n');

  const systemPrompt = `You are a project scoper.

FaultTrace:
${faulttraceRef.slice(0, 1000)}

Pricing:
${pricingRef.slice(0, 500)}

Workspace:
${context}`;

  console.log('=== First call (cache miss) ===');
  const r1 = await simulateLLMCall(task, systemPrompt);
  console.log(`Response length: ${r1.length} chars\n`);

  console.log('=== Second call (should be cache hit) ===');
  const r2 = await simulateLLMCall(task, systemPrompt);
  console.log(`Response length: ${r2.length} chars\n`);

  console.log(' identical?', r1 === r2 ? '✅ Yes' : '❌ No');
}

main().catch(console.error);
