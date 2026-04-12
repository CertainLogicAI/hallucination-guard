#!/usr/bin/env bash
# X Search Monitor — single API call to monitor multiple accounts
# Usage: ./x-search.sh [--dry-run]
# Config: references/watchlist.json
# State: workspace/artifacts/x-monitor-state.json

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WATCHLIST="$SKILL_DIR/references/watchlist.json"
STATE_FILE="/data/.openclaw/workspace/artifacts/x-monitor-state.json"
SECRETS="/data/.openclaw/secrets/x-api.json"

mkdir -p "$(dirname "$STATE_FILE")"

if [ ! -f "$WATCHLIST" ]; then
  echo "❌ Watchlist not found: $WATCHLIST"
  exit 1
fi

if [ ! -f "$SECRETS" ]; then
  echo "❌ X API secrets not found: $SECRETS"
  exit 1
fi

RESULT=$(node -e "
const https = require('https');
const fs = require('fs');

const config = JSON.parse(fs.readFileSync('$SECRETS', 'utf8'));
const watchlist = JSON.parse(fs.readFileSync('$WATCHLIST', 'utf8'));
const stateFile = '$STATE_FILE';

// Step 1: Get bearer token
function getBearerToken() {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(config.api_key + ':' + config.api_secret).toString('base64');
    const body = 'grant_type=client_credentials';
    const req = https.request({
      hostname: 'api.x.com', path: '/oauth2/token', method: 'POST',
      headers: { 'Authorization': 'Basic ' + auth, 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': body.length }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data).access_token));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Step 2: Search
async function run() {
  const bearer = await getBearerToken();

  // Build search query
  const accounts = watchlist.accounts.map(a => 'from:' + a.username).join(' OR ');
  const topics = watchlist.topics || [];
  const topicFilter = topics.length > 0 ? ' (' + topics.join(' OR ') + ')' : '';
  const query = '(' + accounts + ')' + topicFilter + ' -is:retweet -is:reply';

  // Get since_id
  let sinceId = '';
  try { sinceId = JSON.parse(fs.readFileSync(stateFile, 'utf8')).lastSearchId || ''; } catch(e) {}

  const params = new URLSearchParams({
    'query': query,
    'tweet.fields': 'created_at,author_id,public_metrics',
    'expansions': 'author_id',
    'user.fields': 'public_metrics,description,username',
    'max_results': '10'
  });
  if (sinceId) params.set('since_id', sinceId);

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.x.com',
      path: '/2/tweets/search/recent?' + params.toString(),
      method: 'GET',
      headers: { 'Authorization': 'Bearer ' + bearer }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const parsed = JSON.parse(data);
        if (res.statusCode !== 200) {
          console.log(JSON.stringify({ error: true, status: res.statusCode, detail: parsed }));
          return;
        }

        if (!parsed.data || parsed.data.length === 0) {
          console.log(JSON.stringify({ tweets: [], query }));
          return;
        }

        const users = {};
        if (parsed.includes && parsed.includes.users) {
          parsed.includes.users.forEach(u => { users[u.id] = u; });
        }

        const tierMap = {};
        watchlist.accounts.forEach(a => { tierMap[a.username.toLowerCase()] = a; });

        const tweets = parsed.data.map(t => {
          const user = users[t.author_id] || {};
          const username = (user.username || '').toLowerCase();
          const watchEntry = tierMap[username] || {};
          return {
            tweetId: t.id,
            text: t.text,
            createdAt: t.created_at,
            metrics: t.public_metrics,
            user: { id: t.author_id, name: user.name, username: user.username, followers: (user.public_metrics || {}).followers_count || 0 },
            tier: watchEntry.tier || 'UNKNOWN',
            note: watchEntry.note || ''
          };
        });

        const newestId = parsed.data[0].id;
        fs.writeFileSync(stateFile, JSON.stringify({ lastSearchId: newestId, updatedAt: new Date().toISOString(), query }, null, 2));
        console.log(JSON.stringify({ tweets, query }));
      });
    });
    req.on('error', e => console.log(JSON.stringify({ error: true, message: e.message })));
    req.end();
  });
}

run();
" 2>&1)

# Parse and display
echo "$RESULT" | node -e "
const fs = require('fs');
const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));

if (input.error) {
  console.log('❌ API Error:', JSON.stringify(input.detail || input.message));
  process.exit(1);
}

if (!input.tweets || input.tweets.length === 0) {
  console.log('NO_NEW_POSTS');
  console.log('Query: ' + input.query);
  process.exit(0);
}

console.log('📡 Found ' + input.tweets.length + ' new posts from watched accounts:\n');

input.tweets.forEach((t, i) => {
  const tierEmoji = { VIP: '🔥', HIGH: '✅', MEDIUM: '🟡' }[t.tier] || '📌';
  console.log(tierEmoji + ' [' + t.tier + '] @' + t.user.username + ' (' + t.user.followers.toLocaleString() + ' followers)');
  console.log('  Tweet: ' + t.text.substring(0, 200) + (t.text.length > 200 ? '...' : ''));
  console.log('  Engagement: ' + (t.metrics?.like_count||0) + ' likes, ' + (t.metrics?.retweet_count||0) + ' RTs, ' + (t.metrics?.reply_count||0) + ' replies');
  console.log('  ID: ' + t.tweetId);
  if (t.note) console.log('  Note: ' + t.note);
  console.log('');
});
"
