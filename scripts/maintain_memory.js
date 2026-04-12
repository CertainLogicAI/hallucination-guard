#!/usr/bin/env node
/**
 * maintain_memory.js — Daily memory maintenance routine
 *
 * Runs:
 * 1. Summarize memory files (concise storage)
 * 2. normalize-memory-frontmatter.js (fix broken read_when)
 * 3. memory-index.js (rebuild tag index)
 * 4. Clear memory-query-cache.json (invalidate cache after corpus changes)
 *
 * Usage: node scripts/maintain_memory.js
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const matter = require('gray-matter');
const { summarize } = require('./summarize.js');

const ROOT = path.resolve('/data/.openclaw/workspace');
const MEMORY_DIR = path.join(ROOT, 'memory');
const NORMALIZE = path.join(ROOT, 'scripts', 'normalize-memory-frontmatter.js');
const INDEX = path.join(ROOT, 'scripts', 'memory-index.js');

function run(script) {
  try {
    execSync(`node ${script}`, { stdio: 'inherit' });
  } catch (e) {
    console.error(`Error running ${script}:`, e.message);
    process.exit(1);
  }
}

function summarizeMemoryFiles() {
  const today = new Date().toISOString().slice(0, 10) + '.md';
  const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md') && !f.endsWith('.bak') && !f.endsWith('.gz') && f !== today);
  let totalSummarized = 0;
  for (const file of files) {
    const fullPath = path.join(MEMORY_DIR, file);
    const raw = fs.readFileSync(fullPath, 'utf8');
    const { data, content: body } = matter(raw);
    const summarized = summarize(body);
    if (summarized !== body) {
      // Backup before overwrite
      fs.copyFileSync(fullPath, fullPath + '.bak');
      const newContent = matter.stringify(summarized, data);
      fs.writeFileSync(fullPath, newContent, 'utf8');
      totalSummarized++;
      console.log(`summarized ${file} (${body.length} → ${summarized.length} chars)`);
    }
  }
  console.log(`Summarized ${totalSummarized} files.`);
}

function clearQueryCache() {
  const cachePath = path.join(ROOT, 'memory-query-cache.json');
  if (fs.existsSync(cachePath)) {
    fs.unlinkSync(cachePath);
    console.log('Cleared memory query cache.');
  }
}

console.log('Starting memory maintenance...');
summarizeMemoryFiles();
run(NORMALIZE);
run(INDEX);
clearQueryCache();
console.log('Memory maintenance complete.');
