#!/usr/bin/env node
/**
 * Comprehensive test for FaultTrace API
 * Tests: health, auth, rate limiting, file upload
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE_URL || 'http://localhost:9877';
const FIXTURE = path.join(__dirname, 'test/fixtures/sample.l5x');
const VALID_KEY = 'dev-test-key-123';

function request(options, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(options.path, BASE);
    const req = http.request({
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: options.method || 'GET',
      headers: options.headers || {}
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ status: res.statusCode, body: json });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function testHealth() {
  console.log('→ Health check');
  const res = await request({ path: '/health' });
  console.log(`  ${res.status} ${JSON.stringify(res.body)}`);
  return res.status === 200;
}

async function testNoAuth() {
  console.log('→ No auth header');
  const res = await uploadFile(null);
  console.log(`  ${res.status} ${JSON.stringify(res.body)}`);
  return res.status === 401;
}

async function testInvalidAuth() {
  console.log('→ Invalid API key');
  const res = await uploadFile('Bearer invalid-key');
  console.log(`  ${res.status} ${JSON.stringify(res.body)}`);
  return res.status === 401;
}

async function testValidAuth() {
  console.log('→ Valid API key');
  const res = await uploadFile(`Bearer ${VALID_KEY}`);
  console.log(`  ${res.status} issues: ${res.body.issues?.length ?? 0}`);
  return res.status === 200 && Array.isArray(res.body.issues);
}

async function testRateLimitAuth() {
  console.log('→ Rate limit test (authenticated, 5 requests)');
  let passed = true;
  for (let i = 0; i < 5; i++) {
    const res = await uploadFile(`Bearer ${VALID_KEY}`);
    console.log(`  req ${i+1}: ${res.status}`);
    if (res.status !== 200) passed = false;
  }
  // 6th should be 429
  const res6 = await uploadFile(`Bearer ${VALID_KEY}`);
  console.log(`  req 6: ${res6.status} (expected 429)`);
  if (res6.status !== 429) passed = false;
  return passed;
}

function uploadFile(authHeader) {
  const boundary = '----Boundary' + Math.random().toString(36);
  const fileContent = fs.readFileSync(FIXTURE);
  const body = Buffer.concat([
    Buffer.from(`--${boundary}\r\n`),
    Buffer.from('Content-Disposition: form-data; name="file"; filename="sample.l5x"\r\n'),
    Buffer.from('Content-Type: application/octet-stream\r\n\r\n'),
    fileContent,
    Buffer.from(`\r\n--${boundary}--\r\n`)
  ]);

  return request({
    path: '/api/v1/analyze',
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': body.length,
      ...(authHeader && { 'Authorization': authHeader })
    }
  }, body);
}

async function run() {
  console.log('Testing FaultTrace API');
  console.log(`Base URL: ${BASE}\n`);

  try {
    const results = [
      await testHealth(),
      await testNoAuth(),
      await testInvalidAuth(),
      await testValidAuth(),
      await testRateLimitAuth()
    ];

    const allPassed = results.every(Boolean);
    console.log(`\n${allPassed ? '✅ All tests passed' : '❌ Some tests failed'}`);
    process.exit(allPassed ? 0 : 1);
  } catch (err) {
    console.error('Test error:', err.message);
    process.exit(1);
  }
}

run();
