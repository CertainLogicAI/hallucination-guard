#!/usr/bin/env node
/**
 * summarize.js — Extractive summarization for memory flush
 *
 * Usage: node scripts/summarize.js < input.md > output.md
 *
 * Strategy:
 * - Preserve all headings (lines starting with #)
 * - Preserve bullet points (lines starting with - or *)
 * - For paragraphs > 200 chars, keep first sentence and truncate to 200 chars + "..."
 * - Keep all lines if file is already < 3000 chars
 */

const fs = require('fs');
const path = require('path');

function summarize(content, maxPara = 200) {
  const lines = content.split('\n');
  const out = [];
  let inList = false;
  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('#')) {
      out.push(line);
      inList = false;
    } else if (trimmed.match(/^[-*]/)) {
      out.push(line);
      inList = true;
    } else if (trimmed === '') {
      out.push(line);
      inList = false;
    } else if (inList) {
      // continuation of list item? keep as-is
      out.push(line);
    } else {
      // Paragraph line
      if (line.length > maxPara) {
        // Keep first sentence (up to first period) then truncate
        const firstPeriod = line.indexOf('.');
        const keep = firstPeriod > 0 ? line.slice(0, firstPeriod + 1) : line.slice(0, maxPara);
        out.push(keep + (keep.length < line.length ? ' ...' : ''));
      } else {
        out.push(line);
      }
    }
  }
  return out.join('\n');
}

function main() {
  const content = fs.readFileSync(0, 'utf8');
  const summarized = summarize(content);
  process.stdout.write(summarized);
}

if (require.main === module) main();
module.exports = { summarize };
