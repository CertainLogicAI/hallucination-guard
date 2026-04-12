---
summary: "\"OpenClaw Update Rollback Plan\""
read_when: ["["idea", "openclaw"]"]
---
# OpenClaw Update Rollback Plan

## Current State (working)
- **Version:** 2026.3.12 (6472949)
- **Package path:** /usr/local/lib/node_modules/openclaw
- **Binary:** /usr/local/bin/openclaw → ../lib/node_modules/openclaw/openclaw.mjs
- **Node:** v22.22.1
- **Target:** 2026.3.23-2

## Before Update
```bash
# 1. Backup current install
cp -r /usr/local/lib/node_modules/openclaw /data/.openclaw/openclaw-backup-2026.3.12

# 2. Save current config
cp /data/.openclaw/openclaw.json /data/.openclaw/openclaw.json.bak

# 3. Stop gateway
openclaw gateway stop
```

## Update
```bash
# 4. Install update
npm install -g openclaw@latest

# 5. Restart gateway
openclaw gateway start

# 6. Verify
openclaw --version
openclaw gateway status
# Send a test message via Telegram
```

## Verify Checklist
- [ ] `openclaw --version` shows new version
- [ ] `openclaw gateway status` shows running
- [ ] Telegram bot responds
- [ ] Cron list works (`openclaw cron list`)
- [ ] ANTHROPIC_MODEL_ALIASES error gone?
- [ ] Config reads without error

## Rollback (if broken)
```bash
# Stop gateway
openclaw gateway stop

# Remove broken version
rm -rf /usr/local/lib/node_modules/openclaw

# Restore backup
cp -r /data/.openclaw/openclaw-backup-2026.3.12 /usr/local/lib/node_modules/openclaw

# Restore config if changed
cp /data/.openclaw/openclaw.json.bak /data/.openclaw/openclaw.json

# Restart
openclaw gateway start

# Verify
openclaw --version  # should show 2026.3.12
```

## Or pin to specific version
```bash
npm install -g openclaw@2026.3.12
```
