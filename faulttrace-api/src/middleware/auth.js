/**
 * API Key Authentication Middleware
 *
 * Validates `Authorization: Bearer <key>` header.
 * Keys are loaded from environment variable ALLOWED_API_KEYS (comma-separated)
 * or from a file `api_keys.txt` (one key per line).
 */

const fs = require('fs');
const path = require('path');

let validKeys = new Set();

function loadApiKeys() {
  const keysFromEnv = process.env.ALLOWED_API_KEYS;
  if (keysFromEnv) {
    keysFromEnv.split(',').forEach(k => validKeys.add(k.trim()));
  }

  // api_keys.txt is in project root (two levels up from this file)
  const keysFile = path.join(__dirname, '../../api_keys.txt');
  if (fs.existsSync(keysFile)) {
    const content = fs.readFileSync(keysFile, 'utf8');
    content.split('\n').forEach(line => {
      const key = line.trim();
      if (key && !key.startsWith('#')) {
        validKeys.add(key);
      }
    });
  }

  if (validKeys.size === 0) {
    console.warn('Auth: No API keys configured. ALLOWED_API_KEYS or api_keys.txt missing. All requests will be rejected.');
  } else {
    console.log(`Auth: Loaded ${validKeys.size} API key(s)`);
  }
}

// Load on module init
loadApiKeys();

/**
 * Middleware: require valid API key
 */
function requireApiKey(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Missing Authorization header' });
  }

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return res.status(401).json({ error: 'Invalid Authorization format. Use: Bearer <key>' });
  }

  const apiKey = parts[1];

  if (!validKeys.has(apiKey)) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  // Attach key to request for logging/metering
  req.apiKey = apiKey;
  next();
}

/**
 * For routes that are public (no auth required)
 */
function optionalAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const parts = authHeader.split(' ');
    if (parts.length === 2 && parts[0] === 'Bearer') {
      const apiKey = parts[1];
      if (validKeys.has(apiKey)) {
        req.apiKey = apiKey;
      }
    }
  }
  next();
}

module.exports = {
  requireApiKey,
  optionalAuth,
  loadApiKeys
};
