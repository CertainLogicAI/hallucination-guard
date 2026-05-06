#!/usr/bin/env node
// Post to X from a file
import { TwitterApi } from 'twitter-api-v2';
import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

function loadCredentials() {
  if (process.env.X_API_KEY && process.env.X_ACCESS_TOKEN) {
    return {
      consumerKey: process.env.X_API_KEY,
      consumerSecret: process.env.X_API_SECRET,
      accessToken: process.env.X_ACCESS_TOKEN,
      accessTokenSecret: process.env.X_ACCESS_SECRET,
    };
  }
  const configPaths = [
    join(homedir(), '.clawdbot', 'secrets', 'x-api.json'),
    join(process.cwd(), '.x-api.json'),
    join('/data/.openclaw/secrets', 'x-api.json'),
  ];
  for (const configPath of configPaths) {
    if (existsSync(configPath)) {
      try {
        return JSON.parse(readFileSync(configPath, 'utf8'));
      } catch (e) {
        console.error(`❌ Failed to parse ${configPath}:`, e.message);
      }
    }
  }
  return null;
}

function mapCredentials(raw) {
  // Handle different key formats
  return {
    consumerKey: raw.consumerKey || raw.api_key,
    consumerSecret: raw.consumerSecret || raw.api_secret,
    accessToken: raw.accessToken || raw.access_token,
    accessTokenSecret: raw.accessTokenSecret || raw.access_token_secret,
  };
}

const rawCreds = loadCredentials();
if (!rawCreds) {
  console.error('❌ No credentials found.');
  process.exit(1);
}

const credentials = mapCredentials(rawCreds);
const missing = Object.entries(credentials).filter(([k,v]) => !v);
if (missing.length > 0) {
  console.error('❌ Missing credentials:', missing.map(([k]) => k).join(', '));
  process.exit(1);
}

const client = new TwitterApi({
  appKey: credentials.consumerKey,
  appSecret: credentials.consumerSecret,
  accessToken: credentials.accessToken,
  accessSecret: credentials.accessTokenSecret,
});

const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: x-post-file <path-to-tweet-text>');
  process.exit(1);
}

try {
  const text = readFileSync(filePath, 'utf8').trim();
  const { data } = await client.v2.tweet(text);
  console.log(`✅ Posted: https://x.com/i/status/${data.id}`);
} catch (err) {
  console.error('❌ Failed:', err.message);
  if (err.data) console.error(JSON.stringify(err.data, null, 2));
  process.exit(1);
}
