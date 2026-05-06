#!/usr/bin/env node
/**
 * backfill-memory-tags.js — Add richer read_when tags to historical memory entries
 *
 * Process:
 * 1. Load each memory/*.md file (except today's and backups)
 * 2. Parse frontmatter; extract existing tags
 * 3. Analyze body text to detect additional relevant tags via keyword patterns
 * 4. Merge tags (dedupe, alphabetical order)
 * 5. If changed, create .bak backup and write updated file
 *
 * Tag taxonomy:
 * - faulttrace, plc, l5x, controls        (PLC analyzer)
 * - deterministic, consulting             (Deterministic AI business)
 * - token-optimization, cache, memory-index, performance (efficiency)
 * - skills, monetization, business, gumroad, clawhub, clawmart (skills biz)
 * - security, audit, hardening            (security)
 * - x-api, twitter                        (X/Twitter integration)
 * - domains, patent                       (brand/IP)
 * - self-eval, beta                       (process/content types)
 */

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const MEMORY_DIR = path.resolve('/data/.openclaw/workspace/memory');
const SKIPS = new Set(['2026-03-28.md', /\.bak$/, /\.gz$/]);

function loadIndex() {
  const indexPath = path.resolve('/data/.openclaw/workspace/memory-index.json');
  if (fs.existsSync(indexPath)) {
    return JSON.parse(fs.readFileSync(indexPath, 'utf8'));
  }
  return {};
}

const TAG_PATTERNS = {
  'faulttrace': /\b(FaultTrace|faulttrace|plc-analyzer|PLC Analyzer)\b/i,
  'plc': /\b(PLC|controls engineer|Allen-Bradley|Rockwell|Siemens|Studio 5000|TIA Portal|ControlLogix|CompactLogix|GuardLogix|L5X|SCL|STL|Function Block)\b/i,
  'l5x': /\bL5X\b/i,
  'deterministic': /\bdeterministic\b/i,
  'consulting': /\bconsulting|discovery|proposal|client|engagement\b/i,
  'token-optimization': /\b(token|tokens|budget|optimization|context|efficiency)\b/i,
  'cache': /\b(cache|cached|redis|lru)\b/i,
  'memory-index': /\b(memory-index|tag index)\b/i,
  'performance': /\b(performance|latency|speed|fast|slow)\b/i,
  'skills': /\b(skill|skills|clawhub|clawmart|blenderism)\b/i,
  'monetization': /\b(monetization|revenue|gumroad|pricing|premium|buy|sell)\b/i,
  'business': /\b(business|product|launch|market|customers)\b/i,
  'security': /\b(security|audit|permissions|vulnerability|hardening)\b/i,
  'x-api': /\b(x-api|twitter-api|oauth| bearer token)\b/i,
  'domains': /\b(domain|dns|cloudflare|\.ai)\b/i,
  'patent': /\b(patent|ip|provisional|trademark)\b/i,
  'self-eval': /#+\s*Self-Eval/s,
  'beta': /\b(beta|tester|waitlist)\b/i,
  'openclaw': /\b(OpenClaw|openclaw)\b/i,
  'reference': /\b(reference|reference corpus|ground truth)\b/i,
  'guardrail': /\b(guardrail|hallucination|factual)\b/i
};

function detectTags(body) {
  const detected = new Set();
  for (const [tag, regex] of Object.entries(TAG_PATTERNS)) {
    if (regex.test(body)) {
      detected.add(tag);
    }
  }
  return Array.from(detected);
}

function mergeTags(existing, detected) {
  const combined = new Set(existing);
  detected.forEach(t => combined.add(t));
  // Return sorted alphabetically for consistency
  return Array.from(combined).sort();
}

function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const { data, content: body } = matter(content);
  const existingTags = Array.isArray(data.read_when) ? data.read_when : [];
  const detected = detectTags(body);
  const merged = mergeTags(existingTags, detected);

  if (merged.length !== existingTags.length || merged.some((t, i) => t !== existingTags[i])) {
    const newFrontmatter = { ...data, read_when: merged };
    const newContent = matter.stringify(body, newFrontmatter);
    // Backup
    fs.writeFileSync(filePath + '.bak', content, 'utf8');
    fs.writeFileSync(filePath, newContent, 'utf8');
    return { file: path.basename(filePath), added: merged.filter(t => !existingTags.includes(t)), total: merged.length };
  }
  return null;
}

function main() {
  const files = fs.readdirSync(MEMORY_DIR).filter(f => !SKIPS.has(f) && f.endsWith('.md'));
  let changed = 0, unchanged = 0, totalAdded = 0;
  console.log(`Backfilling tags for ${files.length} memory files...`);
  for (const file of files) {
    const full = path.join(MEMORY_DIR, file);
    const result = processFile(full);
    if (result) {
      changed++;
      totalAdded += result.added.length;
      console.log(`✓ ${result.file}: +${result.added.join(', ')} (total ${result.total})`);
    } else {
      unchanged++;
    }
  }
  console.log(`\nSummary: ${changed} updated, ${unchanged} unchanged, ${totalAdded} tags added`);
  console.log('Backups created with .bak extension');
  console.log('Next: run memory-index.js to rebuild the index');
}

main();
