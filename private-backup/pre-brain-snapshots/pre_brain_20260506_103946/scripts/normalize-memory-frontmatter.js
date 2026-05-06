#!/usr/bin/env node
/**
 * normalize-memory-frontmatter.js — Fix malformed read_when arrays in memory/*.md
 *
 * Problem: older files have: read_when: ["["memory"]"]
 * Fix: change to proper YAML array: read_when: ["memory"]
 *
 * Makes a backup copy .bak before editing.
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.resolve('/data/.openclaw/workspace/memory');

function fixReadWhen(content) {
  const lines = content.split('\n');
  let changed = false;
  const newLines = lines.map(line => {
    if (!line.startsWith('read_when:')) return line;
    // Extract candidate alphanumeric tokens after the colon
    const afterColon = line.split('read_when:')[1] || '';
    const candidates = afterColon.match(/[a-zA-Z0-9_]+/g) || [];
    const tags = candidates.filter(t => !['[',']'].includes(t));
    if (tags.length === 0) return line;
    const newLine = `read_when: [${tags.map(t => `"${t}"`).join(', ')}]`;
    if (newLine !== line) changed = true;
    return newLine;
  });
  return { content: newLines.join('\n'), changed };
}

function processFile(filePath) {
  const backupPath = filePath + '.bak';
  fs.copyFileSync(filePath, backupPath); // keep backup
  const original = fs.readFileSync(filePath, 'utf8');
  const { content: fixed, changed } = fixReadWhen(original);
  if (changed) {
    fs.writeFileSync(filePath, fixed, 'utf8');
    console.log(`fixed: ${path.basename(filePath)}`);
  } else {
    console.log(`ok: ${path.basename(filePath)}`);
  }
}

function main() {
  const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
  files.forEach(f => processFile(path.join(MEMORY_DIR, f)));
  console.log(`processed ${files.length} files`);
}

if (require.main === module) main();
module.exports = { fixReadWhen };
