#!/usr/bin/env bash
# X Mentions Monitor — fetches recent mentions and filters by account quality
# Usage: ./x-mentions.sh
# Outputs filtered mentions to stdout and saves state to workspace/artifacts/x-mentions-state.json

set -uo pipefail

STATE_FILE="/data/.openclaw/workspace/artifacts/x-mentions-state.json"
SECRETS="/data/.openclaw/secrets/x-api.json"
USER_ID="1549638180827271169"

mkdir -p "$(dirname "$STATE_FILE")"

# Get last seen mention ID
SINCE_ID=""
if [ -f "$STATE_FILE" ]; then
  SINCE_ID=$(node -e "try{console.log(JSON.parse(require('fs').readFileSync('$STATE_FILE','utf8')).lastMentionId||'')}catch(e){console.log('')}")
fi

# Fetch mentions
RESULT=$(node -e "
const crypto = require('crypto');
const https = require('https');
const config = require('$SECRETS');

function oauthSign(method, url, params) {
  const oauth = {
    oauth_consumer_key: config.api_key,
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: config.access_token,
    oauth_version: '1.0'
  };
  const allParams = { ...oauth, ...params };
  const paramString = Object.keys(allParams).sort()
    .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(allParams[k]))
    .join('&');
  const baseString = method + '&' + encodeURIComponent(url) + '&' + encodeURIComponent(paramString);
  const signingKey = encodeURIComponent(config.api_secret) + '&' + encodeURIComponent(config.access_token_secret);
  const signature = crypto.createHmac('sha1', signingKey).update(baseString).digest('base64');
  oauth.oauth_signature = signature;
  return 'OAuth ' + Object.keys(oauth).sort()
    .map(k => encodeURIComponent(k) + '=\"' + encodeURIComponent(oauth[k]) + '\"')
    .join(', ');
}

const params = {
  'tweet.fields': 'created_at,author_id,text',
  'expansions': 'author_id',
  'user.fields': 'public_metrics,created_at,description,profile_image_url',
  'max_results': '20'
};

const sinceId = process.argv[1];
if (sinceId) params.since_id = sinceId;

const queryString = Object.keys(params)
  .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
  .join('&');

const url = 'https://api.x.com/2/users/$USER_ID/mentions';
const auth = oauthSign('GET', url, params);

const options = {
  hostname: 'api.x.com',
  path: '/2/users/$USER_ID/mentions?' + queryString,
  method: 'GET',
  headers: { 'Authorization': auth }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(JSON.stringify({status: res.statusCode, body: JSON.parse(data)})));
});
req.on('error', e => console.error(JSON.stringify({error: e.message})));
req.end();
" "$SINCE_ID" 2>&1)

STATUS=$(echo "$RESULT" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.status||'error')")

if [ "$STATUS" != "200" ]; then
  echo "❌ API error (status $STATUS)"
  echo "$RESULT" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(JSON.stringify(d.body,null,2))" 2>/dev/null
  exit 1
fi

# Process and filter mentions
echo "$RESULT" | node -e "
const fs = require('fs');
const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const body = input.body;

if (!body.data || body.data.length === 0) {
  console.log('NO_MENTIONS');
  process.exit(0);
}

// Build user lookup
const users = {};
if (body.includes && body.includes.users) {
  body.includes.users.forEach(u => { users[u.id] = u; });
}

const now = Date.now();
const thirtyDaysMs = 30 * 24 * 60 * 60 * 1000;

const results = [];

body.data.forEach(tweet => {
  const user = users[tweet.author_id] || {};
  const metrics = user.public_metrics || {};
  const followers = metrics.followers_count || 0;
  const following = metrics.following_count || 0;
  const tweets = metrics.tweet_count || 0;
  const createdAt = user.created_at ? new Date(user.created_at).getTime() : 0;
  const accountAge = now - createdAt;
  const hasBio = !!(user.description && user.description.trim().length > 0);

  // Filters
  const isNewAccount = accountAge < thirtyDaysMs;
  const isSpamRatio = following > 5000 && followers < 100;
  const isBlankProfile = !hasBio;

  // Skip filters
  if (isNewAccount || isSpamRatio) return;

  // Tier assignment
  let tier, action;
  if (followers >= 10000) {
    tier = 'VIP';
    action = 'Reply immediately — HIGH PRIORITY';
  } else if (followers >= 1000) {
    tier = 'WORTH_IT';
    action = 'Draft reply for approval';
  } else if (followers >= 500) {
    tier = 'MAYBE';
    action = 'Reply only if question or positive';
  } else {
    tier = 'SKIP';
    action = 'Skip unless direct question';
  }

  if (tier === 'SKIP' && !tweet.text.includes('?')) return;

  results.push({
    tier,
    action,
    tweetId: tweet.id,
    text: tweet.text,
    createdAt: tweet.created_at,
    user: {
      id: user.id,
      name: user.name,
      username: user.username,
      followers,
      following,
      tweets,
      hasBio
    }
  });
});

// Save newest mention ID
if (body.data.length > 0) {
  const newest = body.data[0].id;
  fs.writeFileSync('$STATE_FILE', JSON.stringify({ lastMentionId: newest, updatedAt: new Date().toISOString() }));
}

if (results.length === 0) {
  console.log('NO_RELEVANT_MENTIONS');
} else {
  console.log(JSON.stringify(results, null, 2));
}
"