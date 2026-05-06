#!/usr/bin/env node
/**
 * search_memory_index.js — Memory search using tag index for efficiency
 *
 * Usage: node scripts/search_memory_index.js "query text" [maxResults=5]
 *
 * Process:
 * 1. Extract candidate tags from query (simple alphanumeric keywords)
 * 2. Look up memory-index.json to find candidate files
 * 3. Read those files, scan for relevant sections (headings, bullet points)
 * 4. Return top matching snippets with source file + line numbers
 *
 * This reduces token usage by avoiding full corpus scans.
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.resolve('/data/.openclaw/workspace/memory');
const INDEX_FILE = path.resolve('/data/.openclaw/workspace/memory-index.json');

function loadIndex() {
  const raw = fs.readFileSync(INDEX_FILE, 'utf8');
  return JSON.parse(raw);
}

function extractKeywords(query) {
  // Very simple: split on non-alphanum, lowercase, remove stopwords
  const stopwords = new Set(['the','is','and','or','what','how','when','why','who','where','a','an','of','to','in','for','with','on','at','by','from','up','about','into','through','during','before','after','above','below','between','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now']);
  return query
    .toLowerCase()
    .split(/[^a-z0-9_]+/)
    .filter(w => w.length > 2 && !stopwords.has(w));
}

function candidateFiles(queryKeywords, index) {
  const fileSet = new Set();
  queryKeywords.forEach(kw => {
    if (index[kw]) {
      index[kw].forEach(f => fileSet.add(f));
    }
  });
  // Also add files tagged "memory" as fallback
  if (fileSet.size === 0 && index['memory']) {
    index['memory'].forEach(f => fileSet.add(f));
  }
  return Array.from(fileSet);
}

function scoreFile(content, keywords) {
  const lower = content.toLowerCase();
  let score = 0;
  keywords.forEach(kw => {
    const regex = new RegExp(kw, 'g');
    const matches = (lower.match(regex) || []).length;
    score += matches;
  });
  return score;
}

function extractSnippets(content, maxSnippets = 3) {
  const lines = content.split('\n');
  const snippets = [];
  let currentHeading = null;
  let buffer = [];
  const flush = () => {
    if (buffer.length > 0) {
      const text = buffer.join('\n').trim();
      if (text.length > 50) {
        snippets.push(text);
      }
      buffer = [];
    }
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Heading detection: starts with '#'
    if (line.startsWith('#')) {
      flush();
      currentHeading = line.slice(1).trim();
      buffer.push(line);
    } else if (line.match(/^[-*] /) && currentHeading) {
      // bullet under a heading
      buffer.push(line);
    } else if (line.trim() === '' && buffer.length > 0) {
      flush();
    } else if (currentHeading) {
      buffer.push(line);
    }
    if (snippets.length >= maxSnippets) break;
  }
  flush();
  return snippets.slice(0, maxSnippets);
}

function search(query, maxResults = 5) {
  const index = loadIndex();
  const keywords = extractKeywords(query);
  if (keywords.length === 0) {
    return { query, results: [], note: 'No keywords extracted' };
  }
  const files = candidateFiles(keywords, index);
  if (files.length === 0) {
    return { query, results: [], note: 'No candidate files found in index' };
  }
  const scored = files.map(file => {
    const fullPath = path.join(MEMORY_DIR, file);
    const content = fs.readFileSync(fullPath, 'utf8');
    const score = scoreFile(content, keywords);
    return { file, content, score };
  }).filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxResults);

  const results = scored.map(item => {
    const snippets = extractSnippets(item.content, 2);
    return {
      source: item.file,
      score: item.score,
      snippets
    };
  });

  return { query, results, keywords };
}

// CLI
if (require.main === module) {
  const [,, query, max] = process.argv;
  if (!query) {
    console.error('Usage: node search_memory_index.js "query" [maxResults]');
    process.exit(1);
  }
  const out = search(query, parseInt(max) || 5);
  console.log(JSON.stringify(out, null, 2));
}

module.exports = { search, extractKeywords, candidateFiles };
