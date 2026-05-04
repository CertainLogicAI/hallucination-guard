# AgentPathfinder v2 — Architecture Document
## Version: 2.0
## Date: 2026-04-25

---

## 1. Architecture Overview

AgentPathfinder is a **deterministic task orchestration system** that uses cryptographic key splitting to enforce all-or-nothing task completion. The core insight: a task is only "done" when every substep is proven complete, and that proof is a cryptographic shard of a master key.

### 1.1 System Boundary

```
╔══════════════════════════════════════════════════════╗
║                   User / CLI                         ║
╚══════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════╗
║              AgentPathfinder System                  ║
║  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ ║
║  │ Task Engine  │  │Issuing Layer │  │   Audit   │ ║
║  │              │◄─│              │─►│   Trail   │ ║
║  └──────┬───────┘  └──────┬───────┘  └───────────┘ ║
║         │                  │                        ║
║  ┌──────┴───────┐  ┌──────┴───────┐                ║
║  │ Agent Runtime│  │  Core Crypto │                ║
║  │ (Subagent)   │  │              │                ║
║  └──────────────┘  └──────────────┘                ║
╚══════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════╗
║              OpenClaw Subagent Runtime               ║
║         (sessions_spawn / subprocess)               ║
╚══════════════════════════════════════════════════════╝
```

---

## 2. Module Architecture

### 2.1 Dependency Graph

```
pathfinder_core.py        ──┬──► No dependencies (pure crypto)
                            │
task_engine.py            ──┼──► pathfinder_core
                            │    audit_trail
                            │
audit_trail.py            ──┼──► pathfinder_core (hmac_sign/verify)
                            │
issuing_layer.py          ──┼──► pathfinder_core, task_engine, audit_trail
                            │
agent_runtime.py          ──┴──► task_engine, issuing_layer

cli.py                    ──► ALL modules
```

### 2.2 Module Responsibilities

#### pathfinder_core.py — Cryptographic Primitives
- **KeyGen**: `generate_master_key()` → 32 random bytes (256-bit)
- **ShardSplit**: XOR-based splitting into M = N+1 fragments
- **Reconstruct**: XOR all M fragments to recover key
- **HMAC**: Sign and verify with HMAC-SHA256
- **Hash**: SHA-256 of key for public reference (never expose key)

**Invariants:**
- All shards are 32 bytes
- Reconstruct requires ALL shards (no threshold — strict N+1-of-N+1)
- Individual shards are statistically indistinguishable from random

#### task_engine.py — Task Lifecycle & State Machine
- **CreateTask**: Generate key, split shards, persist task JSON
- **GetTask**: Load task by UUID
- **GetStatus**: Human-readable progress report
- **State Transitions**: Enforce valid state machine transitions

**State Machine:**
```
REGISTERED ──► DISPATCHED ──► IN_PROGRESS ──► [STEP_COMPLETE | STEP_FAILED]
                                                          │
                              ┌─────────────────────────────┘
                              │
                    All steps complete ──► RECONSTRUCTING ──► TASK_COMPLETE
                                                  │
                                                  ▼
                                        RECONSTRUCTION_FAILED (tamper detection)
```

#### issuing_layer.py — Shard Vault & Token Issuance
- **HoldIssuerShard**: Never distributed; stored encrypted in task file
- **IssueStepToken**: Validate result, sign token, log to audit
- **ReconstructMasterKey**: Combine all tokens + issuer shard, verify hash
- **FailStep**: Mark step failed, log to audit

**Security:**
- Issuer shard is the linchpin — without it, no reconstruction
- In v2.0: stored in task JSON (needs encrypt-at-rest for production)
- In v2.1+: encrypted with passphrase or HSM

#### agent_runtime.py — Execution Wrapper
- **ExecuteStep**: Run step function, hash result, request token
- **ExecuteTask**: Sequential execution with retry logic
- **RetryPolicy**: 3 attempts, no backoff (fast fail)

**Agent Interface:**
```python
def my_step_func(**kwargs) -> Any:
    """Pure function. Return serializable result."""
    return computed_value
```

#### audit_trail.py — Tamper-Evident Logging
- **AppendOnly**: JSON Lines, append only, never modify
- **HMAC-Signed**: Every event signed with master_key
- **TamperDetection**: Verify on read; flag mismatches
- **IntegrityReport**: Summary of total/tampered/corrupted events

**Log Format:**
```jsonl
{"event":"TASK_REGISTERED","task_id":"...","steps":5,"key_hash":"abc...","timestamp":"2026-04-25T12:00:00Z","seq":0,"hmac":"hex..."}
{"event":"STEP_COMPLETE","task_id":"...","step_number":1,"result_hash":"def...","token_id":"tok_abc","timestamp":"2026-04-25T12:01:00Z","seq":1,"hmac":"hex..."}
```

---

## 3. Data Flow

### 3.1 Task Creation
```
User: task.yaml
        │
        ▼
[TaskEngine.create_task] 
  ├── Generate master_key = os.urandom(32)
  ├── Split into N step_shards + 1 issuer_shard
  ├── Create task JSON with state=REGISTERED
  ├── Persist to ./pathfinder_data/tasks/{task_id}.json
  └── AuditTrail.log("TASK_REGISTERED")
        │
        ▼
  Returns: task_id
```

### 3.2 Step Execution
```
[AgentRuntime.execute_step]
  ├── Load task and step definition
  ├── Get step_shard from IssuingLayer (distributed to agent)
  ├── Execute step_func(**kwargs)
  ├── Hash result: SHA-256(result)[:16]
  └── [IssuingLayer.issue_step_token]
          ├── Validate step is pending
          ├── Verify result hash
          ├── Create signed token with shard
          ├── Update step state=complete
          ├── Increment completed_steps counter
          └── AuditTrail.log("STEP_COMPLETE")
```

### 3.3 Key Reconstruction
```
[IssuingLayer.reconstruct_master_key]
  ├── Check all steps complete (completed_steps == num_steps)
  ├── Collect N step_shards from tokens
  ├── Combine with issuer_shard (held in vault)
  ├── XOR all shards: key = s[1] ^ s[2] ^ ... ^ s[N+1]
  ├── Verify: SHA-256(key) == task.key_hash
  │   ├── Match: state=TASK_COMPLETE, audit log
  │   └── Mismatch: state=RECONSTRUCTION_FAILED, tamper detected
  └── Return key or None
```

### 3.4 Failure Handling
```
[AgentRuntime.execute_step] → Exception
  └── [IssuingLayer.fail_step]
          ├── Update step state=failed
          ├── Increment failed_steps counter
          ├── Increment retry_count
          └── AuditTrail.log("STEP_FAILED")

[AgentRuntime] → Retry (max 3)
  ├── If retry succeeds: normal flow
  └── If retry fails: state=PAUSED
          └── User intervention required
```

---

## 4. API Surface

### 4.1 Public Python API

```python
from agentpathfinder import (
    TaskEngine, IssuingLayer, AgentRuntime,
    generate_master_key, split_key, reconstruct_key
)

# 1. Create task
engine = TaskEngine()
task_id = engine.create_task(name="Deploy", steps=[
    {"name": "validate"},
    {"name": "build"},
    {"name": "deploy"}
])

# 2. Bind functions and execute
runtime = AgentRuntime(engine, IssuingLayer(engine))
status = runtime.execute_task(task_id, step_functions={
    "validate": validate_func,
    "build": build_func,
    "deploy": deploy_func
})

# 3. Check status
print(engine.get_status(task_id))

# 4. Audit
audit = AuditTrail(path, master_key)
events = audit.read_trail(task_id)
```

### 4.2 CLI

```bash
# Create
pathfinder create --file task.yaml

# Execute
pathfinder run <task_id> --module steps.py

# Monitor
pathfinder status <task_id>

# Audit
pathfinder audit <task_id>
```

---

## 5. Security Model

### 5.1 Threats Addressed

| Threat | Mitigation |
|--------|------------|
| Agent lies about completion | Step token requires actual result hash |
| Agent tampers with audit log | HMAC-signed with master_key (agent doesn't have it) |
| Partial task claimed as complete | Key requires ALL shards |
| Step skipped | State machine enforces sequential completion |
| Result replay | Result hash tied to specific step_number and task_id |
| Audit log deletion | Append-only file; corruption detected on read |

### 5.2 Trust Boundaries

```
TRUSTED ZONE (User's machine):
  - TaskEngine (creates tasks, holds state)
  - IssuingLayer (holds issuer_shard, signs tokens)
  - AuditTrail (signs events with master_key)
  - Master key (never leaves this zone)

UNTRUSTED ZONE (Agent runtime):
  - AgentRuntime (executes step functions)
  - Step functions (user-provided, could be buggy/malicious)
  - Step shards (distributed to agent, but useless without issuer_shard)
```

### 5.3 Key Material Handling

| Key Material | Location | Access |
|-------------|----------|--------|
| Master key | Only exists during split/reconstruct | Never persisted |
| Issuer shard | Task JSON (encrypted in v2.1+) | IssuingLayer only |
| Step shards | Distributed to agent per step | One shard per step |
| HMAC signing key | Derived from master_key + task context | AuditTrail, IssuingLayer |

---

## 6. File System Layout

```
./pathfinder_data/
├── tasks/
│   └── {task_id}.json           # Task state + encrypted issuer_shard
├── audit/
│   └── {task_id}.jsonl          # Append-only signed event log
└── keys/
    └── (reserved for v2.1+ HSM/keystore)
```

### 6.1 Task JSON Schema

```json
{
  "task_id": "uuid",
  "name": "string",
  "state": "registered|in_progress|paused|task_complete|...",
  "created_at": "ISO8601",
  "num_steps": 3,
  "key_hash": "sha256_hex",
  "issuer_shard": "encrypted_hex",  // v2.1+
  "completed_steps": 0,
  "failed_steps": 0,
  "steps": [
    {
      "step_number": 1,
      "name": "validate",
      "state": "pending|complete|failed",
      "shard": "hex",  // distributed to agent
      "token_id": null,
      "result_hash": null,
      "error": null,
      "retry_count": 0
    }
  ]
}
```

---

## 7. Error Handling Strategy

### 7.1 Categories

| Error | Response |
|-------|----------|
| Step function exception | Log STEP_FAILED, retry up to 3x, then PAUSED |
| Result validation fails | Same as exception — treat as failure |
| Reconstruction hash mismatch | RECONSTRUCTION_FAILED, tamper alert |
| Audit HMAC failure | TAMPER_DETECTED on read, flag for review |
| Missing task file | ValueError, log to stderr |
| Step already complete | ValueError, idempotent? (no) |

### 7.2 Retry Logic

```python
MAX_RETRIES = 3
for attempt in range(MAX_RETRIES + 1):
    result = execute_step()
    if result["status"] == "complete":
        break
    if attempt < MAX_RETRIES:
        continue
    # All retries exhausted
    pause_task()
```

---

## 8. Scaling Considerations

### 8.1 Current Limitations (v2.0)

- Sequential execution only
- Filesystem-only storage
- In-process issuing layer
- No REST API
- No distributed agents

### 8.2 Future Extensions (v2.1+)

- **Parallel steps**: DAG dependency graph instead of linear list
- **REST API**: HTTP endpoints for remote task management
- **Distributed agents**: Agents running on separate machines
- **Encrypted vault**: Encrypt issuer_shard with passphrase or HSM
- **Database backend**: SQLite/Postgres for task state at scale
- **Web dashboard**: Real-time progress visualization
- **Webhook notifications**: Callback on step completion/failure

---

## 9. Test Coverage

| Test Category | Count | Status |
|--------------|-------|--------|
| Cryptographic primitives | 4 | ✅ |
| Task lifecycle | 3 | ✅ |
| Token issuance | 1 | ✅ |
| Reconstruction | 2 | ✅ |
| Failure handling | 1 | ✅ |
| **Total** | **11** | **✅** |

---

## 10. Open Questions for Anton

1. **Parallel execution?** Some tasks have independent substeps (e.g., build frontend + backend simultaneously)
2. **Retry policy?** Currently 3 retries, no backoff. Want exponential backoff?
3. **Agent attestation?** Currently trusts agent ID string. Want agent keypair signing?
4. **Encrypt issuer shard?** Currently plain JSON. Want passphrase encryption now?
5. **REST API?** Want HTTP endpoints for integration, or CLI-only for now?

**Approved to build?**
