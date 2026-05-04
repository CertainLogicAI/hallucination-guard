# AgentPathfinder v2 — Operational Requirements
## Version: 2.0
## Date: 2026-04-25

---

## 1. Core User Needs (from Anton)

| Need | How AgentPathfinder Addresses It |
|------|----------------------------------|
| **"Tasks aren't done at a glance"** | `pathfinder status <task_id>` shows every step with ✅ ❌ ⏳ icons, progress bar, overall state |
| **"Track to last verified change"** | Audit trail is append-only, sequence-numbered, HMAC-signed. Every event has nanosecond timestamp. Tamper detection flags any modification. |
| **"Troubleshooting help"** | Failed steps show exact error message, retry count, last attempt timestamp. Completed steps show token ID and result hash for verification. |
| **"Finish sequence for failure recovery"** | Failed steps stay in "failed" state (not deleted). `pathfinder retry` or `pathfinder resume` re-executes from failure point without losing completed steps. |

---

## 2. Operational Interface

### 2.1 At-a-Glance Status

```bash
$ pathfinder status deploy-abc123

Task: Deploy API (deploy-abc123)
State: PAUSED (step 3 failed after 3 retries)
Progress: 2/5 steps complete

Steps:
  ✅ Step 1: validate_config    COMPLETE  tok_a7f3e2  2026-04-25T12:01:33Z  (0 retries)
  ✅ Step 2: build_image       COMPLETE  tok_b8d491  2026-04-25T12:02:15Z  (0 retries)
  ❌ Step 3: run_tests         FAILED    error: connection timeout
                                    last_attempt: 2026-04-25T12:05:47Z  (3/3 retries)
  ⏳ Step 4: push_container    PENDING
  ⏳ Step 5: notify_slack      PENDING

Key: NOT reconstructed (3/5 shards collected)
Issuing shard: HELD (not distributed)
Audit trail: 7 events, untampered ✅
```

### 2.2 Track to Last Verified Change

```bash
$ pathfinder audit deploy-abc123

Audit Trail for deploy-abc123:
  [2026-04-25T12:00:00Z] TASK_REGISTERED     ✅ seq=0  steps=5  
  [2026-04-25T12:00:01Z] STEP_DISPATCHED     ✅ seq=1  step=1  agent=hermes-subagent-a13f
  [2026-04-25T12:01:33Z] STEP_COMPLETE       ✅ seq=2  step=1  token=tok_a7f3e2  result_hash=8e3a...
  [2026-04-25T12:01:34Z] STEP_DISPATCHED     ✅ seq=3  step=2  agent=hermes-subagent-b2d4
  [2026-04-25T12:02:15Z] STEP_COMPLETE       ✅ seq=4  step=2  token=tok_b8d491  result_hash=9c1f...
  [2026-04-25T12:02:16Z] STEP_DISPATCHED     ✅ seq=5  step=3  agent=hermes-subagent-c5e7
  [2026-04-25T12:05:47Z] STEP_FAILED         ✅ seq=6  step=3  error="connection timeout"  retries=3

Integrity: ✅ OK
  Total events: 7
  Tampered: 0
  Corrupted: 0
```

### 2.3 Failure Recovery — Resume from Failure Point

```bash
# Step 3 failed. Fix the underlying issue (e.g., restart test DB).
# Then resume from where it failed:

$ pathfinder retry deploy-abc123 --step 3

  [AgentRuntime] Retrying step 3/5: run_tests
  [AgentRuntime] Step 3 COMPLETE ✅
  [AgentRuntime] Continuing to step 4...
  [AgentRuntime] Step 4 COMPLETE ✅
  [AgentRuntime] Step 5 COMPLETE ✅
  [AgentRuntime] All steps complete. Reconstructing key...
  [AgentRuntime] ✅ Task COMPLETE — key reconstructed successfully

$ pathfinder status deploy-abc123

Task: Deploy API (deploy-abc123)
State: TASK_COMPLETE
Progress: 5/5 steps complete
Key: RECONSTRUCTED ✅
  hash: a3f2e8... (verified against expected hash)
```

---

## 3. Failure Recovery Design

### 3.1 Why Completed Steps Are Preserved

When Step 3 fails after 3 retries:
- Steps 1 and 2 remain `complete` with tokens `tok_a7f3e2` and `tok_b8d491`
- Their shards are already collected — **not redistributed**
- Only Step 3's shard resets to `pending`
- `retry_count` resets to 0 for the retry

**Why this matters:** You don't lose progress. A 100-step task that fails at step 97 doesn't need to re-run steps 1-96.

### 3.2 Retry Command

```bash
# Retry specific failed step
pathfinder retry <task_id> --step <step_number> --module steps.py

# Resume task (retry all failed steps in order)
pathfinder resume <task_id> --module steps.py
```

### 3.3 What "Finish the Sequence" Means

The user can:
1. **Inspect** what's done: `pathfinder status` shows completed/pending/failed
2. **Diagnose** what failed: error messages, result hashes, agent IDs
3. **Fix** the underlying issue (outside AgentPathfinder)
4. **Resume** from failure point without losing completed work
5. **Verify** completion: reconstructed key proves all steps ran

---

## 4. Verification Chain

Every step has a cryptographic proof of completion:

```
Step 1 Complete:
  ├─ Result: "config validated"
  ├─ Result Hash: SHA-256("config validated")[:16] = "8e3a..."
  ├─ Token: tok_a7f3e2
  ├─ Token Signature: HMAC(issuer_shard + step_shard, "task_id:1:...:8e3a")
  ├─ Shard: "a3f2..."  (distributed to agent, now collected)
  └─ Timestamp: 2026-04-25T12:01:33Z

Step 2 Complete: (same structure)
  ...

Task Complete:
  ├─ All 5 shards collected
  ├─ XOR reconstruction: K = s[1] ^ s[2] ^ ... ^ s[5] ^ s[issuer]
  ├─ Verification: SHA-256(K) == task.key_hash  ✅
  └─ Audit: 7 events, all HMAC verified ✅
```

**The reconstructed key is proof that every step executed.** No step can be skipped, faked, or lost without breaking the key.

---

## 5. Gap Analysis

| Feature | Status | Gap |
|---------|--------|-----|
| Task creation with UUID | ✅ Built |
| Step execution with retry (3x) | ✅ Built |
| Status showing done/pending/failed | ✅ Built |
| Audit trail with HMAC + tamper detection | ✅ Built |
| Key reconstruction after all steps | ✅ Built |
| **Retry/resume after max retries exhausted** | ❌ **MISSING** | Need `pathfinder retry` and `pathfinder resume` commands |
| Agent identity tracking | ⚠️ Basic | Agent ID logged in audit, but no keypair attestation |
| Result artifact storage | ⚠️ Basic | Only result_hash stored, not actual result data |

---

## 6. Implementation Priority

1. **P1: `retry` and `resume` CLI commands** — Unblocks failure recovery
2. **P2: Agent identity with keypair** — Stronger attestation than string ID
3. **P3: Result artifact storage** — Persist actual step outputs for debugging
4. **P4: Parallel steps** — DAG support for independent substeps
5. **P5: REST API** — HTTP endpoints for external integration

---

## 7. Decision Needed

**Should I implement P1 (retry/resume) now?** This is the only gap blocking "finish the sequence for failure recovery." Everything else works.
