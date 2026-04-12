#!/usr/bin/env node
/**
 * Build workspace cache — use gray-matter for reliable YAML parsing
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
        try {
          const { data, content } = matter.read(full);
          // Coerce read_when to array
          let read_when = data.read_when || [];
          if (typeof read_when === 'string') {
            try {
              // Try parse as JSON
              const parsed = JSON.parse(read_when.replace(/'/g, '"'));
              read_when = Array.isArray(parsed) ? parsed : [read_when];
            } catch {
              read_when = read_when.split(',').map(s => s.trim()).filter(Boolean);
            }
          }
          if (!Array.isArray(read_when)) read_when = [];

          files.push({
            path: rel,
            summary: (data.summary || '').trim(),
            read_when,
            size: stat.size,
            modified: stat.mtime.toISOString()
          });
        } catch (err) {
          console.error(`Failed to parse ${rel}: ${err.message}`);
        }
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
    // Keep entire file content; agent will need it whole
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
}

main();
