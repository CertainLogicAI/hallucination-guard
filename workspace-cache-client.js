#!/usr/bin/env node
/**
 * Workspace Cache Preloader — Monkey-patches memory access for token efficiency
 *
 * Usage: set NODE_OPTIONS="--require /data/.openclaw/workspace/workspace-cache-client.js"
 *
 * This module runs at startup and:
 * 1. Loads workspace-cache.json into memory
 * 2. Patches memory_get to check cache first (avoid file reads when possible)
 * 3. Adds global.getRelevantFiles(tags) helper for agents
 * 4. Provides LLM response cache (Redis if available)
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = '/data/.openclaw/workspace';
const CACHE_PATH = path.join(ROOT, 'workspace-cache.json');

let cache = null;
let redisClient = null;
let llmCacheEnabled = false;

function loadCache() {
  if (cache) return cache;
  try {
    const raw = fs.readFileSync(CACHE_PATH, 'utf8');
    cache = JSON.parse(raw);
    console.log(`[WorkspaceCache] Loaded ${cache.files.length} files, ${cache.references.length} references`);
    initLLMCache();
    return cache;
  } catch (err) {
    console.error('[WorkspaceCache] Failed to load cache:', err.message);
    return null;
  }
}

/**
 * Initialize LLM response cache (Redis if available, else in-memory)
 */
function initLLMCache() {
  try {
    const Redis = require('ioredis');
    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
    redisClient = new Redis(redisUrl);
    redisClient.on('connect', () => {
      console.log('[LLMCache] Redis connected');
      llmCacheEnabled = true;
    });
    redisClient.on('error', (err) => {
      console.error('[LLMCache] Redis error:', err.message);
      llmCacheEnabled = false;
    });
    // Quick ping
    redisClient.ping().catch(() => {
      console.log('[LLMCache] Redis ping failed, falling back to in-memory');
      llmCacheEnabled = false;
    });
  } catch (e) {
    console.log('[LLMCache] Redis not available, using in-memory cache');
    llmCacheEnabled = false;
  }
}

/**
 * Generate cache key from LLM inputs
 */
function llmCacheKey(model, messages, options = {}) {
  const payload = JSON.stringify({ model, messages, options });
  return 'llm:' + crypto.createHash('sha256').update(payload).digest('hex');
}

/**
 * Get cached LLM response
 * @param {string} model
 * @param {Array} messages
 * @param {Object} options
 * @returns {Promise<{cached: boolean, response?: any, usage?: any}>}
 */
async function getCachedLLMResponse(model, messages, options = {}) {
  if (!llmCacheEnabled && !global.__llmMemoryCache) {
    global.__llmMemoryCache = new Map();
  }
  const key = llmCacheKey(model, messages, options);

  if (llmCacheEnabled) {
    try {
      const cached = await redisClient.get(key);
      if (cached) {
        const parsed = JSON.parse(cached);
        return { cached: true, response: parsed.response, usage: parsed.usage };
      }
    } catch (err) {
      // fall through to memory
    }
  }

  // In-memory fallback
  if (global.__llmMemoryCache) {
    const mem = global.__llmMemoryCache.get(key);
    if (mem) return { cached: true, response: mem.response, usage: mem.usage };
  }

  return { cached: false };
}

/**
 * Store LLM response in cache
 */
async function setCachedLLMResponse(model, messages, options = {}, response, usage) {
  const key = llmCacheKey(model, messages, options);
  const value = JSON.stringify({ response, usage, timestamp: Date.now() });

  if (llmCacheEnabled) {
    try {
      // TTL 24 hours
      await redisClient.setex(key, 86400, value);
    } catch (err) {
      // fallback to memory
      global.__llmMemoryCache.set(key, { response, usage });
    }
  } else {
    global.__llmMemoryCache.set(key, { response, usage });
  }
}

/**
 * Clear LLM cache (dev only)
 */
async function clearLLMCache() {
  if (llmCacheEnabled) {
    await redisClient.del('llm:*'); // careful: this deletes all keys with pattern
  } else {
    global.__llmMemoryCache?.clear();
  }
}

/**
 * Get file paths whose read_when tags intersect with the provided tags
 * @param {string[]} tags
 * @returns {string[]} matching file paths (relative to workspace)
 */
function getRelevantFiles(tags) {
  const c = loadCache();
  if (!c) return [];
  const matches = new Set();
  for (const tag of tags) {
    const list = c.index[tag] || [];
    list.forEach(p => matches.add(p));
  }
  return Array.from(matches);
}

/**
 * Get summary for a file quickly without reading it
 */
function getFileSummary(filePath) {
  const c = loadCache();
  if (!c) return null;
  const entry = c.files.find(f => f.path === filePath);
  return entry ? entry.summary : null;
}

/**
 * Get reference content by key
 */
function getReference(key) {
  const c = loadCache();
  if (!c) return null;
  const ref = c.references.find(r => r.key === key);
  return ref ? ref.content : null;
}

// Expose to global scope (agents can call these)
global.getRelevantFiles = getRelevantFiles;
global.getFileSummary = getFileSummary;
global.getReference = getReference;
global.getCachedLLMResponse = getCachedLLMResponse;
global.setCachedLLMResponse = setCachedLLMResponse;
global.clearLLMCache = clearLLMCache;

// Initialize at startup
loadCache();

module.exports = {
  getRelevantFiles,
  getFileSummary,
  getReference,
  getCachedLLMResponse,
  setCachedLLMResponse,
  clearLLMCache,
  loadCache
};
