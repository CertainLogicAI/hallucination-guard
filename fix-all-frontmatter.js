#!/usr/bin/env node
/**
 * Fix all frontmatter by rewriting with strict YAML (no indentation)
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';

function getTags(filename) {
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

function inferSummary(content, filename) {
  const m = content.match(/^#\s+(.+)$/m);
  if (m) {
    let s = m[1].trim();
    if (s.length > 100) s = s.slice(0, 97) + '...';
    return s;
  }
  const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
  if (lines.length) {
    let s = lines[0].trim();
    if (s.length > 100) s = s.slice(0, 97) + '...';
    return s;
  }
  return filename.replace(/\.md$/, '').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function fixFile(relPath) {
  const full = path.join(ROOT, relPath);
  const content = fs.readFileSync(full, 'utf8');
  const hasFM = content.startsWith('---\n');
  let body = content;
  let existing = {};

  if (hasFM) {
    const end = content.indexOf('\n---\n', 4);
    if (end !== -1) {
      const fm = content.slice(4, end); // between markers
      body = content.slice(end + 5);
      // Very simple parser: key: value (one line)
      fm.split('\n').forEach(line => {
        const m = line.match(/^(\w+):\s*(.+)$/);
        if (m) existing[m[1]] = m[2].trim();
      });
    }
  }

  // Use existing summary or infer; use existing read_when or infer
  const summary = existing.summary || inferSummary(body, relPath);
  const read_when = existing.read_when ? (Array.isArray(existing.read_when) ? existing.read_when : [existing.read_when]) : getTags(relPath);

  const newFM = [
    '---',
    `summary: "${summary.replace(/"/g, '\\"')}"`,
    `read_when: [${read_when.map(t => `"${t}"`).join(', ')}]`,
    '---',
    ''
  ].join('\n');

  const newContent = newFM + body;
  if (newContent !== content) {
    fs.writeFileSync(full, newContent, 'utf8');
    return true;
  }
  return false;
}

function main() {
  const all = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'workspace-references') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        all.push(path.relative(ROOT, full));
      }
    }
  }
  walk(ROOT);

  let changed = 0;
  for (const file of all) {
    try {
      if (fixFile(file)) changed++;
    } catch (err) {
      console.error(`Error processing ${file}: ${err.message}`);
    }
  }

  console.log(`Fixed ${changed} of ${all.length} files.`);
}

main();
