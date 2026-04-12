#!/usr/bin/env node
// Simple wrapper for embedding-provider.js
const { execSync } = require('child_process');
const fs = require('fs');

// Usage: 
//   node search-wrapper.js index          -> rebuild index
//   node search-wrapper.js search "query" -> perform search
const args = process.argv.slice(2);

if (args[0] === 'index') {
  // Rebuild the index (quietly logs to logs file)
  const logPath = '/data/.openclaw/logs/embedding-index.log';
  const cmd = `date "+%Y-%m-%d %H:%M:%S" >> ${logPath} && node /data/.openclaw/embedding-provider.js index >> ${logPath} 2>&1`;
  execSync(cmd);
  console.log('Index rebuilt – see /data/.openclaw/logs/embedding-index.log');
} else if (args[0] === 'search') {
  if (args.length < 2) {
    console.error('Usage: search-wrapper.js search "<query>"');
    process.exit(1);
  }
  const query = args.slice(1).join(' ');
  const result = execSync(`node /data/.openclaw/embedding-provider.js search "${query}"`, { encoding: 'utf8' });
  console.log(result);
} else {
  console.error('Usage: search-wrapper.js {index|search "<query>"}');
  process.exit(1);
}
