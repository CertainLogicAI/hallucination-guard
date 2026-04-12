#!/usr/bin/env node
/**
 * Build Workspace Cache — single JSON file for fast agent startup
 *
 * Output: workspace-cache.json (≈ 50–100KB)
 *
 * Contains:
 * - files[]: { path, summary, read_when, size, modified }
 * - references[]: { key, content }
 * - index: { tag -> [file paths] }
 */

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const ROOT = '/data/.openclaw/workspace';
const OUT = path.join(ROOT, 'workspace-cache.json');
const REF_DIR = path.join(ROOT, 'workspace-references');

function buildFileEntries() {
  const files = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === 'node_modules' || entry.name.startsWith('.') || entry.name === 'workspace-references') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        const rel = path.relative(ROOT, full);
        const stat = fs.statSync(full);
        const content = fs.readFileSync(full, 'utf8');
        const { data, body } = matter(content);
        files.push({
          path: rel,
          summary: data.summary || '',
          read_when: Array.isArray(data.read_when) ? data.read_when : [],
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
    // Strip delimiters if present (### REFERENCE markers)
    let clean = content;
    const startMarker = `### REFERENCE: ${key} ###`;
    const endMarker = `### END REFERENCE ###`;
    const startIdx = clean.indexOf(startMarker);
    const endIdx = clean.indexOf(endMarker);
    if (startIdx !== -1 && endIdx !== -1) {
      clean = clean.slice(startIdx + startMarker.length, endIdx).trim();
    }
    refs.push({ key, content: clean });
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
  console.log('Building workspace cache...');

  const files = buildFileEntries();
  console.log(`  Indexed ${files.length} markdown files`);

  const references = buildReferences();
  console.log(`  Loaded ${references.length} reference blocks`);

  const index = buildIndex(files);
  const indexStats = Object.entries(index).map(([tag, list]) => `${tag}:${list.length}`).join(', ');
  console.log(`  Index tags: ${indexStats}`);

  const cache = {
    generated: new Date().toISOString(),
    files,
    references,
    index
  };

  fs.writeFileSync(OUT, JSON.stringify(cache, null, 2), 'utf8');
  const sizeKB = Math.round(fs.statSync(OUT).size / 1024);
  console.log(`Cache written to workspace-cache.json (${sizeKB} KB)`);

  // Also create a binary .packed version? Not needed yet.
}

main();
