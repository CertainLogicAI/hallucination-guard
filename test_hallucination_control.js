#!/usr/bin/env node
/**
 * Hallucination Control Test
 * Demonstrates how guardrails, caching, and reference-based reasoning prevent hallucinations
 * while maintaining performance.
 */

const { getRelevantFiles, getFileSummary, getReference, getCachedLLMResponse, setCachedLLMResponse } = require('/data/.openclaw/workspace/workspace-cache-client');

// Simulate an LLM call with latency and token usage
async function callLLM(model, messages, options) {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 200)); // 200ms latency
  
  // Extract user query
  const userMsg = messages.find(m => m.role === 'user')?.content || '';
  
  // Simulate two types of responses: accurate or hallucinated
  let response;
  if (userMsg.toLowerCase().includes('unused tag')) {
    // Accurate response based on reference
    response = "Unused tags are flagged by Rule 12 in FaultTrace. They represent memory allocated but never read, wasting resources.";
  } else if (userMsg.toLowerCase().includes('pricing')) {
    // Accurate response based on pricing reference
    response = "FaultTrace offers four subscription tiers: Hobbyist ($9/mo, 5 analyses), Pro ($49/mo, 100 analyses), Team ($99/mo, 500 analyses, 3 seats), and Enterprise (custom).";
  } else if (userMsg.toLowerCase().includes('faulttrace')) {
    // Accurate response
    response = "FaultTrace is a static analysis tool for Allen-Bradley PLC code (L5X files) that scans for common issues, unused tags, type mismatches, and safety violations without executing the code.";
  } else {
    // Hallucinated response (plausible but false)
    response = "FaultTrace uses quantum computing to analyze PLC code in real-time, reducing analysis time by 99.9% and eliminating the need for L5X files.";
  }
  
  // Simulate token usage
  const inputTokens = Math.ceil((JSON.stringify(messages).length + JSON.stringify(options).length) / 4);
  const outputTokens = Math.ceil(response.length / 4);
  
  return {
    response,
    usage: { inputTokens, outputTokens, totalTokens: inputTokens + outputTokens }
  };
}

// Guardrail: check if response is supported by reference text
function isResponseSupported(response, reference) {
  if (!reference) return false;
  // Simple check: look for key phrases from response in reference
  const keyPhrases = response
    .toLowerCase()
    .match(/[a-z]+/g)
    .filter(w => w.length > 4) // ignore short words
    .slice(0, 10); // first 10 meaningful words
  
  const matches = keyPhrases.filter(phrase => reference.toLowerCase().includes(phrase));
  return matches.length >= 3; // at least 3 key phrases found in reference
}

// Run test for a given query
async function testQuery(query) {
  console.log(`\n=== Testing Query: "${query}" ===`);
  
  // Step 1: Get relevant context from cache (summaries only)
  const startContext = Date.now();
  const relevantFiles = getRelevantFiles(['faulttrace', 'pricing']);
  const context = relevantFiles.map(path => {
    const summary = getFileSummary(path) || '(no summary)';
    return `## ${path}\n${summary}`;
  }).join('\n\n');
  
  // Get full references (not summarized)
  const faulttraceRef = getReference('faulttrace-product') || '';
  const pricingRef = getReference('pricing-subscription') || '';
  const contextTime = Date.now() - startContext;
  
  // Step 2: Build system prompt with guardrail instruction
  const systemPrompt = `You are a helpful assistant. Answer based ONLY on the provided references.
If you are uncertain or the information is not in the references, say "I don't have enough information to answer that."
References:
FaultTrace: ${faulttraceRef}
Pricing: ${pricingRef}

Context (summaries):
${context}`;
  
  // Step 3: Check LLM cache first
  const model = 'test-model';
  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: query }
  ];
  const options = { max_tokens: 500 };
  
  const startLLM = Date.now();
  const cached = await getCachedLLMResponse(model, messages, options);
  let llmResult;
  
  if (cached.cached) {
    console.log('🟢 LLM Cache HIT - no API call needed');
    llmResult = { response: cached.response, usage: cached.usage };
  } else {
    console.log('🔴 LLM Cache MISS - simulating API call');
    llmResult = await callLLM(model, messages, options);
    // Cache the result
    await setCachedLLMResponse(model, messages, options, llmResult.response, llmResult.usage);
  }
  
  const llmTime = Date.now() - startLLM;
  
  // Step 4: Apply guardrail
  const isSupported = isResponseSupported(llmResult.response, faulttraceRef + pricingRef);
  let finalResponse = llmResult.response;
  
  if (!isSupported) {
    console.log('🛡️  Guardrail triggered: Response not supported by references');
    finalResponse = "I don't have enough information to answer that based on the provided references.";
  } else {
    console.log('✅ Response validated by reference check');
  }
  
  // Step 5: Report results
  console.log(`\n--- Results ---`);
  console.log(`Context load time: ${contextTime}ms`);
  console.log(`LLM processing time: ${llmTime}ms`);
  console.log(`Total tokens used: ${llmResult.usage.totalTokens}`);
  console.log(`Response: ${finalResponse}`);
  console.log(`Hallucination prevented: ${!isSupported ? 'YES' : 'NO (response was accurate)'}`);
  
  return {
    query,
    contextTime,
    llmTime,
    tokens: llmResult.usage.totalTokens,
    response: finalResponse,
    hallucinationPrevented: !isSupported
  };
}

// Run multiple tests
async function main() {
  console.log('=== Hallucination Control Test Suite ===');
  
  const queries = [
    "What is FaultTrace?",
    "How does FaultTrace detect unused tags?",
    "What are the subscription tiers for FaultTrace?",
    "How much does FaultTrace cost per analysis?", // slightly ambiguous
    "Can FaultTrace analyze Siemens TIA Portal files?", // should trigger guardrail (not in references yet)
    "What programming language is FaultTrace written in?" // not in references
  ];
  
  let totalTokens = 0;
  let hallucinationsPrevented = 0;
  
  for (const query of queries) {
    const result = await testQuery(query);
    totalTokens += result.tokens;
    if (result.hallucinationPrevented) hallucinationsPrevented++;
  }
  
  console.log(`\n=== Summary ===`);
  console.log(`Total queries: ${queries.length}`);
  console.log(`Total tokens used: ${totalTokens}`);
  console.log(`Average tokens per query: ${Math.round(totalTokens / queries.length)}`);
  console.log(`Hallucinations prevented: ${hallucinationsPrevented}/${queries.length} (${Math.round((hallucinationsPrevented/queries.length)*100)}%)`);
  
  // Performance note: without cache, each query would load full files (~150k tokens)
  // With cache, we use ~3k tokens per query (context) + LLM output
  const estimatedBaselineTokens = queries.length * 150000; // 150k per query baseline
  const savings = ((estimatedBaselineTokens - totalTokens) / estimatedBaselineTokens * 100).toFixed(1);
  console.log(`Estimated token savings vs baseline: ${savings}%`);
}

main().catch(console.error);
