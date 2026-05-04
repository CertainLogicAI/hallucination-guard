# AgentPathfinder v2 — P1 Implementation Plan
## Option A: All P1 Fixes
## Started: 2026-04-25

---

## Phase 1: Storage Security (IN PROGRESS)
**Goal:** Separate step shards from task JSON.
**Changes:**
- [ ] `create_task()`: Write step shards to vault, not task JSON
- [ ] `get_step_shard()`: Read from vault directory
- [ ] `issue_step_token()`: Delete shard from vault on completion
- [ ] Task JSON: Remove step["shard"], keep issuer_shard + metadata
- [ ] Update all tests to use vault

---

## Phase 2: Atomic Persistence
**Goal:** Crash-safe writes + "running" state + idempotency
**Changes:**
- [ ] Atomic file writes (write temp, rename)
- [ ] Add "running" state to state machine
- [ ] Idempotency keys per step execution
- [ ] Startup recovery: detect crashed steps

---

## Phase 4: Audit Integrity
**Goal:** Separate audit signing key from master key
**Changes:**
- [ ] Derive audit_key from master_key using HKDF or simple KDF
- [ ] AuditTrail only receives audit_key, never master_key
- [ ] Update all audit initializations

---

## Phase 3: Concurrency Control
**Goal:** Safe multi-process access
**Changes:**
- [ ] File locking on task JSON during read-modify-write
- [ ] Atomic state transitions

---

## Phase 5: Authentication
**Goal:** Agent identity verification
**Changes:**
- [ ] Agent registration with ephemeral keypair
- [ ] Step result signing by agent
- [ ] IssuingLayer verifies agent signature before token issuance

---

## Current Status
Phase 1: IN PROGRESS
