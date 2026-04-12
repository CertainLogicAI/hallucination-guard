/**
 * Analyzer module — wraps FaultTrace static analysis
 *
 * This module provides:
 * - analyzeL5XBuffer: main entry point with caching
 * - setRealAnalyzer: for injecting the real analyzer after porting
 *
 * In production, cache is enabled. In development, cache is disabled by default
 * to ensure you see fresh results while building.
 */

const { NODE_ENV } = process.env;
const cache = require('./cache/redis');

// Will be set by the real analyzer once ported (see PORTING.md)
let realAnalyzer = null;

/**
 * Set the real analyzer function (used after porting)
 * @param {Function} fn - async (buffer) => report
 */
function setRealAnalyzer(fn) {
  realAnalyzer = fn;
}

/**
 * Mock analyzer for development only.
 * Returns deterministic fake data that matches the schema.
 */
async function mockAnalyze(l5xBuffer) {
  return {
    metadata: {
      fileName: 'uploaded.l5x',
      fileSize: l5xBuffer.length,
      analyzerVersion: '0.1.0',
      analyzedAt: new Date().toISOString()
    },
    summary: {
      totalRungs: 1,
      totalTags: 2,
      warnings: 1,
      errors: 0,
      info: 0
    },
    issues: [
      {
        id: 'unused-tag-001',
        severity: 'warning',
        rule: 'UnusedTag',
        message: 'Tag Motor_Start is declared but never used',
        location: { rung: 1, instructionIndex: 3 },
        suggestion: 'Remove declaration or use in logic'
      }
    ],
    ioMap: { inputs: [], outputs: [] },
    tags: [
      { name: 'Motor_Start', type: 'BOOL', used: false },
      { name: 'Motor_Run', type: 'BOOL', used: true }
    ]
  };
}

/**
 * Main entry point: analyze an L5X file with optional caching.
 * @param {Buffer} l5xBuffer - Raw L5X content
 * @param {Object} options - { useCache?: boolean }
 */
async function analyzeL5XBuffer(l5xBuffer, options = {}) {
  const { useCache = NODE_ENV === 'production' } = options;

  if (useCache && cache.isReady()) {
    const cached = await cache.get(l5xBuffer);
    if (cached) {
      console.log('[Cache] HIT');
      return cached;
    }
  }

  let report;
  if (realAnalyzer) {
    console.log('[Analyzer] using real implementation');
    report = await realAnalyzer(l5xBuffer);
  } else if (NODE_ENV === 'development') {
    console.log('[Analyzer] using mock (real analyzer not set)');
    // Simulate some work so we notice it's not instant
    await new Promise(resolve => setTimeout(resolve, 100));
    report = mockAnalyze(l5xBuffer);
  } else {
    throw new Error(
      'Real analyzer not set. Call setRealAnalyzer() with the ported FaultTrace engine before starting server in production.'
    );
  }

  if (useCache && cache.isReady()) {
    await cache.set(l5xBuffer, report, 86400); // 24h TTL
    console.log('[Cache] STORED');
  }

  return report;
}

module.exports = {
  analyzeL5XBuffer,
  setRealAnalyzer
};
