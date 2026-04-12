#!/usr/bin/env node
/**
 * memory-query-cache.js — Simple persistent cache for memory_search results
 *
 * Usage as a module:
 *   const cache = require('./memory-query-cache.js');
 *   const key = cache.makeKey(query, opts);
 *   let results = cache.get(key);
 *   if (!results) { results = await doSearch(...); cache.set(key, results); }
 *
 * Storage: workspace/memory-query-cache.json
 * TTL: 24 hours (configurable)
 */

const fs = require('fs');
const path = require('path');

const CACHE_FILE = path.resolve('/data/.openclaw/workspace/memory-query-cache.json');
const TTL_MS = 24 * 60 * 60 * 1000; // 1 day

function loadCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const raw = fs.readFileSync(CACHE_FILE, 'utf8');
      return JSON.parse(raw);
    }
  } catch (e) {
    console.warn(`memory-query-cache: failed to load: ${e.message}`);
  }
  return {};
}

function saveCache(cache) {
  try {
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2), 'utf8');
  } catch (e) {
    console.warn(`memory-query-cache: failed to save: ${e.message}`);
  }
}

function makeKey(query, opts = {}) {
  // Normalize: trim query, lower-case, sort opts keys
  const q = query.trim().toLowerCase();
  const max = opts.maxResults ?? 5;
  const min = opts.minScore ?? 0.1;
  return `q=${encodeURIComponent(q)}|max=${max}|min=${min}`;
}

function isStale(entry) {
  if (!entry.ts) return true;
  return (Date.now() - entry.ts) > TTL_MS;
}

function get(cache, key) {
  const entry = cache[key];
  if (!entry) return null;
  if (isStale(entry)) {
    delete cache[key];
    return null;
  }
  return entry.results;
}

function set(cache, key, results) {
  cache[key] = {
    results,
    ts: Date.now()
  };
  // Periodic save could be deferred; for simplicity, save every set
  saveCache(cache);
}

// Self-test when run directly
if (require.main === module) {
  const cache = loadCache();
  const testKey = makeKey('token optimization', { maxResults: 3 });
  console.log('Test key:', testKey);
  console.log('Cache size:', Object.keys(cache).length);
  set(cache, testKey, [{ source: 'test.md', snippet: 'example' }]);
  console.log('After set:', get(cache, testKey));
}

module.exports = { loadCache, saveCache, makeKey, get, set, TTL_MS };
