#!/usr/bin/env node
/**
 * Reference Replacer v2 — Exact block substitution
 *
 * Each reference file has a block between:
 *   # FAULTTFAULTTRACE-REFERENCE-START
 *   ...exact content...
 *   # FAULTTFAULTTRACE-REFERENCE-END
 *
 * We'll find that exact block in other files and replace it with `{faulttrace}`.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const REF_DIR = path.join(ROOT, 'workspace-references');

// Reference mapping: keyword -> { file, markerStart, markerEnd, content }
const REFS = {};

function loadReferences() {
  const files = fs.readdirSync(REF_DIR).filter(f => f.endsWith('.md'));
  for (const file of files) {
    const key = file.replace('.md', '');
    const fullPath = path.join(REF_DIR, file);
    const content = fs.readFileSync(fullPath, 'utf8');
    const startMarker = `# ${key.toUpperCase()}-REFERENCE-START`;
    const endMarker = `# ${key.toUpperCase()}-REFERENCE-END`;
    const startIdx = content.indexOf(startMarker);
    const endIdx = content.indexOf(endMarker);
    if (startIdx === -1 || endIdx === -1) {
      console.warn(`Reference ${file} missing markers, skipping`);
      continue;
    }
    const blockStart = startIdx + startMarker.length + 1; // after marker line
    const blockEnd = endIdx;
    const blockContent = content.slice(blockStart, blockEnd).trim();
    REFS[key] = {
      file,
      markerStart: startMarker,
      markerEnd: endMarker,
      content: blockContent
    };
  }
  console.log(`Loaded ${Object.keys(REFS).length} references`);
}

function replaceInFile(filePath) {
  const fullPath = path.join(ROOT, filePath);
  const original = fs.readFileSync(fullPath, 'utf8');
  let modified = false;
  let newContent = original;

  for (const [key, ref] of Object.entries(REFS)) {
    if (!original.includes(ref.content)) continue;
    // Replace exact block with `{key}`
    newContent = newContent.replace(ref.content, `{${key}}`);
    modified = true;
  }

  if (modified) {
    fs.writeFileSync(fullPath, newContent, 'utf8');
    return true;
  }
  return false;
}

function main() {
  loadReferences();

  // Get all markdown files except references themselves
  const targets = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === 'workspace-references' || entry.name === 'node_modules' || entry.name.startsWith('.')) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        targets.push(path.relative(ROOT, full));
      }
    }
  }
  walk(ROOT);

  console.log(`Scanning ${targets.length} files for reference blocks...\n`);

  let changed = 0;
  for (const file of targets) {
    if (replaceInFile(file)) {
      console.log(`Updated: ${file}`);
      changed++;
    }
  }

  console.log(`\nTotal files modified: ${changed}`);
}

main();
