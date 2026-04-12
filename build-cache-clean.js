#!/usr/bin/env node
/**
 * Build clean workspace cache — no gray-matter, simple regex extraction
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const OUT = path.join(ROOT, 'workspace-cache.json');
const REF_DIR = path.join(ROOT, 'workspace-references');

function extractFrontmatter(content, filename) {
  // Returns { summary: string, read_when: string[] } or defaults
  if (!content.startsWith('---\n')) {
    return { summary: inferSummary(content, filename), read_when: inferTags(filename) };
  }

  const end = content.indexOf('\n---\n', 4);
  if (end === -1) return { summary: inferSummary(content, filename), read_when: inferTags(filename) };

  const fm = content.slice(4, end); // between the --- lines
  const body = content.slice(end + 5);

  let summary = '';
  let read_when = [];

  // Extract summary
  const summaryMatch = fm.match(/^summary:\s*['"]?([^'"]+)['"]?/m);
  if (summaryMatch) summary = summaryMatch[1].trim();

  // Extract read_when (can be: read_when: ["a","b"]  or read_when: [a, b] or read_when: a, b)
  const readMatch = fm.match(/^read_when:\s*\[([^\]]+)\]\)?/m);
  if (readMatch) {
    const inner = readMatch[1];
    // Split by comma, strip quotes/spaces
    read_when = inner.split(',').map(s => s.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
  } else {
    // Single tag fallback
    const singleMatch = fm.match(/^read_when:\s*(\w+)/m);
    if (singleMatch) read_when = [singleMatch[1]];
  }

  if (!summary) summary = inferSummary(body, filename);
  if (read_when.length === 0) read_when = inferTags(filename);

  return { summary, read_when };
}

function inferSummary(content, filename) {
  const m = content.match(/^#\s+(.+)$/m);
  if (m) {
    let s = m[1].trim();
    if (s.length > 500) s = s.slice(0, 497) + '...';
    return s;
  }
  const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
  if (lines.length) {
    let s = lines[0].trim();
    if (s.length > 500) s = s.slice(0, 497) + '...';
    return s;
  }
  return filename.replace(/\.md$/, '').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function inferTags(filename) {
  const tags = new Set();
  if (filename.includes('ideas/')) tags.add('idea');
  if (filename.includes('skills/')) tags.add('skill');
  if (filename.includes('memory/')) tags.add('memory');
  if (filename.includes('workspace/')) tags.add('workspace');
  if (filename.includes('faulttrace')) tags.add('faulttrace');
  if (filename.includes('openclaw')) tags.add('openclaw');
  if (filename.includes('agent')) tags.add('agent');
  if (filename.includes('cost') || filename.includes('price')) tags.add('pricing');
  if (filename.includes('llm') || filename.includes('token')) tags.add('llm');
  if (filename.includes('docker')) tags.add('docker');
  if (filename.includes('api')) tags.add('api');
  return Array.from(tags).slice(0, 5);
}

function buildFiles() {
  const files = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'workspace-references') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        const rel = path.relative(ROOT, full);
        const stat = fs.statSync(full);
        const content = fs.readFileSync(full, 'utf8');
        const { summary, read_when } = extractFrontmatter(content, rel);
        files.push({
          path: rel,
          summary,
          read_when,
          size: stat.size,
          modified: stat.mtime.toISOString()
        });
      }
    }
  }
  walk(ROOT);
  return files;
}

function buildReferences() {
  const refs = [];
  if (!fs.existsSync(REF_DIR)) return refs;
  const files = fs.readdirSync(REF_DIR).filter(f => f.endsWith('.md'));
  for (const file of files) {
    const key = file.replace('.md', '');
    const full = path.join(REF_DIR, file);
    const content = fs.readFileSync(full, 'utf8');
    refs.push({ key, content });
  }
  return refs;
}

function buildIndex(files) {
  const index = {};
  for (const file of files) {
    for (const tag of file.read_when) {
      if (!index[tag]) index[tag] = [];
      index[tag].push(file.path);
    }
  }
  return index;
}

function main() {
  console.log('Building workspace cache (clean)...');

  const files = buildFiles();
  console.log(`  Indexed ${files.length} markdown files`);

  const references = buildReferences();
  console.log(`  Loaded ${references.length} reference blocks`);

  const index = buildIndex(files);
  console.log(`  Index built with ${Object.keys(index).length} tags`);

  const cache = {
    generated: new Date().toISOString(),
    files,
    references,
    index
  };

  fs.writeFileSync(OUT, JSON.stringify(cache, null, 2), 'utf8');
  const sizeKB = Math.round(fs.statSync(OUT).size / 1024);
  console.log(`Cache written to workspace-cache.json (${sizeKB} KB)`);
}

main();
