const express = require('express');
const router = express.Router();
const { analyzeL5XBuffer } = require('../analyzer');

/**
 * POST /api/v1/analyze
 * Analyze an L5X file and return JSON report
 *
 * Expects multipart/form-data with field 'file' (.l5x)
 */
router.post('/analyze', async (req, res, next) => {
  try {
    const file = req.file;

    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Optional: force cache bypass via query ?force=1
    const useCache = !(req.query.force === '1');

    // Run analysis with caching
    const report = await analyzeL5XBuffer(file.buffer, { useCache });

    // Add request metadata
    report.metadata.requestId = req.headers['x-request-id'] || null;
    report.metadata.ip = req.apiKey ? 'masked' : req.ip;

    res.json(report);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
