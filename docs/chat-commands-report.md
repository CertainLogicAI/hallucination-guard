# Chat Command System — Detailed Report

**Date:** 2026-05-07  
**Scope:** All `!`-prefixed chat commands currently implemented  
**Status:** Protocol defined. **NOT yet wired into live message handler.**  

---

## ⚠️ Critical Clarification

**These chat commands are for X-posting safety and emergency override only.** They are NOT the "mathematically perfect prompts" strategy you described on 2026-05-04. That strategy is about **prompt decomposition → hallucination reduction → bounded choice sets**. These commands are **operational safety controls**. Different system, different purpose. See end of this doc for the distinction.

---

## Authentication

Before any `!` command executes, identity is verified:

| Channel | How Verified |
|---|---|
| **Webchat (this UI)** | You are authenticated by session. All commands execute as you. |
| **Telegram** | Must be from your paired DM (Chat ID: 1381429689). Group chat commands rejected for L1-L2. |
| **Discord/Slack** | Requires `@CertainLogicAI` bot admin role. |
| **Unknown/unpaired** | All commands rejected: `⛔ Authentication required.` |

---

## Command Reference (Full Breakdown)

### 🔴 LEVEL 1 — KILL SWITCH

Stops all X posting immediately. Most destructive command. Most protected.

| Command | Syntax | Confirmation Required? | What It Does |
|---|---|---|---|
| `!x-kill` | `!x-kill "reason"` | ✅ Yes — you must reply `!confirm` within 60s | Removes all X-posting crons, clears scheduled content files, locks review gate |
| `!x-kill-now` | `!x-kill-now "reason"` | ❌ No — instant execution | Same as `!x-kill` but skips confirmation. Only when delay is dangerous. |

**Execution flow for `!x-kill`:**
```
You: !x-kill "suspicious post queued"
Alex: 🛑 KILL SWITCH INITIATED
      Reason: suspicious post queued
      This will:
        • Remove all X-posting crons (X Morning, X Midday, X Evening, etc.)
        • Clear scheduled content (delete .md files in content_output/)
        • Lock review gate (deny all pending slots)
      Reply !confirm within 60s, or !cancel.

You (within 60s): !confirm
Alex: ✅ Kill switch deployed.
      Crons removed: 5
      Content cleared: 3 files
      Review gate: LOCKED
      Log: logs/x-kill-20260507-065612.log
      ⚠️ Next: Investigate. Do NOT re-enable without your approval.
```

**What happens under the hood:**
1. `openclaw cron list | grep "x-"` → get all X cron IDs
2. `openclaw cron remove <id>` for each
3. `rm -f /data/.openclaw/workspace/marketing/content_output/*.md`
4. Write emergency lock to `approved_slots.json`
5. Log to `memory/YYYY-MM-DD.md` + `logs/x-kill-<timestamp>.log`
6. Verify: check no X crons remain, no content files remain

---

### 🟠 LEVEL 2 — REVIEW GATE OVERRIDE

Control which slots post and which don't.

| Command | Syntax | Confirmation? | What It Does |
|---|---|---|---|
| `!x-status` | `!x-status` | ❌ No | Shows all slots: pending / approved / posted / denied |
| `!x-approve` | `!x-approve morning` | ❌ No | Force-approves a slot for posting |
| `!x-deny` | `!x-deny morning` | ❌ No | Force-denies a slot |
| `!x-approve-all` | `!x-approve-all` | ✅ Yes — `!confirm` within 30s | Approves ALL pending slots at once |
| `!x-lock` | `!x-lock` | ❌ No | Instant lock — deny all pending slots |

**Example session:**
```
You: !x-status
Alex: 📋 X Post Status — 2026-05-07
      ⏳ Pending: morning, midday
      ✅ Approved: evening
      ✅ Posted: night (8:47 AM)
      ⛔ Denied: —

You: !x-approve morning
Alex: ✅ Slot 'morning' approved.
      Will post at next cron run (8:00 AM CST).
      Audit: marketing/content_output/approval_log.csv

You: !x-deny midday
Alex: ✅ Slot 'midday' denied.
      File removed. Will not post.
```

**What happens under the hood:**
- `!x-approve <slot>` → `python3 marketing/post_review.py --approve <slot>` → writes to `approved_slots.json`
- `!x-deny <slot>` → removes slot file + marks denied in approval log
- `!x-approve-all` → loops through all pending slots, approves each
- `!x-status` → reads `approved_slots.json` + checks filesystem for slot files

---

### 🟡 LEVEL 3 — CRON / SCHEDULE OVERRIDE

Control timing and execution without killing everything.

| Command | Syntax | Confirmation? | What It Does |
|---|---|---|---|
| `!x-dry-run` | `!x-dry-run` | ❌ No | Generates all slots. Shows what WOULD go out. Nothing posts. |
| `!x-next` | `!x-next` | ❌ No | Shows next scheduled post time + slot name |
| `!x-skip` | `!x-skip evening` | ❌ No | Removes a slot's content + denies it. Equivalent to deny. |
| `!x-pause` | `!x-pause 4` | ❌ No | Pauses all X crons for N hours. Auto-resume after. |
| `!x-resume` | `!x-resume` | ✅ Yes — `!confirm` within 60s | Resumes ALL X crons. **Only works after L1 kill, only by you.** |

**Example:**
```
You: !x-dry-run
Alex: 🔍 DRY RUN — 2026-05-07
      morning:  "AI agents that don't hallucinate..."
      midday:   "3 PLC parsing bugs we caught..."
      evening:  "Month 6 IP decision thread..."
      No posts sent. Gate status: pending review.
      Content files: 3 generated, 0 approved.

You: !x-pause 4
Alex: ⏸️  X posting paused for 4 hours.
      Will auto-resume at 12:00 PM CST.
```

**What happens under the hood:**
- `!x-dry-run` → `cd marketing && python3 content_engine.py --all --dry-run`
- `!x-pause N` → `openclaw cron update <each-x-cron> --patch '{"enabled": false}'` + schedule re-enable
- `!x-resume` → re-enable all X crons. After L1 kill, requires your explicit confirmation.

---

### 🟢 LEVEL 4 — CONTENT / MANUAL POST

Post directly, bypassing gate + cron entirely.

| Command | Syntax | Confirmation? | What It Does |
|---|---|---|---|
| `!x-post` | `!x-post "Text here"` | ✅ Yes — `!confirm` within 60s | Emergency manual post. Goes live immediately. |
| `!x-replace` | `!x-replace morning "New text"` | ❌ No | Replace a slot's content file before gate runs. |

**Example:**
```
You: !x-post "Urgent: FaultTrace v2.1 released. Fixes critical L5X parsing bug."
Alex: ⚠️  MANUAL POST PENDING
      Text: "Urgent: FaultTrace v2.1 released. Fixes critical L5X parsing bug."
      This posts immediately to @CertainLogicAI.
      Reply !confirm within 60s.

You: !confirm
Alex: ✅ Posted.
      Tweet ID: 1234567890
      Note: Manual post bypassed review gate.
```

**What happens under the hood:**
- `!x-post` → `cd skills/x-api/scripts && node x-post.mjs --file <temp>` OR direct `client.v2.tweet()`
- `!x-replace` → overwrite `content_output/slot_X.md` with new text

---

### 🔵 UTILITY COMMANDS

| Command | Syntax | What It Does |
|---|---|---|
| `!x-help` | `!x-help` | Shows quick reference card |
| `!x-log` | `!x-log` | Shows last 5 approval / action / override entries |
| `!x-wtf` | `!x-wtf` | Emergency diagnostic. Shows what's broken RIGHT NOW |

**Example:**
```
You: !x-wtf
Alex: 🚨 DIAGNOSTIC — 2026-05-07 08:00 AM CST
      Brain API: ✅ OK (443 facts)
      X crons: 5 active
      Next post: morning (8:00 AM) in 12 minutes
      Content files: 3 pending, 1 approved, 1 posted
      Review gate: OPEN
      Credentials: ✅ Valid, verified
      Last error: None
```

---

## Confirmation Gate Summary

| Command | Confirm? | Timeout | Why |
|---|---|---|---|
| `!x-kill` | ✅ Yes | 60s | Extremely destructive, irreversible without manual rebuild |
| `!x-kill-now` | ❌ No | Instant | For genuine emergencies where 60s is too long |
| `!x-post` | ✅ Yes | 60s | Permanent public action |
| `!x-approve-all` | ✅ Yes | 30s | Batch approval reduces per-slot scrutiny |
| `!x-resume` (post-L1) | ✅ Yes | 60s | Re-enabling after kill is high-risk |
| `!x-approve <slot>` | ❌ No | Instant | Low blast radius, reversible (deny later) |
| `!x-deny <slot>` | ❌ No | Instant | Safe — only prevents posting |
| `!x-dry-run` | ❌ No | Instant | Read-only |
| `!x-status` | ❌ No | Instant | Read-only |
| `!x-pause` | ❌ No | Instant | Reversible with resume |
| `!x-skip` | ❌ No | Instant | Equivalent to deny |
| `!x-replace` | ❌ No | Instant | Content replacement, not live post |

---

## Audit Trail

Every command leaves evidence in THREE places:

1. **`logs/chat-cmd-YYYY-MM-DD.log`** → Full command + result + side effects
2. **`memory/YYYY-MM-DD.md`** → Human-readable narrative of actions
3. **`marketing/content_output/approval_log.csv`** → For review gate actions

Example log entry:
```json
{"ts": "2026-05-07T08:00:00-04:00", "cmd": "!x-approve morning", "user": "anton-webui", "result": "approved", "slot": "morning", "side_effects": ["approved_slots.json updated"]}
```

---

## Red Lines (Commands I Will NOT Execute)

Even with `!EMERGENCY` prefix:

| If you type... | I will... |
|---|---|
| `!x-post "<sensitive data>"` | Redact the sensitive data before showing confirm screen |
| `!x-kill` followed by `!x-resume` in same session | Require 5-minute cooldown between kill and resume |
| `!x-kill-now` without a quoted reason | Reject: require reason string |
| Any command from unauthenticated channel | Reject with `⛔ Authentication required` |
| `!x-approve-all` when 0 slots pending | Reject with `ℹ️ No pending slots to approve` |

---

## Status: NOT YET LIVE

These commands are defined in docs and scripts but **not yet wired into the live message handler.** I recognize them in this conversation because you are in the authenticated webchat session, but in a fresh session or other channel, I would need explicit wiring.

**To make them live:** The OpenClaw message pipeline needs to be configured to recognize `!`-prefixed commands and route them through the failsafe protocol before executing. This is a gateway-level config change.

---

## Appendix: Mathematical Prompts Strategy vs. Chat Commands

| Aspect | Chat Commands (this doc) | Mathematical Prompts (2026-05-04) |
|---|---|---|
| **Purpose** | Operational safety — stop bad things | Structural correctness — prevent hallucination |
| **Mechanism** | Command parser → script execution | Prompt decomposition → bounded choice sets |
| **What it controls** | X posting, cron timing, review gate | Model output space, failure mode boundaries |
| **Target error rate** | Zero posting incidents | 2% hallucination rate |
| **Status** | Protocol defined, not live | Concept logged, not yet implemented |
| **Key deliverable** | `!x-kill`, `!x-approve`, `!x-dry-run` | "Agents as operators of software machines" |
| **Integration** | Runs on top of current system | Replaces/augments prompt architecture |
| **First step to implement** | Gateway config for `!` prefix routing | Define prompt decomposition schema for each intent |

**Bottom line:** These chat commands are the **operational kill switch**. The mathematically perfect prompts are the **cognitive foundation**. They can coexist — commands trigger scripts, prompts govern how the agent thinks inside those scripts — but they are not the same thing. The prompt strategy is still upcoming.
