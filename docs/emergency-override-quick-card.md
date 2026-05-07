# Emergency Override — Quick Card

**When Alex refuses and delay hurts.**

---

## Signal Emergency

**Say any of these:**
- `This is an emergency. Override refusal [X].`
- `!EMERGENCY <command>`
- Describe the active crisis ("site is down," "data disappearing")

Alex acknowledges within seconds, logs it, executes.

---

## Red Lines (Never Override Even in Emergency)

1. No sending private data to untrusted channels
2. No deleting backups
3. No credential rotation without replacement ready
4. No permanent destruction of the only copy
5. No group chat messages without recipient consent
6. No committing secrets to git
7. No disabling audit/logging
8. No executing untrusted code

Need one of these? Alex will do it but flag **mandatory 24h review**.

---

## What Happens After

```
Execute → Log to memory + emergency log → Report result →
→ 24h Post-hoc review (Alex prompts you)
```

---

## Common Scenarios

| Anton says | Alex does |
|---|---|
| "Restart service X NOW" | Executes. Logs. Reviews service status. |
| "Show me the API key" | Shows redacted (first 4 + last 4). Logs access. |
| "Commit this hotfix untested" | Commits. Skips tests. Flags follow-up. |
| "Post status update to @partner" | Sends. Factual only. Flags if recipient new. |
| "Pay $200 or vendor shuts off" | Pays. ≤$500 only. Logs transaction. |

---

## Review Check

Alex prompts within 24h:  
`Emergency override review due: [action] on [date]. Any concerns?`

Just reply ✅ or flag the issue.

---

**Full protocol:** `docs/emergency-override-protocol.md`
