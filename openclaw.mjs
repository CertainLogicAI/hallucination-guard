// openclaw.mjs – Deterministic AI Verification Layer
// This preload script ensures:
// 1. All LLM interactions are deterministic
// 2. Responses are cached only after cryptographic verification
// 3. Cache entries are versioned to prevent stale hallucinations

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

// === CONFIGURATION ===
const REDIS_HOST = 'localhost'; // Adjust if Redis runs remotely
const REDIS_PORT = 6379;
const CACHE_KEY_PREFIX = 'openclaw-cache';
const REFERENCE_VERSION_FILE = '/data/.openclaw/workspace/reference_version.json';

// Default security constants
const DEFAULT_HASH_ALGO = 'sha256';

// === UTILITIES ===

// Generate SHA-256 hash of input
function hashContent(content) {
  return crypto.createHash('sha256').update(content).digest('hex');
}

// Generate deterministic cache key
function generateCacheKey(filePath) {
  return `openclaw-cache:${filePath}`;
}

// Load reference version from file (used for cache invalidation)
async function getReferenceVersion() {
  try {
    const raw = await fs.readFile(REFERENCE_VERSION_FILE, 'utf8');
    return JSON.parse(raw).version || '1.0';
  } catch {
    return '1.0';
  }
}

// Cache validation: Check if cached response matches expected reference
async function validateCacheEntry(cacheKey, expectedVersion) {
  const cached = await redis.get(cacheKey);
  if (!cached) return false;
  
  const entry = JSON.parse(cached);
  if (entry.version !== expectedVersion) {
    return false; // Cache entry stale – invalidate
  }
  return true;
}

// ---------------------------
// CORE LOGIC (EXPOSED AS MODULE)
// ---------------------------

class DeterministicCache {
  constructor() {
    this.redis = this.redisAvailable()
      ? require('redis').createClient({ host: 'localhost', port: 6379 })
      : new Map(); // In-memory fallback
  }

  async isRedisAvailable() {
    try {
      // Quick connection test
      await this.redis.ping();
      return true;
    } catch (err) {
      console.log('⚠️ Redis unavailable – using in-memory fallback');
      return false;
    }
  }

  async getFile(path) {
    if (this.redisAvailable()) {
      const key = generateCacheKey(path);
      const cached = await this.redis.get(key);
      if (cached) return JSON.parse(cached);
      const content = await fs.promises.readFile(path, 'utf8');
      await this.redis.set(generateCacheKey(path), JSON.stringify(content));
      return content;
    } else {
      // Fallback: read directly (no caching)
      return await fs.promises.readFile(path, 'utf8');
    }
  }

  async setCache(key, value) {
    if (this.redisAvailable()) {
      await this.redis.set(generateCacheKey(key), JSON.stringify(value));
    }
  }

  // ---------------------------------------------------------
  // 🔒 Core Deterministic Function – For Use in LLM Wrapper
  // ---------------------------------------------------------
  async processResponse(responseContent, referenceVersion) {
    // 1. Compute hash of response
    const computedHash = crypto.createHash('sha256').update(responseContent).digest('hex');

    // 2. Retrieve reference version for this request
    const storedVersion = await redis.get(`reference_version:${responseTraceId}`);
    const storedHash = await redis.get(`hash:${responseTraceId}`);

    // 3. Validate response integrity
    if (computedHash !== storedHash) {
      // FAILURE – Flag for audit/review
      console.error('[CACHE POISONING DETECTED]');
      // In production: log to audit trail & invalidate cache
      return null;
    }

    // 4. Store in cache only if version matches
    const entry = {
      content: responseContent,
      hash: computedHash,
      version: storedVersion,
      timestamp: Date.now()
    };
    
    await this.redis.set(
      generateCacheKey(responseTraceId),
      JSON.stringify(entry)
    );

    return responseContent;
  }
}

// Export for use in OpenClaw's preload system
module.exports = {
  preload: async () => {
    // Trigger cache population on startup
    await populateCriticalFiles();
  }
};

// ---------------------------
// Helper Constants
const REFERENCE_VERSION_FILE = '/data/.openclaw/workspace/reference_version.json';
// -------------------------------------------------------------------------