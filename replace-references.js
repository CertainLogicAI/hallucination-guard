#!/usr/bin/env node
/**
 * Reference Replacer — Swap duplicate content for {ref} links
 *
 * Scans all markdown files and replaces known repeated paragraphs with
 * canonical reference placeholders to reduce token burn.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const REFERENCES_DIR = path.join(ROOT, 'workspace-references');

// Map of reference keyword → file path (relative to workspace)
const REF_MAP = {
  faulttrace: 'workspace-references/faulttrace-product.md',
  openclaw: 'workspace-references/openclaw-agents.md',
  'pricing-sub': 'workspace-references/pricing-subscription.md',
  'pricing-usage': 'workspace-references/pricing-usage.md',
  docker: 'workspace-references/docker-deploy.md',
  'llm-cost': 'workspace-references/llm-cost-models.md',
  'api-auth': 'workspace-references/api-auth.md'
};

// Load reference contents (first paragraph or first few lines as signature)
const REF_SIGNATURES = {};
for (const [key, relPath] of Object.entries(REF_MAP)) {
  const fullPath = path.join(ROOT, relPath);
  if (!fs.existsSync(fullPath)) {
    console.error(`Missing reference file: ${relPath}`);
    process.exit(1);
  }
  const content = fs.readFileSync(fullPath, 'utf8');
  // Use first heading + first two paragraphs as signature
  const lines = content.split('\n').filter(l => l.trim());
  const heading = lines.find(l => l.startsWith('# '))?.slice(2).trim() || '';
  const paragraphs = [];
  for (const line of lines) {
    if (line.startsWith('# ')) continue;
    if (line.trim() === '') continue;
    paragraphs.push(line.trim());
    if (paragraphs.length >= 2) break;
  }
  REF_SIGNATURES[key] = {
    heading,
    preview: paragraphs.join(' ').slice(0, 150),
    fullContent: content // keep full reference for potential exact match
  };
}

/**
 * Check if a block of text matches a reference signature.
 * Returns reference key if match, null otherwise.
 */
function matchReference(text) {
  const trimmed = text.trim();
  // Try exact match first (full reference)
  for (const [key, sig] of Object.entries(REF_SIGNATURES)) {
    // Exact match of full content? (rare)
    if (trimmed === sig.fullContent.trim()) return key;
  }

  // Heuristic: heading + first sentence match
  for (const [key, sig] of Object.entries(REF_SIGNATURES)) {
    if (trimmed.includes(sig.heading) && trimmed.includes(sig.preview.slice(0, 50))) {
      return key;
    }
  }
  return null;
}

/**
 * Replace paragraphs in a file with {ref} links where duplicates detected.
 */
function processFile(filePath) {
  const fullPath = path.join(ROOT, filePath);
  const content = fs.readFileSync(fullPath, 'utf8');
  const lines = content.split('\n');

  // We'll rebuild the file, skipping replaced paragraphs
  const newLines = [];
  let i = 0;
  let modified = false;

  // Simple state: accumulate a paragraph (separated by blank lines)
  while (i < lines.length) {
    // Collect paragraph
    let paraStart = i;
    let paraLines = [];
    while (i < lines.length && lines[i].trim() !== '') {
      paraLines.push(lines[i]);
      i++;
    }
    // Include trailing blank line if present
    if (i < lines.length && lines[i].trim() === '') {
      i++; // skip blank
    }
    const paragraph = paraLines.join('\n');

    // Skip tiny paragraphs (headings or short lines)
    if (paragraph.trim().length < 80 || !paragraph.includes(' ')) {
      newLines.push(paragraph);
      continue;
    }

    const refKey = matchReference(paragraph);
    if (refKey) {
      // Replace with reference link
      newLines.push(`{${refKey}}`);
      modified = true;
    } else {
      newLines.push(paragraph);
    }
  }

  if (modified) {
    const newContent = newLines.join('\n');
    return { newContent, modified };
  }
  return null;
}

function main() {
  // Get all markdown files (excluding workspace-references themselves)
  const allFiles = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === 'workspace-references' || entry.name === 'node_modules' || entry.name.startsWith('.')) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        allFiles.push(path.relative(ROOT, full));
      }
    }
  }
  walk(ROOT);

  console.log(`Scanning ${allFiles.length} files for duplicate content...\n`);

  let totalModified = 0;
  for (const file of allFiles) {
    const result = processFile(file);
    if (result) {
      fs.writeFileSync(path.join(ROOT, file), result.newContent, 'utf8');
      console.log(`Replaced in: ${file}`);
      totalModified++;
    }
  }

  console.log(`\nTotal files modified: ${totalModified}`);
  console.log('Next: Review changes; consider adding {ref} links manually for missed duplicates.');
}

main();
