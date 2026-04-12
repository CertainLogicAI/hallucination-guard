require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const multer = require('multer');
const path = require('path');

const { requireApiKey, optionalAuth } = require('./middleware/auth');
const { trialLimiter, authLimiter } = require('./middleware/rateLimit');
const analyzeRouter = require('./routes/analyze');

const app = express();
// Force port for this app to avoid conflicts with OpenClaw gateway
const PORT = parseInt(process.env.FAULTRACE_PORT) || 9876;

// Security middleware
app.use(helmet());
app.use(cors({ origin: process.env.CORS_ORIGIN || '*' }));

// Health check (public, no rate limit)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Webhooks: need raw body before JSON parser
app.use('/webhooks', express.raw({ type: 'application/json' }), require('./middleware/stripeWebhook'), require('./routes/webhooks'));

// Body parsing for normal routes (after webhooks)
app.use(express.json({ limit: '10mb' }));

// File upload (multipart/form-data)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    if (path.extname(file.originalname).toLowerCase() === '.l5x') {
      cb(null, true);
    } else {
      cb(new Error('Only .l5x files allowed'));
    }
  }
});

// API routes
// rate limiting: apply trial limiter first (IP-based), then auth check, then auth-based limiter
// Note: order matters. We attach both limiters via middleware before route handler.
const apiRouter = require('./routes/analyze');
app.use('/api/v1', trialLimiter, optionalAuth, (req, res, next) => {
  // Apply stricter limit for authenticated users
  if (req.apiKey) {
    return authLimiter(req, res, next);
  }
  // Unauthenticated: already rate-limited by trialLimiter, just continue
  next();
}, requireApiKey, upload.single('file'), apiRouter);

// Global error handler
app.use((err, req, res, next) => {
  console.error('Error:', err.message || err);
  const status = err.name === 'MulterError' ? 400 : 500;
  res.status(status).json({ error: err.message || 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`FaultTrace API listening on port ${PORT}`);
});

module.exports = app;
