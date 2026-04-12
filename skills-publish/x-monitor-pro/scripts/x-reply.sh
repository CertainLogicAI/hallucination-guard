#!/usr/bin/env bash
# X Reply — post a reply to a specific tweet
# Usage: ./x-reply.sh <tweet_id> "Your reply text"

set -uo pipefail

TWEET_ID="${1:?Usage: x-reply.sh <tweet_id> \"reply text\"}"
TEXT="${2:?Missing reply text}"
SECRETS="/data/.openclaw/secrets/x-api.json"

if [ ${#TEXT} -gt 280 ]; then
  echo "❌ Reply is ${#TEXT} chars (max 280)"
  exit 1
fi

RESULT=$(node -e "
const crypto = require('crypto');
const https = require('https');
const config = require('$SECRETS');

function oauthSign(method, url) {
  const oauth = {
    oauth_consumer_key: config.api_key,
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: config.access_token,
    oauth_version: '1.0'
  };
  const allParams = { ...oauth };
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

const body = JSON.stringify({
  text: process.argv[1],
  reply: { in_reply_to_tweet_id: process.argv[2] }
});

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
      const p = JSON.parse(data);
      console.log('OK|' + p.data.id);
    } else {
      console.log('ERR|' + res.statusCode + '|' + data);
    }
  });
});
req.write(body);
req.end();
" "$TEXT" "$TWEET_ID" 2>&1)

IFS='|' read -r STATUS ID REST <<< "$RESULT"

if [ "$STATUS" = "OK" ]; then
  echo "✅ Reply posted: https://x.com/4cryptoclearly/status/$ID"
else
  echo "❌ Failed (HTTP $ID): $REST"
fi
