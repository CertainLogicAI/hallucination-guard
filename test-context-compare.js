#!/usr/bin/env node
/**
 * Context Quality Comparison — Baseline vs Optimized
 *
 * Measures:
 * - Time to build context
 * - Token count of context
 * - What information is present/absent
 *
 * Usage: node test-context-compare.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const CACHE_PATH = path.join(ROOT, 'workspace-cache.json');

let cache = null;
function loadCache() {
  if (cache) return cache;
  const raw = fs.readFileSync(CACHE_PATH, 'utf8');
  cache = JSON.parse(raw);
  return cache;
}

// Baseline: Load ALL .md files full content (old behavior)
function buildBaselineContext() {
  console.log('Building baseline context (full workspace)...');
  const start = Date.now();
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

  let totalTokens = 0;
  let totalChars = 0;
  const samples = [];

  for (const file of allFiles) {
    const content = fs.readFileSync(path.join(ROOT, file), 'utf8');
    totalChars += content.length;
    totalTokens += Math.ceil(content.length / 4);
    if (samples.length < 3) samples.push({ file, preview: content.slice(0, 300) });
  }

  // Add references
  const refDir = path.join(ROOT, 'workspace-references');
  if (fs.existsSync(refDir)) {
    fs.readdirSync(refDir).filter(f => f.endsWith('.md')).forEach(f => {
      const content = fs.readFileSync(path.join(refDir, f), 'utf8');
      totalChars += content.length;
      totalTokens += Math.ceil(content.length / 4);
    });
  }

  const elapsed = Date.now() - start;
  return { totalFiles: allFiles.length, totalTokens, totalChars, elapsedMs: elapsed, samples };
}

// Optimized: Cache + summaries + references
function buildOptimizedContext() {
  console.log('Building optimized context (cache + summaries)...');
  const start = Date.now();
  const c = loadCache();

  // Use tags that would match a project-scoping task
  const tags = ['faulttrace', 'api', 'pricing', 'idea', 'cost', 'llm', 'docker'];
  const relevantPaths = new Set();
  for (const tag of tags) {
    (c.index[tag] || []).forEach(p => relevantPaths.add(p));
  }
  const relevantFiles = Array.from(relevantPaths);

  let totalTokens = 0;
  let totalChars = 0;
  const samples = [];

  // Summaries only
  for (const path of relevantFiles) {
    const entry = c.files.find(f => f.path === path);
    const text = entry ? `## ${entry.path}\n${entry.summary}` : '(missing)';
    totalChars += text.length;
    totalTokens += Math.ceil(text.length / 4);
    if (samples.length < 3) samples.push({ file: path, preview: text.slice(0, 300) });
  }

  // References (full)
  for (const ref of c.references) {
    totalChars += ref.content.length;
    totalTokens += Math.ceil(ref.content.length / 4);
  }

  const elapsed = Date.now() - start;
  return { relevantFiles: relevantFiles.length, totalTokens, totalChars, elapsedMs: elapsed, samples };
}

function main() {
  console.log('=== Workspace Context Quality Comparison ===\n');

  const baseline = buildBaselineContext();
  console.log('\n[ BASELINE ]');
  console.log(`Files loaded: ${baseline.totalFiles}`);
  console.log(`Total tokens: ${baseline.totalTokens.toLocaleString()}`);
  console.log(`Total chars: ${baseline.totalChars.toLocaleString()}`);
  console.log(`Load time: ${baseline.elapsedMs}ms`);
  console.log('\nSample content (first 3 files):');
  baseline.samples.forEach(s => {
    console.log(`\n--- ${s.file} ---\n${s.preview}...`);
  });

  const optimized = buildOptimizedContext();
  console.log('\n[ OPTIMIZED ]');
  console.log(`Relevant files: ${optimized.relevantFiles}`);
  console.log(`Total tokens: ${optimized.totalTokens.toLocaleString()}`);
  console.log(`Total chars: ${optimized.totalChars.toLocaleString()}`);
  console.log(`Load time: ${optimized.elapsedMs}ms`);
  console.log('\nSample content (summaries + refs):');
  optimized.samples.forEach(s => {
    console.log(`\n--- ${s.file} ---\n${s.preview}...`);
  });

  console.log('\n=== COMPARISON ===');
  const tokenReduction = ((baseline.totalTokens - optimized.totalTokens) / baseline.totalTokens * 100).toFixed(1);
  const speedup = ((baseline.elapsedMs - optimized.elapsedMs) / baseline.elapsedMs * 100).toFixed(1);
  console.log(`Token reduction: ${tokenReduction}%`);
  console.log(`Context build speed: ${speedup}% faster`);

  console.log('\n=== QUALITY CHECK ===');
  console.log('Review the samples above. Ask:');
  console.log('- Does the optimized context contain enough information to answer project-scoping questions?');
  console.log('- Are key details (FaultTrace capabilities, pricing tiers, Docker deployment) present?');
  console.log('- Are any critical files missing from the relevant set?');
  console.log('\nIf summaries are too terse, we can increase summary length in the cache build.');
}

main();
