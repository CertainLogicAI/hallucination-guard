#!/usr/bin/env node
/**
 * Workspace Frontmatter Audit & Standardization
 *
 * Scans all .md files in workspace (excluding node_modules) and:
 * - Detects if file has proper YAML frontmatter (starts with `---` then YAML then `---`)
 * - Reports files missing frontmatter
 * - For files with malformed frontmatter, suggests fix
 *
 * Usage: node audit-frontmatter.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const EXCLUDE_DIRS = ['node_modules', '.git', 'artifacts/original']; // extend as needed

function hasFrontmatter(content) {
  // Check if starts with '---\n' and has another '---\n' within first 50 lines
  const lines = content.split('\n');
  if (lines[0].trim() !== '---') return false;
  for (let i = 1; i < Math.min(50, lines.length); i++) {
    if (lines[i].trim() === '---') return true;
  }
  return false;
}

function extractFrontmatter(content) {
  const lines = content.split('\n');
  if (lines[0].trim() !== '---') return null;
  let end = 1;
  while (end < lines.length && lines[end].trim() !== '---') end++;
  if (end >= lines.length) return null; // malformed
  const fm = lines.slice(1, end).join('\n');
  const body = lines.slice(end + 1).join('\n');
  return { fm, body };
}

function auditFile(filePath) {
  const fullPath = path.join(ROOT, filePath);
  const content = fs.readFileSync(fullPath, 'utf8');
  const hasFM = hasFrontmatter(content);

  if (hasFM) {
    const { fm } = extractFrontmatter(content);
    const hasSummary = /summary:/.test(fm);
    const hasReadWhen = /read_when:/.test(fm);
    return { filePath, hasFrontmatter: true, hasSummary, hasReadWhen };
  } else {
    return { filePath, hasFrontmatter: false, hasSummary: false, hasReadWhen: false };
  }
}

function shouldExclude(dir) {
  return EXCLUDE_DIRS.some(ex => dir.includes(ex));
}

function getAllMarkdownFiles() {
  const files = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (shouldExclude(full)) continue;
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md')) {
        files.push(path.relative(ROOT, full));
      }
    }
  }
  walk(ROOT);
  return files;
}

function main() {
  const files = getAllMarkdownFiles();
  console.log(`Auditing ${files.length} markdown files...\n`);

  const results = {
    total: files.length,
    withFrontmatter: 0,
    missingSummary: [],
    missingReadWhen: [],
    noFrontmatter: []
  };

  for (const file of files) {
    const audit = auditFile(file);
    if (audit.hasFrontmatter) {
      results.withFrontmatter++;
      if (!audit.hasSummary) results.missingSummary.push(file);
      if (!audit.hasReadWhen) results.missingReadWhen.push(file);
    } else {
      results.noFrontmatter.push(file);
    }
  }

  console.log('Results:');
  console.log(`  Total files: ${results.total}`);
  console.log(`  With frontmatter: ${results.withFrontmatter}`);
  console.log(`  Missing frontmatter: ${results.noFrontmatter.length}`);
  console.log(`  Frontmatter missing summary: ${results.missingSummary.length}`);
  console.log(`  Frontmatter missing read_when: ${results.missingReadWhen.length}`);

  if (results.noFrontmatter.length > 0) {
    console.log('\nFiles lacking frontmatter (sample 10):');
    results.noFrontmatter.slice(0, 10).forEach(f => console.log('  -', f));
    if (results.noFrontmatter.length > 10) console.log(`  ...and ${results.noFrontmatter.length - 10} more`);
  }

  if (results.missingSummary.length > 0) {
    console.log('\nFrontmatter missing summary (sample 10):');
    results.missingSummary.slice(0, 10).forEach(f => console.log('  -', f));
  }

  if (results.missingReadWhen.length > 0) {
    console.log('\nFrontmatter missing read_when (sample 10):');
    results.missingReadWhen.slice(0, 10).forEach(f => console.log('  -', f));
  }

  // Write results to JSON for next steps
  fs.writeFileSync(path.join(ROOT, 'frontmatter-audit.json'), JSON.stringify(results, null, 2));
  console.log('\nDetailed report saved to frontmatter-audit.json');
}

main();
