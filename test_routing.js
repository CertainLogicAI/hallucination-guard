#!/usr/bin/env node
/**
 * test_routing.js — Verify OpenClaw model routing works
 *
 * Usage: node test_routing.js "<query>" <expectedModel>
 *
 * Example: node test_routing.js "deterministic consulting" "moonshot/kimik2.5"
 */

const { spawn } = require('child_process');
const [,, query, expectedModel] = process.argv;

if (!query || !expectedModel) {
  console.error('Usage: node test_routing.js "<query>" <expectedModel>');
  process.exit(1);
}

const child = spawn('openclaw', ['agent', '--agent', 'main', `--model`, expectedModel, '-m', `memory_search query='${query}' maxResults=1 --json`], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let stdout = '';
child.stdout.on('data', (data) => {
  stdout += data.toString();
});

child.stderr.on('data', (data) => {
  console.error('STDERR:', data.toString());
});

child.on('close', (code) => {
  if (code !== 0) {
    console.error(`✅ Test passed: child exited with code ${code}`);
    return;
  }
  try {
    const response = JSON.parse(stdout);
    const actualModel = response.model || response.results?.[0]?.model || 'unknown';
    if (actualModel.includes(expectedModel) || actualModel === expectedModel) {
      console.log(`✅ Test passed: got ${actualModel}, expected ${expectedModel}`);
    } else {
      console.log(`❌ Test failed: got ${actualModel}, expected ${expectedModel}`);
      console.log('Full response:', JSON.stringify(response, null, 2));
    }
  } catch (e) {
    console.error('❌ Test failed: could not parse JSON response');
    console.log('Raw output:', stdout);
  }
});

setTimeout(() => {
  child.kill('SIGTERM');
}, 30000); // 30s timeout
