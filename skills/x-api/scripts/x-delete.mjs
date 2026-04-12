#!/usr/bin/env node
// Delete a tweet using OAuth 1.0a User Context
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

const credentials = loadCredentials();
if (!credentials) {
  console.error('❌ No credentials found. Set X_API_* env vars or create x-api.json');
  process.exit(1);
}

const tweetId = process.argv[2];
if (!tweetId) {
  console.error('Usage: x-delete <tweet-id>');
  process.exit(1);
}

const client = new TwitterApi({
  appKey: credentials.consumerKey,
  appSecret: credentials.consumerSecret,
  accessToken: credentials.accessToken,
  accessSecret: credentials.accessTokenSecret,
});

try {
  await client.v2.deleteTweet(tweetId);
  console.log(`✅ Deleted tweet ${tweetId}`);
} catch (err) {
  console.error('❌ Failed:', err.message);
  if (err.data) console.error(JSON.stringify(err.data, null, 2));
  process.exit(1);
}
