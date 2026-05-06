# AgentPathfinder v2 — P1 Fix Prioritization
## 2026-04-25

---

## P1 Issues Ranked by Dependency Order

### Phase 1: Storage Security (Foundation)
**Issue #1: All shards co-located in task JSON**
- **Effort:** Medium (2-3 hours)
- **What:** Separate step shards from task JSON. Issue to agents, delete from file. Only issuer_shard stays in task JSON.
- **Why first:** Every other fix assumes the shards are actually protected. Without this, the security model is decoration.
- **Implementation:** `create_task()` generates shards → writes step shards to separate files or distributes immediately → task JSON only stores `issuer_shard` + metadata.

### Phase 2: Atomic Persistence (Reliability)
**Issue #5: Non-atomic JSON writes + Issue #3: Crash = duplicate execution**
- **Effort:** Medium (2-3 hours)
- **What:** 
  - Atomic file writes (write to temp, rename)
  - Add "running" state to detect crashes
  - Idempotency keys per step execution
- **Why second:** Without atomic writes, crash recovery is impossible. Without "running" state, you can't distinguish crashed steps from pending ones.
- **Implementation:**
  ```
  pending → running → [complete | failed]
  ```
  On startup, scan for "running" steps → mark as "crashed" → require manual review or auto-retry with idempotency key.

### Phase 3: Concurrency Control (Scale)
**Issue #2: No concurrency control**
- **Effort:** Low-Medium (1-2 hours)
- **What:** File-level locking or atomic compare-and-swap on task state.
- **Why third:** Only matters if multiple agents/processes access the same task. If Phase 2 is done (atomic writes), this becomes a smaller gap.
- **Implementation:** `fcntl.flock()` on task JSON during read-modify-write, or SQLite for task state with transactions.

### Phase 4: Audit Integrity (Logging)
**Issue #4: Audit trail uses master key as HMAC key**
- **Effort:** Low (30-60 min)
- **What:** Generate separate audit signing key derived from master key. Never expose master key to AuditTrail.
- **Why fourth:** Important but not blocking. Audit tampering requires master key compromise, which Phase 1 makes harder.
- **Implementation:** `audit_key = HKDF(master_key, salt=b"audit", info=task_id)` — AuditTrail only gets `audit_key`.

### Phase 5: Authentication (Access Control)
**Issue #6: No auth boundary on IssuingLayer**
- **Effort:** Medium (2-3 hours)
- **What:** Agent identity verification before token issuance. Require agent to prove possession of a keypair or shared secret.
- **Why fifth:** Only matters in distributed/multi-agent scenarios. If single-process, this is less urgent.
- **Implementation:** Agent generates ephemeral keypair, signs step result, IssuingLayer verifies against registered agent public key.

---

## Recommended Implementation Order

```
Phase 1 → Phase 2 → Phase 4 → Phase 3 → Phase 5
(Storage)  (Atomic)  (Audit)   (Lock)   (Auth)
```

**Rationale:**
- Phase 1 + 2 together make the system crash-safe and actually secure the key splitting
- Phase 4 is quick and addresses a real integrity concern
- Phase 3 only matters after Phase 2 (no point locking if writes aren't atomic)
- Phase 5 is the most complex and least urgent for single-process use

---

## Estimate: Full P1 Fix = ~1 Day of Work

| Phase | Effort | Cumulative |
|-------|--------|------------|
| 1. Storage Security | 2-3 hrs | 2-3 hrs |
| 2. Atomic Persistence | 2-3 hrs | 4-6 hrs |
| 4. Audit Integrity | 0.5-1 hr | 5-7 hrs |
| 3. Concurrency | 1-2 hrs | 6-9 hrs |
| 5. Authentication | 2-3 hrs | 8-12 hrs |

---

## Decision Needed

**Option A:** Implement all P1 fixes now (1 day, ~10 hours)
**Option B:** Implement Phase 1 + 2 only (core security + crash safety, ~5 hours)
**Option C:** Implement Phase 1 only (shard separation, ~3 hours) — minimum viable fix
**Option D:** Something else

What's the call?
