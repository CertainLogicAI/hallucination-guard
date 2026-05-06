#!/usr/bin/env node
/**
 * memory-index.js — Build a reverse index of memory/*.md files by tags
 *
 * Reads frontmatter `read_when` arrays from each daily note and produces:
 * { "tag": ["2026-03-21.md", "2026-03-22.md", ...] }
 *
 * Output: /data/.openclaw/workspace/memory-index.json
 */

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const MEMORY_DIR = path.resolve('/data/.openclaw/workspace/memory');
const OUT_FILE = path.resolve('/data/.openclaw/workspace/memory-index.json');

function extractReadWhen(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  try {
    const { data } = matter(content);
    if (Array.isArray(data.read_when)) return data.read_when;
  } catch (e) {
    // Skip malformed frontmatter
  }
  return [];
}

function buildIndex() {
  const index = {};
  const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
  files.forEach(file => {
    const tags = extractReadWhen(path.join(MEMORY_DIR, file));
    tags.forEach(tag => {
      if (!index[tag]) index[tag] = [];
      index[tag].push(file);
    });
  });
  // sort file lists chronologically (by filename)
  Object.keys(index).forEach(tag => {
    index[tag].sort();
  });
  fs.writeFileSync(OUT_FILE, JSON.stringify(index, null, 2));
  console.log(`memory-index built: ${Object.keys(index).length} tags, ${files.length} files`);
}

if (require.main === module) {
  buildIndex();
}

module.exports = { buildIndex };
