/**
 * Redis Cache implementation
 *
 * Provides simple get/set with TTL for analysis results.
 * Keys are hashes of L5X content for deterministic caching.
 */

const Redis = require('ioredis');

const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
const client = new Redis(redisUrl);

let redisReady = false;

client.on('connect', () => {
  console.log('Redis connected');
  redisReady = true;
});

client.on('error', (err) => {
  console.error('Redis error:', err.message);
  redisReady = false;
});

/**
 * Generate a cache key from L5X buffer (SHA256 hash)
 */
function cacheKeyFromBuffer(buffer) {
  const crypto = require('crypto');
  return 'faulttrace:analysis:' + crypto.createHash('sha256').update(buffer).digest('hex');
}

/**
 * Store analysis result in cache
 * @param {Buffer} l5xBuffer - Original file
 * @param {Object} report - Analysis report (JSON-serializable)
 * @param {number} ttlSeconds - Time to live in seconds (default 24h)
 */
async function set(l5xBuffer, report, ttlSeconds = 86400) {
  try {
    const key = cacheKeyFromBuffer(l5xBuffer);
    await client.setex(key, ttlSeconds, JSON.stringify(report));
    return true;
  } catch (err) {
    console.error('Redis set error:', err.message);
    return false;
  }
}

/**
 * Retrieve cached analysis result
 * @param {Buffer} l5xBuffer - Original file
 * @returns {Promise<Object|null>}
 */
async function get(l5xBuffer) {
  try {
    const key = cacheKeyFromBuffer(l5xBuffer);
    const data = await client.get(key);
    return data ? JSON.parse(data) : null;
  } catch (err) {
    console.error('Redis get error:', err.message);
    return null;
  }
}

/**
 * Check if Redis is available
 */
function isReady() {
  return redisReady;
}

/**
 * Flush all cache (dev only)
 */
async function flush() {
  if (process.env.NODE_ENV === 'development') {
    await client.flushdb();
    console.log('Redis cache flushed');
  }
}

module.exports = {
  set,
  get,
  isReady,
  flush
};
