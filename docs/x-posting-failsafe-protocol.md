# X Posting Failsafe Protocol

**Version:** 1.0  
**Last updated:** 2026-05-07  
**Scope:** All automated X posting systems (v1 slots, v2 trending, review gate, crons)

---

## Philosophy

Everything that can go wrong will. The protocol prioritizes **stop-first, ask-second** — no automated system is more important than preventing a credential leak, off-brand post, or rate-limit ban.

**3-Click Rule:** Any emergency action must be executable in ≤3 commands/clicks.

---

## Emergency Levels

### 🔴 LEVEL 1 — KILL SWITCH (Immediate)
**Triggers:** Credential compromise suspected, off-brand post detected, rate limit warning, account flagged, ANY doubt.

**Actions (do in order, first that works wins):**

1. **Kill all X crons:**
   ```bash
   openclaw cron list | grep -i "x-" | awk '{print $1}' | xargs -I{} openclaw cron remove {}
   ```

2. **Delete scheduled tweet files (prevents queue flush):**
   ```bash
   rm -f /data/.openclaw/workspace/marketing/content_output/*.md
   rm -f /data/.openclaw/workspace/marketing/content_output/approved_slots.json
   ```

3. **Disable review gate approvals:**
   ```bash
   echo '{"emergency_lock": true, "reason": "<your reason>"}' > /data/.openclaw/workspace/marketing/content_output/approved_slots.json
   ```

4. **Verify silence:**
   ```bash
   cd /data/.openclaw/workspace/company-brain && bun run src/cli.ts list | grep -i "x-" || echo "NO X POSTS SCHEDULED"
   ```

**After kill:** Immediately investigate root cause. Do NOT re-enable until fix verified.

---

### 🟠 LEVEL 2 — REVIEW GATE OVERRIDE
**Triggers:** Need to post urgently despite gate, skip a slot that shouldn't go out, manual correction required.

**Override capabilities:**

| Action | Command |
|---|---|
| Force-approve a slot | `python3 /data/.openclaw/workspace/marketing/post_review.py --approve <slot>` |
| Force-deny a slot | `python3 /data/.openclaw/workspace/marketing/post_review.py --deny <slot>` |
| Emergency lock all | `echo '{"emergency_lock": true}' > /data/.openclaw/workspace/marketing/content_output/approved_slots.json` |
| Unlock all | `python3 /data/.openclaw/workspace/marketing/post_review.py --approve-all` |
| Show current status | `python3 /data/.openclaw/workspace/marketing/post_review.py --status` |

**Override audit trail:** Every `--approve`/`--deny` logs to `marketing/content_output/approval_log.csv` with timestamp + user. Never delete this file.

---

### 🟡 LEVEL 3 — CRON TIME OVERRIDE
**Triggers:** Testing new schedule, timezone changes, daylight saving, one-off campaign timing.

**Safe override process:**

1. **Never edit cron times directly in production** — always test in isolated session first:
   ```bash
   openclaw sessions_spawn --mode run --task "Test X cron timing: run x_post.py with slot morning at 5 minutes from now"
   ```

2. **Temporary time change** (valid for 1 run, auto-reverts):
   ```bash
   # Create a one-shot cron with explicit end time
   openclaw cron add --name "X Test Manual" \
     --schedule "at:<ISO timestamp>" \
     --command "cd /data/.openclaw/workspace/marketing && python3 x_post.py morning"
   ```

3. **Permanent schedule change** (requires git commit):
   - Edit the cron via `openclaw cron update <id>`
   - Test in isolated session
   - Commit change to git with message: `config(x): <reason> [<ticket>]`
   - Document in `memory/YYYY-MM-DD.md`

4. **Daylight saving / timezone override:**
   ```bash
   # All crons run in UTC internally; CST offset handled by schedule tz field
   # Emergency: override all X crons to UTC+0
   openclaw cron list | grep "x-" | awk '{print $1}' | while read id; do
     openclaw cron update $id --patch '{"schedule": {"tz": "UTC"}}'
   done
   ```

---

### 🟢 LEVEL 4 — POST CONTENT OVERRIDE
**Triggers:** Generated post is wrong, need to inject manual post, correction/update needed.

**Override capabilities:**

| Scenario | Method |
|---|---|
| Replace a slot's content | Edit the markdown file in `content_output/slot_X.md` BEFORE review gate runs |
| Inject manual post | Use `x-post.mjs` or X web interface directly — bypasses all automation |
| Regenerate a slot | Delete `content_output/slot_X.md`, trigger `content_engine.py --slot X` |
| Skip slot entirely | `post_review.py --deny <slot>` or rename file to `slot_X.skip` |
| Emergency correction post | Manual X composition — automation stays silent |

**Rule:** Manual posts via X web interface or `x-post.mjs` NEVER trigger review gate. Use for corrections, announcements, or sensitive content.

---

## Testing Mode

### Dry-Run Protocol
**Use before any cron change, model swap, or major config edit.**

```bash
# 1. Run content engine in dry-run (generates but doesn't save)
cd /data/.openclaw/workspace/marketing && python3 content_engine.py --all --dry-run

# 2. Show what WOULD be posted
python3 post_review.py --show

# 3. Test a single slot through the pipeline (no actual post)
cd /data/.openclaw/workspace/skills/x-api/scripts && node x-post.mjs --dry-run "Test post content"

# 4. Verify cron timing without executing
openclaw cron runs <cron-id> --limit 5  # shows next scheduled run times
```

### Isolated Test Session
```bash
# Spawn a throwaway session that can test X posting without affecting production
openclaw sessions_spawn \
  --mode run \
  --task "Test the X morning slot pipeline: generate content, run review gate mock, verify no actual post"
```

---

## Role-Based Access

| Role | Capabilities |
|---|---|
| **Anton (you)** | All overrides, kill switch, permanent config changes |
| **Alex (me)** | Level 2-4 overrides, can trigger kill switch but MUST notify you immediately. Cannot re-enable after kill without approval. |
| **Subagent/Isolated sessions** | Dry-run only. No posting, no approval, no cron edits. |
| **Cron jobs** | Execute approved slots only. Cannot override gate. Cannot self-approve. |

---

## Audit Trail Requirements

Every override action must leave evidence:

1. **Git commit** — config changes committed with reason
2. **Memory log** — `memory/YYYY-MM-DD.md` entry for any Level 1-2 event
3. **Approval log** — `marketing/content_output/approval_log.csv` for gate overrides
4. **Cron history** — `openclaw cron runs <id>` stores execution history
5. **X account history** — Screenshot or note deleted/edited posts

---

## Recovery Checklist

After a Level 1 kill switch, before re-enabling:

- [ ] Root cause documented in `memory/`
- [ ] Bug fix committed and tested
- [ ] Credentials rotated if any exposure possible
- [ ] Review gate reset (`approved_slots.json` cleared or rebuilt)
- [ ] Dry-run passes: generate → review → simulate post
- [ ] Anton explicitly approves re-enable
- [ ] Re-enable ONE cron first (lowest risk slot), monitor for 24h
- [ ] Full re-enable only after 24h clean

---

## Quick Reference Card

```
EMERGENCY STOP (any terminal):
  openclaw cron list | grep "x-" | awk '{print $1}' | xargs openclaw cron remove

REVIEW GATE STATUS:
  python3 /data/.openclaw/workspace/marketing/post_review.py --status

FORCE APPROVE SLOT:
  python3 /data/.openclaw/workspace/marketing/post_review.py --approve <slot>

DRY RUN:
  cd /data/.openclaw/workspace/marketing && python3 content_engine.py --all --dry-run
```

---

**Document owner:** Alex  
**Review cycle:** Monthly or after any Level 1 event
