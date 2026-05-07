# Chat-Based Emergency Command Protocol

**Version:** 1.0  
**Last updated:** 2026-05-07  
**Scope:** All messaging channels (webchat, Telegram when paired, Discord, etc.)

---

## Philosophy

Terminal access is not guaranteed during an incident. Every emergency action available via CLI must also be triggerable via chat, with **the same security boundaries**.

**Principle:** Chat commands are a convenience layer, not a bypass. Authorization, audit trails, and confirmation gates remain intact.

---

## Authentication

### Who Can Trigger What

| Identity | Kill Switch (L1) | Review Override (L2) | Cron/Content (L3-4) |
|---|---|---|---|
| **Anton** (`USER.md` identity) | ✅ Yes | ✅ Yes | ✅ Yes |
| **Alex** (this agent) | ✅ Yes, but MUST notify Anton immediately | ✅ Yes | ⚠️ Test mode only |
| **Other users / group chats** | ❌ No | ❌ No | ❌ No |

### Identity Verification

Chat commands use **channel + identity binding**:

- **Webchat (Control UI):** Session-bound. You are authenticated by session custody. Any emergency command in this channel executes as you.
- **Telegram:** Requires paired chat ID (`1381429689`). Command must come from your paired DM. Group chat commands rejected for L1-L2.
- **Discord/Slack:** Role-based. Only `@CertainLogicAI` bot admin role can trigger L1-L2.
- **Unknown/unpaired:** All emergency commands rejected with `⛔ Authentication required.`

---

## Command Reference

### 🔴 Level 1 — Kill Switch

| Command | Action | Confirmation |
|---|---|---|
| `!x-kill <reason>` | Stop all X posting immediately | ⚠️ Requires `!confirm` within 60s |
| `!x-kill-now <reason>` | Same but **skip confirmation** | No confirmation — instant. Use only when delay is dangerous. |

**Response flow:**
```
You: !x-kill "suspicious post queued"
Alex: 🛑 KILL SWITCH INITIATED
      Reason: suspicious post queued
      This will:
        • Remove all X-posting crons
        • Clear scheduled content
        • Lock review gate
      Reply !confirm within 60s to execute, or !cancel.

You: !confirm
Alex: ✅ Kill switch deployed.
      Crons removed: X Morning, X Midday, X Evening...
      Content cleared: 3 files
      Review gate: LOCKED
      Log: logs/x-kill-20260507-065612.log
      Next: Investigate root cause. Do NOT re-enable without your approval.
```

---

### 🟠 Level 2 — Review Gate Override

| Command | Action |
|---|---|
| `!x-status` | Show today's slots: pending / approved / posted / denied |
| `!x-approve <slot>` | Force-approve a slot (e.g. `!x-approve morning`) |
| `!x-deny <slot>` | Force-deny a slot |
| `!x-approve-all` | Approve all pending slots |
| `!x-lock` | Emergency lock gate (deny all pending) |

**Response:**
```
You: !x-status
Alex: 📋 X Post Status — 2026-05-07
      ⏳ Pending: morning, midday
      ✅ Approved: evening
      ✅ Posted: night (8:47 AM)
      ⛔ Denied: —

You: !x-approve morning
Alex: ✅ Slot 'morning' approved.
      Will post at next cron run.
      Audit: marketing/content_output/approval_log.csv
```

---

### 🟡 Level 3 — Cron / Schedule Override

| Command | Action |
|---|---|
| `!x-dry-run` | Generate all slots without posting. Show what WOULD go out. |
| `!x-next` | Show next scheduled post time |
| `!x-skip <slot>` | Skip a slot (remove file + deny) |
| `!x-pause <hours>` | Pause all X crons for N hours (auto-resume) |
| `!x-resume` | Resume X crons (only Anton can do this after L1) |

**Response:**
```
You: !x-dry-run
Alex: 🔍 DRY RUN — 2026-05-07
      morning:  "AI agents that don't hallucinate..."
      midday:   "3 PLC parsing bugs we caught..."
      evening:  "Month 6 IP decision thread..."
      No posts sent. Gate status: pending review.
```

---

### 🟢 Level 4 — Content / Manual Post

| Command | Action |
|---|---|
| `!x-post "<text>"` | Emergency manual post (bypasses gate + review) |
| `!x-replace <slot> "<text>"` | Replace a slot's content before gate |

**⚠️ `!x-post` requires `!confirm` — it goes live immediately.**

---

## Special Commands

| Command | Purpose |
|---|---|
| `!x-help` | Show this reference card |
| `!x-log` | Show last 5 approval / action log entries |
| `!x-wtf` | Emergency diagnostic — show what's broken right now |

---

## Confirmation Gates

Any command that could cause public impact requires confirmation:

| Command | Confirm? | Timeout |
|---|---|---|
| `!x-kill` | ✅ Yes | 60s |
| `!x-kill-now` | ❌ No | Instant |
| `!x-post` | ✅ Yes | 60s |
| `!x-approve-all` | ✅ Yes | 30s |
| `!x-resume` (after L1) | ✅ Yes | 60s |
| `!x-approve <slot>` | ❌ No | Instant |
| `!x-deny <slot>` | ❌ No | Instant |

Confirmation state is **per-session, per-command**. No blanket "yes to all."

---

## Audit Trail

Every chat command is logged with:

1. **Timestamp** (ISO 8601)
2. **Command** (full text)
3. **Identity** (channel + verified user)
4. **Result** (success / denied / error)
5. **Side effects** (crons removed, files changed, posts sent)

Stored in:
- `logs/chat-cmd-YYYY-MM-DD.log` — daily rotation
- `memory/YYYY-MM-DD.md` — for L1 events and resume requests

---

## Integration with CLI Failsafe

Chat commands and CLI commands share the same underlying mechanisms:

- `!x-kill` → executes `scripts/x-kill.sh`
- `!x-approve` → calls `post_review.py --approve`
- `!x-dry-run` → calls `content_engine.py --all --dry-run`

Chat is a thin wrapper — the protocol logic lives in one place.

---

## Fallback: No Chat Access

If messaging is down and you have terminal access:

```bash
# Same as !x-kill
./scripts/x-kill.sh "reason"

# Same as !x-status
python3 marketing/post_review.py --status

# Same as !x-dry-run
cd marketing && python3 content_engine.py --all --dry-run
```

---

## Implementation Notes

### For Alex (this agent)

When an emergency command is received:

1. **Authenticate** — verify sender identity (Anton only for L1)
2. **Confirm** — if required, request `!confirm` and set 60s timer
3. **Execute** — run the underlying script/tool
4. **Log** — append to daily log + memory file
5. **Report** — concise status back to chat

**Never execute L1 on behalf of anyone except Anton. Never execute `!x-kill-now` without explicit text containing that exact command string (prevents accidental triggers).**

---

**Document owner:** Alex  
**Review cycle:** With failsafe protocol doc, monthly or post-incident
