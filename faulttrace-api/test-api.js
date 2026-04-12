#!/usr/bin/env node
/**
 * Test script for FaultTrace API
 * Usage: npm test (configure in package.json later)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const API_URL = process.env.API_URL || 'http://localhost:3000';

function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    const fileName = path.basename(filePath);
    const boundary = '----FormBoundary' + Math.random().toString(36);
    const CRLF = '\r\n';

    const body = Buffer.concat([
      Buffer.from(`--${boundary}${CRLF}`),
      Buffer.from(`Content-Disposition: form-data; name="file"; filename="${fileName}"${CRLF}`),
      Buffer.from(`Content-Type: application/octet-stream${CRLF}${CRLF}`),
      fs.readFileSync(filePath),
      Buffer.from(`${CRLF}--${boundary}--${CRLF}`)
    ]);

    const options = {
      method: 'POST',
      hostname: 'localhost',
      port: 3000,
      path: '/api/v1/analyze',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json);
        } catch (e) {
          resolve({ statusCode: res.statusCode, raw: data });
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Quick manual test
if (require.main === module) {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('Usage: node test-api.js <path-to-l5x-file>');
    process.exit(1);
  }

  uploadFile(filePath)
    .then(result => {
      if (result.statusCode) {
        console.error(`HTTP ${result.statusCode}:`, result.raw);
      } else {
        console.log(JSON.stringify(result, null, 2));
      }
    })
    .catch(err => {
      console.error('Request failed:', err.message);
      process.exit(1);
    });
}

module.exports = { uploadFile };
