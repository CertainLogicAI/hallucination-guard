---
summary: "X Monitor Pro"
read_when: ["[]"]
---



# X Monitor Pro

Automated X/Twitter monitoring and engagement system. Watch high-impact accounts, catch relevant posts during peak hours, draft value-adding replies, and track mentions — all from one API call.

## Quick Reference

| Need | Resource |
|------|----------|
| Search watched accounts for new posts | `scripts/x-search.sh` |
| Reply to a specific tweet | `scripts/x-reply.sh <tweet_id> "text"` |
| Post a new tweet | `scripts/tweet.sh "text"` |
| Check who you're monitoring | `references/watchlist.json` |
| Reply quality guidelines | `references/reply-guidelines.md` |
| Check/post mentions | `scripts/x-mentions.sh` |

## Setup

1. X API secrets must exist at `/data/.openclaw/secrets/x-api.json` with:
   - `api_key`, `api_secret`, `access_token`, `access_token_secret`
2. Edit `references/watchlist.json` to add/remove accounts and topics
3. Set up cron jobs for automated monitoring (see below)

## How It Works

### Single API Call Monitoring
Instead of polling each account separately, we build one search query:
```
(from:user1 OR from:user2 OR from:user3) (topic1 OR topic2) -is:retweet -is:reply
```
One call covers all watched accounts. State is saved so we only see new posts.

### Account Tiers
| Tier | Followers | Action |
|------|-----------|--------|
| VIP | 10K+ | Reply immediately — high priority |
| HIGH | 1K-10K | Draft reply for approval |
| MEDIUM | 500-1K | Reply only if directly relevant |

### Peak Hours (EST)
- 8-10 AM — morning scroll
- 12-1 PM — lunch break
- 5-7 PM — after work

Only poll during these windows to minimize API costs.

### Mention Monitoring
Separate from the search — checks who's talking about/to you:
- Filters by follower count, account age, spam signals
- Skips bots, blank profiles, mass-taggers
- Alerts on VIP and WORTH_IT tier mentions only

## Cron Setup

```bash
# Monitor watched accounts — peak hours only (EST)
# 8 AM, 9 AM, 10 AM, 12 PM, 5 PM, 6 PM, 7 PM
openclaw cron add --name "X Monitor" \
  --cron "0 8,9,10,12,17,18,19 * * 1-5" \
  --tz "America/New_York" \
  --session isolated \
  --message "Run x-search.sh, analyze results, draft replies per reply-guidelines.md" \
  --announce --channel telegram

# Mention monitoring — every 30 min during peak
openclaw cron add --name "X Mentions" \
  --cron "*/30 8-10,12-13,17-19 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Run x-mentions.sh, filter and report" \
  --announce --channel telegram
```

## Reply Workflow
1. Cron fires → search script finds new posts
2. Agent reads post content + account tier
3. Agent drafts reply following `references/reply-guidelines.md`
4. Send to Telegram in **two messages**:
   - **Message 1:** Context (link + who + follower count + their post summary)
   - **Message 2:** Clean reply text only (copy-paste ready, no formatting)
5. User copies reply from Telegram → pastes into X manually
6. Once engagement history is established, use `x-reply.sh` for API posting

## Telegram Delivery Format
Always deliver X reply drafts as two separate Telegram messages:

**First message (context):**
```
🎯 @username (123K followers)
"Summary of their post..."
https://x.com/username/status/1234567890
```

**Second message (reply text only — must be standalone, no extra formatting):**
```
Your draft reply here. Clean text only. Ready to long-press, copy, and paste into X.
```

Never combine context and reply in one message — mobile users can't select partial text.

## Rules
- **One reply per account per day max** — don't stalk
- **No links on first reply** — build familiarity first
- **Add value or don't reply** — no "great post!" filler
- **Match their energy** — technical post = technical reply
- **Under 280 chars** — tight and punchy
- **Context first, reply second** — always two Telegram messages
