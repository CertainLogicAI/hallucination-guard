# AgentPathfinder v2 — Specification

## 1. Core Concept

Single master key (256-bit) → Split into N+1 shards via XOR → N shards distributed as completion tokens → 1 shard held by issuer → Full key only reconstructable when ALL N substeps complete.

## 2. Cryptography

- **Key:** `os.urandom(32)` → 64-char hex
- **Split:** M-1 random shards + 1 computed shard: `s[M] = K XOR s[1] XOR ... XOR s[M-1]`
- **Reconstruction:** XOR all M shards together
- **Signing:** HMAC-SHA256 with master_key for issuer, agent_private_key for agent attestations

## 3. Modules

| Module | Purpose |
|--------|---------|
| `pathfinder_core.py` | KeyGen, ShardSplit, reconstruct, HMAC |
| `task_engine.py` | Task decomposition, step dispatch, state machine |
| `issuing_layer.py` | Shard vault, token issuance, signature validation |
| `agent_runtime.py` | Step execution wrapper, result validation |
| `audit_trail.py` | Append-only JSONL, HMAC-signed events, tamper detection |
| `cli.py` | Task create/run/status/audit/reconstruct |

## 4. State Machine

```
REGISTERED → DISPATCHED → IN_PROGRESS → [STEP_COMPLETE | STEP_FAILED]

All steps complete → RECONSTRUCTING → TASK_COMPLETE (key verified)
                                          → RECONSTRUCTION_FAILED (tamper)

Any step fails → PAUSED (retry) → IN_PROGRESS
               → ABORTED (max retries exceeded)
```

## 5. Audit Events

```jsonl
{"event":"TASK_REGISTERED","task_id":"...","steps":N,"key_hash":"sha256(key)","hmac":"..."}
{"event":"STEP_DISPATCHED","task_id":"...","step_number":1,"shard_hash":"...","hmac":"..."}
{"event":"STEP_COMPLETE","task_id":"...","step_number":1,"result_hash":"...","token_id":"...","hmac":"..."}
{"event":"STEP_FAILED","task_id":"...","step_number":2,"error":"...","hmac":"..."}
{"event":"TASK_COMPLETE","task_id":"...","key_reconstructed":true,"hmac":"..."}
```

## 6. Failure Transparency

```bash
pathfinder status <task_id>

→ Step 1/5: COMPLETE ✅ (token: tok_abc123)
→ Step 2/5: FAILED   ❌ (error: timeout after 30s)
→ Step 3/5: PENDING
→ Step 4/5: PENDING
→ Step 5/5: PENDING

pathfinder audit <task_id>
→ Full timeline with HMAC signatures
```

## 7. CLI

```bash
pathfinder create --file task.yaml   # decompose + register + generate shards
pathfinder run <task_id>             # dispatch to agent, monitor
pathfinder status <task_id>          # show completed/pending/failed
pathfinder audit <task_id>           # full signed audit trail
pathfinder reconstruct <task_id>     # verify all tokens + reconstruct key
```

## 8. Design Principles

- **Deterministic:** Same spec always → same steps
- **Filesystem-only:** JSON + JSONL, no DB
- **Tamper-evident:** Every record HMAC-signed
- **Agent-agnostic:** Any callable Python function as a step
- **Sequential-by-default:** Step N waits for N-1 (configurable to parallel)

## 9. Open Questions

1. **Parallel steps?** Sequential default, but some tasks have independent substeps
2. **Partial credit?** No — strict all-or-nothing key reconstruction
3. **Retry policy?** I propose: 3 retries max, no backoff (fast fail)
4. **Issuing layer?** In-process for MVP, separate daemon if needed later
5. **Agent identity?** Trust agent ID string, or require agent attestation keypair?

**What do you want?**
