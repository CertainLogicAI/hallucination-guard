#!/usr/bin/env bash
# Post a tweet via X API v2
# Usage: ./tweet.sh "Your tweet text here"
# Optional: ./tweet.sh "Reply text" --reply-to <tweet_id>

set -uo pipefail

TEXT="${1:?Usage: tweet.sh \"Your tweet text\" [--reply-to <tweet_id>]}"
REPLY_TO=""

if [ "${2:-}" = "--reply-to" ] && [ -n "${3:-}" ]; then
  REPLY_TO="${3}"
fi

if [ ${#TEXT} -gt 280 ]; then
  echo "❌ Tweet is ${#TEXT} chars (max 280)"
  exit 1
fi

BODY=""
if [ -n "$REPLY_TO" ]; then
  BODY=$(node -e "console.log(JSON.stringify({text: process.argv[1], reply: {in_reply_to_tweet_id: process.argv[2]}}))" "$TEXT" "$REPLY_TO")
else
  BODY=$(node -e "console.log(JSON.stringify({text: process.argv[1]}))" "$TEXT")
fi

RESULT=$(node -e "
const crypto = require('crypto');
const https = require('https');
const config = require('/data/.openclaw/secrets/x-api.json');

function oauthSign(method, url) {
  const oauth = {
    oauth_consumer_key: config.api_key,
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: config.access_token,
    oauth_version: '1.0'
  };
  const paramString = Object.keys(oauth).sort()
    .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(oauth[k]))
    .join('&');
  const baseString = method + '&' + encodeURIComponent(url) + '&' + encodeURIComponent(paramString);
  const signingKey = encodeURIComponent(config.api_secret) + '&' + encodeURIComponent(config.access_token_secret);
  const signature = crypto.createHmac('sha1', signingKey).update(baseString).digest('base64');
  oauth.oauth_signature = signature;
  return 'OAuth ' + Object.keys(oauth).sort()
    .map(k => encodeURIComponent(k) + '=\"' + encodeURIComponent(oauth[k]) + '\"')
    .join(', ');
}

const body = process.argv[1];
const url = 'https://api.x.com/2/tweets';
const auth = oauthSign('POST', url);

const req = https.request({
  hostname: 'api.x.com', path: '/2/tweets', method: 'POST',
  headers: { 'Authorization': auth, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
}, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    if (res.statusCode === 201) {
      const parsed = JSON.parse(data);
      console.log('OK|' + parsed.data.id + '|' + parsed.data.text);
    } else {
      console.log('ERR|' + res.statusCode + '|' + data);
    }
  });
});
req.write(body);
req.end();
" "$BODY" 2>&1)

IFS='|' read -r STATUS ID MSG <<< "$RESULT"

if [ "$STATUS" = "OK" ]; then
  echo "✅ Posted: https://x.com/4cryptoclearly/status/$ID"
  echo "   $MSG"
else
  echo "❌ Failed (HTTP $ID): $MSG"
fi
