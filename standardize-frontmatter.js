#!/usr/bin/env node
/**
 * Workspace Frontmatter Standardization
 *
 * Adds or completes frontmatter for all markdown files.
 * - Missing frontmatter: prepends new YAML with summary + read_when
 * - Partial frontmatter: adds missing fields
 *
 * Dry-run by default. Use --apply to write changes.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const DRY_RUN = process.argv.includes('--dry-run');
const APPLY = process.argv.includes('--apply');

// From audit
const TARGET_FILES = [
  // ... I'll load from frontmatter-audit.json instead of hardcoding
];

function loadAudit() {
  const auditPath = path.join(ROOT, 'frontmatter-audit.json');
  if (!fs.existsSync(auditPath)) {
    throw new Error('Run frontmatter-audit.js first');
  }
  return JSON.parse(fs.readFileSync(auditPath, 'utf8'));
}

function generateSummary(content, filename) {
  // Try first heading (# Title)
  const headingMatch = content.match(/^#\s+(.+)$/m);
  if (headingMatch) {
    let summary = headingMatch[1].trim();
    if (summary.length > 100) summary = summary.slice(0, 97) + '...';
    return summary;
  }
  // Fallback: first non-empty line (not a heading)
  const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#')).slice(0, 3);
  const firstLine = lines[0] || '';
  let summary = firstLine.trim();
  if (summary.length > 100) summary = summary.slice(0, 97) + '...';
  if (!summary) {
    // Last resort: filename-based title
    summary = filename
      .replace(/\.md$/, '')
      .replace(/[-_]/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }
  return summary;
}

function generateTags(filename, existingReadWhen = null) {
  const tags = new Set();

  // Path-based tags
  if (filename.includes('ideas/')) tags.add('idea');
  if (filename.includes('skills/')) tags.add('skill');
  if (filename.includes('memory/')) tags.add('memory');
  if (filename.includes('workspace/artifacts/')) tags.add('artifact');
  if (filename.includes('faulttrace')) tags.add('faulttrace');
  if (filename.includes('openclaw')) tags.add('openclaw');
  if (filename.includes('agent')) tags.add('agent');
  if (filename.includes('cost') || filename.includes('price')) tags.add('pricing');
  if (filename.includes('llm') || filename.includes('token')) tags.add('llm');
  if (filename.includes('docker')) tags.add('docker');
  if (filename.includes('api')) tags.add('api');

  // Preserve existing read_when tags if provided as array
  if (Array.isArray(existingReadWhen)) {
    existingReadWhen.forEach(t => tags.add(t));
  }

  return Array.from(tags).slice(0, 5); // max 5 tags
}

function ensureFrontmatter(filename, content) {
  const hasFM = content.startsWith('---\n');
  let fm = { summary: '', read_when: [] };
  let body = content;

  if (hasFM) {
    const endIdx = content.indexOf('\n---\n', 4);
    if (endIdx !== -1) {
      const fmStr = content.slice(4, endIdx);
      body = content.slice(endIdx + 5);
      // Parse YAML simply (no full parser, just extract key: value)
      fmStr.split('\n').forEach(line => {
        const m = line.match(/^(\w+):\s*(.+)$/);
        if (m) {
          const key = m[1];
          let val = m[2].trim();
          // Handle arrays (read_when)
          if (val.startsWith('[') && val.endsWith(']')) {
            try {
              val = JSON.parse(val.replace(/'/g, '"'));
            } catch {
              val = val.slice(1, -1).split(',').map(s => s.trim().replace(/^['"]|['"]$/g, ''));
            }
          }
          fm[key] = val;
        }
      });
      // Ensure read_when is array
      if (!Array.isArray(fm.read_when)) fm.read_when = [];
    }
  }

  // Generate/update fields
  if (!fm.summary) fm.summary = generateSummary(body, filename);
  if (!fm.read_when || fm.read_when.length === 0) {
    fm.read_when = generateTags(filename, fm.read_when);
  }

  // Reconstruct frontmatter
  const fmLines = [
    '---',
    `summary: "${fm.summary.replace(/"/g, '\\"')}"`,
    `read_when: [${fm.read_when.map(t => `"${t}"`).join(', ')}]`,
    '---'
  ];

  return fmLines.join('\n') + '\n' + body;
}

function main() {
  const audit = loadAudit();
  const allFiles = [...audit.noFrontmatter, ...audit.missingSummary, ...audit.missingReadWhen];
  const uniqueFiles = [...new Set(allFiles)];

  console.log(`Standardizing frontmatter for ${uniqueFiles.length} files...\n`);

  let changes = 0;
  for (const file of uniqueFiles) {
    const fullPath = path.join(ROOT, file);
    const content = fs.readFileSync(fullPath, 'utf8');
    const newContent = ensureFrontmatter(file, content);

    if (newContent !== content) {
      if (DRY_RUN) {
        console.log(`[DRY] Would update: ${file}`);
      } else if (APPLY) {
        fs.writeFileSync(fullPath, newContent, 'utf8');
        console.log(`Updated: ${file}`);
      }
      changes++;
    }
  }

  if (DRY_RUN) {
    console.log(`\nDry-run complete. ${changes} files would be modified.`);
    console.log('Run with --apply to write changes.');
  } else if (APPLY) {
    console.log(`\nApplied ${changes} changes.`);
  } else {
    console.log('\nNo action taken. Use --dry-run or --apply.');
  }
}

main();
