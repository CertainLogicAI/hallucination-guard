const rateLimit = require('express-rate-limit');

/**
 * Rate limiting middleware
 *
 * Two tiers:
 * - Trial/unknown: 10 requests per 15 minutes (aggressive to prevent abuse)
 * - Authenticated (via API key): 100 requests per 15 minutes
 *
 * Configure via RATE_LIMIT_TRIAL and RATE_LIMIT_AUTHED env vars (ms format, e.g. "15m").
 */

const {
  RATE_LIMIT_TRIAL = '15m',
  RATE_LIMIT_AUTHED = '15m'
} = process.env;

const trialLimiter = rateLimit({
  windowMs: parseDuration(RATE_LIMIT_TRIAL),
  max: 10,
  message: { error: 'Too many requests from this IP, please try again later.' },
  standardHeaders: true,
  legacyHeaders: false,
  // By key: IP address (works for unauthenticated requests)
  keyGenerator: (req) => req.ip
});

const authLimiter = rateLimit({
  windowMs: parseDuration(RATE_LIMIT_AUTHED),
  max: 100,
  message: { error: 'API rate limit exceeded, please try again later.' },
  standardHeaders: true,
  legacyHeaders: false,
  // By API key instead of IP, so users don't penalize each other behind NAT
  keyGenerator: (req) => req.apiKey || req.ip
});

/**
 * Parse duration string like "15m", "1h", "30s" into milliseconds
 */
function parseDuration(str) {
  const match = str.match(/^(\d+)([smhd])$/);
  if (!match) {
    console.warn(`Invalid duration format: ${str}, defaulting to 15m`);
    return 15 * 60 * 1000;
  }
  const [, num, unit] = match;
  const n = parseInt(num, 10);
  switch (unit) {
    case 's': return n * 1000;
    case 'm': return n * 60 * 1000;
    case 'h': return n * 60 * 60 * 1000;
    case 'd': return n * 24 * 60 * 60 * 1000;
    default: return 15 * 60 * 1000;
  }
}

module.exports = {
  trialLimiter,
  authLimiter
};
