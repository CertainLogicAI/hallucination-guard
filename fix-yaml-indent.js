#!/usr/bin/env node
/**
 * Fix YAML frontmatter indentation — enforce flush-left keys
 *
 * Rewrites all markdown files to have consistent YAML:
 *   ---
 *   summary: "..."
 *   read_when: ["..."]
 *   ---
 *
 * No indentation, no spaces before keys.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';

function ensureFrontmatter(content, filename) {
  // Split into frontmatter + body
  const hasFM = content.startsWith('---\n');
  let body = content;
  let existing = {};

  if (hasFM) {
    const end = content.indexOf('\n---\n', 4);
    if (end !== -1) {
      const fmPart = content.slice(4, end); // between the --- lines
      body = content.slice(end + 5);
      // Parse existing keys (ignore indentation)
      fmPart.split('\n').forEach(line => {
        const m = line.match(/^(\w+):\s*(.+)$/);
        if (m) existing[m[1]] = m[2].trim();
      }
    }
  }

  // Generate defaults if missing
  if (!existing.summary) {
    // Use first heading or fallback
    const m = body.match(/^#\s+(.+)$/m);
    existing.summary = m ? m[1].trim() : filename.replace(/\.md$/, '').replace(/[-_]/g, ' ');
    if (existing.summary.length > 100) existing.summary = existing.summary.slice(0, 97) + '...';
  }

  if (!existing.read_when) {
    // Generate tags from path
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
    existing.read_when = Array.from(tags).slice(0, 5);
  }

  // Ensure read_when is array (JSON format)
  if (!Array.isArray(existing.read_when)) {
    try {
      if (typeof existing.read_when === 'string') {
        if (existing.read_when.startsWith('[')) {
          existing.read_when = JSON.parse(existing.read_when.replace(/'/g, '"'));
        } else {
          existing.read_when = existing.read_when.split(',').map(s => s.trim());
        }
      } else {
        existing.read_when = [];
      }
    } catch {
      existing.read_when = [];
    }
  }

  // Build NEW frontmatter with NO indentation
  const fmLines = [
    '---',
    `summary: "${existing.summary.replace(/"/g, '\\"')}"`,
    `read_when: [${existing.read_when.map(t => `"${t}"`).join(', ')}]`,
    '---',
    ''
  ];

  return fmLines.join('\n') + body;
}

function walkAndFix() {
  let count = 0;
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'workspace-references') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        const rel = path.relative(ROOT, full);
        const content = fs.readFileSync(full, 'utf8');
        const fixed = ensureFrontmatter(content, rel);
        if (fixed !== content) {
          fs.writeFileSync(full, fixed, 'utf8');
          console.log(`Fixed: ${rel}`);
          count++;
        }
      }
    }
  }
  walk(ROOT);
  return count;
}

const total = walkAndFix();
console.log(`\nTotal frontmatter files fixed: ${total}`);
