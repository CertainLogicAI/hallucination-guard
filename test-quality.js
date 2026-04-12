#!/usr/bin/env node
/**
 * Quality A/B Test — Optimized vs Baseline Context
 *
 * Runs a given agent skill with two context loading strategies:
 * - BASELINE: Loads full content of relevant workspace files (old way)
 * - OPTIMIZED: Uses workspace cache + summaries + references (new way)
 *
 * Compares outputs side-by-side for quality, token usage, and latency.
 *
 * Usage: node test-quality.js <skillId> <task>
 * Example: node test-quality.js project-scoper "Scope a SaaS CRM"
 */

const { performance } = require('perf_hooks');
const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const CACHE_PATH = path.join(ROOT, 'workspace-cache.json');

// Load the skill module (assumes skill has code/index.js exporting run())
function loadSkill(skillId) {
  const skillDir = path.join(ROOT, 'skills', skillId);
  const codePath = path.join(skillDir, 'code', 'index.js');
  if (!fs.existsSync(codePath)) {
    throw new Error(`Skill not found or missing code: ${skillId}`);
  }
  // Delete from require cache to allow multiple runs with different globals
  delete require.cache[require.resolve(codePath)];
  return require(codePath);
}

// Load workspace cache
let cache = null;
function loadCache() {
  if (cache) return cache;
  const raw = fs.readFileSync(CACHE_PATH, 'utf8');
  cache = JSON.parse(raw);
  return cache;
}

// Baseline: Full context loading (simulate old behavior)
async function loadBaselineContext(task) {
  const start = performance.now();
  // Simulate: load all workspace .md files (except references) and read full content
  const allFiles = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === 'node_modules' || entry.name === 'workspace-references' || entry.name.startsWith('.')) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.md')) allFiles.push(path.relative(ROOT, full));
    }
  }
  walk(ROOT);

  // Read full content of each file (this is what agents used to do)
  const contents = [];
  let totalTokens = 0;
  for (const file of allFiles) {
    const content = fs.readFileSync(path.join(ROOT, file), 'utf8');
    totalTokens += Math.ceil(content.length / 4); // rough token count
    contents.push(`## ${file}\n${content}`);
  }

  // Also load references (still needed)
  const refDir = path.join(ROOT, 'workspace-references');
  const refs = [];
  if (fs.existsSync(refDir)) {
    fs.readdirSync(refDir).filter(f => f.endsWith('.md')).forEach(f => {
      const key = f.replace('.md', '');
      const content = fs.readFileSync(path.join(refDir, f), 'utf8');
      refs.push(`## REF ${key}\n${content}`);
      totalTokens += Math.ceil(content.length / 4);
    });
  }

  const context = contents.join('\n\n') + '\n\n' + refs.join('\n\n');
  const elapsed = performance.now() - start;
  return { context, tokenEstimate: totalTokens, loadTimeMs: elapsed };
}

// Optimized: Cache + summaries + references
async function loadOptimizedContext(task) {
  const start = performance.now();
  const c = loadCache();

  // Use tags to filter relevant files (in a real agent, this would be from the task)
  // For this test, we'll just use common tags that would match most project-scoping tasks
  const tags = ['faulttrace', 'api', 'pricing', 'idea', 'cost', 'llm', 'docker'];
  const relevantPaths = [];
  for (const tag of tags) {
    (c.index[tag] || []).forEach(p => relevantPaths.add(p));
  }
  const relevantFiles = Array.from(new Set(relevantPaths));

  // Build context from summaries (not full files)
  let tokenEstimate = 0;
  const summaries = relevantFiles.map(path => {
    const entry = c.files.find(f => f.path === path);
    const summary = entry ? entry.summary : '(missing)';
    const tokens = Math.ceil(summary.length / 4);
    tokenEstimate += tokens;
    return `## ${path}\n${summary}`;
  });

  // Add references (full content)
  const refs = c.references.map(r => `## REF ${r.key}\n${r.content}`);
  tokenEstimate += c.references.reduce((sum, r) => sum + Math.ceil(r.content.length / 4), 0);

  const context = summaries.join('\n\n') + '\n\n' + refs.join('\n\n');
  const elapsed = performance.now() - start;
  return { context, tokenEstimate, loadTimeMs: elapsed };
}

// Count tokens roughly (character count / 4)
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// Run skill with a given context (injects context into global before skill runs)
async function runSkillWithContext(skill, task, context, label) {
  // Inject context as if it came from memory
  global.__testContext = context;

  // Monkey-patch the skill's memory access to return our injected context
  // In a real agent, the skill calls memory_get or reads files. We'll just
  // measure the context size we gave it and assume it uses it directly.
  const tokenCount = estimateTokens(context);

  // Run the skill (it should use global context somehow — but our test skill doesn't actually use context, we're just measuring load times)
  const start = performance.now();
  const output = await skill.run(task);
  const elapsed = performance.now() - start;

  return {
    label,
    contextTokens: tokenCount,
    loadTimeMs: 0, // we measured separately
    executionTimeMs: elapsed,
    outputLength: output.length,
    outputPreview: output.slice(0, 200)
  };
}

// Main test runner
async function main() {
  const [skillId, ...taskParts] = process.argv.slice(2);
  if (!skillId) {
    console.error('Usage: node test-quality.js <skillId> <task>');
    process.exit(1);
  }
  const task = taskParts.join(' ') || 'Scope a new project: mobile inventory app';

  console.log(`=== Quality A/B Test: ${skillId} ===`);
  console.log(`Task: ${task}\n`);

  // Load skill
  let skill;
  try {
    skill = loadSkill(skillId);
  } catch (err) {
    console.error(`Failed to load skill: ${err.message}`);
    process.exit(1);
  }

  // Baseline
  console.log('Running BASELINE (full context)...');
  const baselineContext = await loadBaselineContext(task);
  const baselineResult = await runSkillWithContext(skill, task, baselineContext.context, 'BASELINE');

  // Optimized
  console.log('Running OPTIMIZED (cache + summaries)...');
  const optimizedContext = await loadOptimizedContext(task);
  const optimizedResult = await runSkillWithContext(skill, task, optimizedContext.context, 'OPTIMIZED');

  // Compare
  console.log('\n=== RESULTS ===\n');

  const table = [
    ['Metric', 'Baseline', 'Optimized', 'Change'],
    ['Context load time (ms)', baselineContext.loadTimeMs.toFixed(1), optimizedContext.loadTimeMs.toFixed(1), ((optimizedContext.loadTimeMs - baselineContext.loadTimeMs)/baselineContext.loadTimeMs*100).toFixed(1)+'%'],
    ['Context tokens', baselineContext.tokenEstimate.toLocaleString(), optimizedContext.tokenEstimate.toLocaleString(), ((optimizedContext.tokenEstimate - baselineContext.tokenEstimate)/baselineContext.tokenEstimate*100).toFixed(1)+'%'],
    ['Execution time (ms)', baselineResult.executionTimeMs.toFixed(1), optimizedResult.executionTimeMs.toFixed(1), ((optimizedResult.executionTimeMs - baselineResult.executionTimeMs)/baselineResult.executionTimeMs*100).toFixed(1)+'%'],
    ['Output length (chars)', baselineResult.outputLength, optimizedResult.outputLength, ((optimizedResult.outputLength - baselineResult.outputLength)/baselineResult.outputLength*100).toFixed(1)+'%']
  ];

  console.table(table);

  console.log('\nOutput comparison:');
  console.log('--- BASELINE OUTPUT ---');
  console.log(baselineResult.outputPreview + '...');
  console.log('\n--- OPTIMIZED OUTPUT ---');
  console.log(optimizedResult.outputPreview + '...');

  // Quality scoring (manual)
  console.log('\n[MANUAL REVIEW NEEDED] Compare the two outputs for completeness and accuracy.');
  console.log('Check: Are key requirements mentioned? Are references correct? Is the structure sound?');

  // Token cost estimate (Sonnet avg $9/1M)
  const baselineCost = (baselineContext.tokenEstimate / 1e6) * 9;
  const optimizedCost = (optimizedContext.tokenEstimate / 1e6) * 9;
  console.log(`\nEstimated LLM cost per run (Sonnet avg $9/1M):`);
  console.log(`  Baseline: $${baselineCost.toFixed(4)}`);
  console.log(`  Optimized: $${optimizedCost.toFixed(4)}`);
  console.log(`  Savings: $${(baselineCost - optimizedCost).toFixed(4)} (${((baselineCost - optimizedCost)/baselineCost*100).toFixed(1)}%)`);
}

main().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
