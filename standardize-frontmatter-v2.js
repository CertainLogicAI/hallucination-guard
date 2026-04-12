#!/usr/bin/env node
/**
 * Workspace Frontmatter Standardization — v2
 *
 * Preserves existing frontmatter intact. Only injects missing fields.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const DRY_RUN = process.argv.includes('--dry-run');
const APPLY = process.argv.includes('--apply');

function loadAudit() {
  const auditPath = path.join(ROOT, 'frontmatter-audit.json');
  if (!fs.existsSync(auditPath)) {
    throw new Error('Run frontmatter-audit.js first');
  }
  return JSON.parse(fs.readFileSync(auditPath, 'utf8'));
}

function inferSummary(content, filename) {
  // First heading
  const m = content.match(/^#\s+(.+)$/m);
  if (m) {
    let s = m[1].trim();
    if (s.length > 100) s = s.slice(0, 97) + '...';
    return s;
  }
  // First non-empty non-heading line
  const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
  if (lines.length) {
    let s = lines[0].trim();
    if (s.length > 100) s = s.slice(0, 97) + '...';
    return s;
  }
  // Filename fallback
  return filename.replace(/\.md$/, '').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function inferTags(filename) {
  const tags = new Set();
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
  // Cap at 5 tags
  return Array.from(tags).slice(0, 5);
}

function needsFrontmatter(content) {
  return !content.startsWith('---\n');
}

function parseFrontmatterBlock(content) {
  const end = content.indexOf('\n---\n', 4);
  if (end === -1) return null;
  return {
    block: content.slice(0, end + 5), // includes trailing newline after closing ---
    body: content.slice(end + 5)
  };
}

function hasField(fmBlock, field) {
  const regex = new RegExp(`^${field}:`, 'm');
  return regex.test(fmBlock);
}

function injectField(fmBlock, field, value) {
  // Insert after opening --- line
  const lines = fmBlock.split('\n');
  const insertIdx = lines.findIndex(l => l.trim() === '---');
  if (insertIdx === -1) return fmBlock;
  const indent = ' ';
  const newLine = `${indent}${field}: "${value}"`;
  lines.splice(insertIdx + 1, 0, newLine);
  return lines.join('\n') + '\n';
}

function main() {
  const audit = loadAudit();
  const allFiles = [...new Set([...audit.noFrontmatter, ...audit.missingSummary, ...audit.missingReadWhen])];
  console.log(`Standardizing frontmatter for ${allFiles.length} files...\n`);

  let changes = 0;
  for (const file of allFiles) {
    const fullPath = path.join(ROOT, file);
    const content = fs.readFileSync(fullPath, 'utf8');
    let newContent = content;

    if (needsFrontmatter(content)) {
      // Add entirely new frontmatter
      const summary = inferSummary(content, file);
      const tags = inferTags(file);
      const fm = [
        '---',
        `summary: "${summary.replace(/"/g, '\\"')}"`,
        `read_when: [${tags.map(t => `"${t}"`).join(', ')}]`,
        '---',
        ''
      ].join('\n');
      newContent = fm + content;
    } else {
      // Existing frontmatter: inject missing fields
      const parsed = parseFrontmatterBlock(content);
      if (!parsed) {
        console.warn(`Malformed frontmatter in ${file}, skipping`);
        continue;
      }
      let fmBlock = parsed.block;
      let modified = false;

      if (!hasField(fmBlock, 'summary')) {
        const summary = inferSummary(parsed.body, file);
        fmBlock = injectField(fmBlock, 'summary', summary);
        modified = true;
      }

      if (!hasField(fmBlock, 'read_when')) {
        const tags = inferTags(file);
        const readWhenLine = `read_when: [${tags.map(t => `"${t}"`).join(', ')}]`;
        // Insert after summary if present, else after opening ---
        const lines = fmBlock.split('\n');
        const insertIdx = lines.findIndex(l => l.trim() === '---') + 1;
        lines.splice(insertIdx, 0, readWhenLine);
        fmBlock = lines.join('\n') + '\n';
        modified = true;
      }

      if (modified) {
        newContent = fmBlock + parsed.body;
      }
    }

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
