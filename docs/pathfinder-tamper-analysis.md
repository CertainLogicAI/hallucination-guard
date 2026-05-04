# AgentPathfinder — Tamper Realities

**Date:** 2026-04-25
**Question:** Is this completely tamper-proof by an agent?

---

## Honest Answer: No

AgentPathfinder is **tamper-evident**, not **tamper-proof** against a malicious agent with filesystem access.

---

## What IS Protected

| Threat | Protection | How |
|--------|-----------|-----|
| **Accidental corruption** | ✅ Atomic writes | temp + fsync + rename |
| **Concurrent access** | ✅ File locking | fcntl.LOCK_EX per task |
| **Crash during step** | ✅ Running state + idempotency | Detect stuck steps, reset safely |
| **Audit tampering (after the fact)** | ✅ HMAC-SHA256 | Any edit breaks signature chain |
| **Partial completion** | ✅ Hash verification | Reconstruct only if all steps match |

---

## What is NOT Protected

### If a Malicious Agent Has Filesystem Access

The current architecture stores:
- **Task JSON:** Contains `issuer_shard` (hex-encoded)
- **Vault directory:** Contains all step shards as individual files

A compromised agent with read access to both can:
1. Read the task JSON → get `issuer_shard`
2. Read all vault files → get all step shards
3. XOR them together → reconstruct the master key

**The protection is:** The audit trail will show exactly what happened, when, and which agent was involved. But the key is exposed.

### If a Malicious Agent Has Task Engine Access

A compromised agent with access to the `TaskEngine` class can:
- Call `get_step_shard(task_id, step_number)` for ANY step
- Modify task state directly (bypassing the issuing layer)
- Delete or corrupt vault files

**Current mitigation:** Agent authentication (Phase 5) verifies HMAC-signed requests, but this only protects the *issuing layer*. If the agent breaks out of that boundary, the filesystem is exposed.

---

## The Threat Model

AgentPathfinder is designed for **trusted agents in a trusted environment**:

| Scenario | Security Level | Appropriate? |
|----------|---------------|--------------|
| Hermes agent on your local machine | ✅ Trusted | Yes — agents are under your control |
| CI/CD runner in GitHub Actions | ⚠️ Semi-trusted | Yes — environment is isolated, ephemeral |
| Multi-tenant SaaS with user-uploaded agents | ❌ Untrusted | **No** — agents could attack each other |
| Public marketplace with arbitrary agents | ❌ Untrusted | **No** — requires sandboxing |

---

## What Would Make It Tamper-Proof

For true tamper-proofing against malicious agents:

| Feature | Effort | Protects Against |
|---------|--------|-----------------|
| **Remote vault (server-side)** | 2-3 weeks | Agent never sees shards |
| **Trusted Execution Environment (TEE)** | 2-3 months | Hardware-enforced isolation |
| **Remote attestation** | 1 month | Prove agent is running correct code |
| **Capability-based access** | 1-2 weeks | Agent gets only its step, nothing else |
| **Encrypted vault at rest** | 1 week | Protects against filesystem snooping |

---

## Recommended Hardening for Beta

### Phase 1 (Immediate — Free Tier)
- **Encrypt vault files at rest** with a key derived from machine fingerprint
- **Restrict agent access** via capability tokens (agent can only see its own step)
- **Rate limiting** on step shard requests

### Phase 2 (Pro Tier — Hosted Vault)
- **Server-side vault:** Agent never holds raw shards
- **Blind signatures:** Agent proves completion without seeing key material
- **Audit verification API:** Centralized tamper detection

### Phase 3 (Enterprise — TEE)
- **Intel SGX / AMD SEV** enclaves for step execution
- **Remote attestation** before shard release
- **Hardware-backed key storage**

---

## Bottom Line

**Current state:** Tamper-evident. If something goes wrong, the audit trail proves exactly what happened. But a malicious agent with filesystem access can reconstruct the key.

**For beta:** This is fine. Free tier users run their own agents. Pro tier will add hosted vault (server-side storage) which eliminates the local filesystem attack.

**For enterprise:** Requires TEE or remote vault with blind signatures.

**The honest answer to "is it completely tamper-proof":**

**No.** But it's **damn hard to tamper with undetected**, and **damn easy to detect tampering**. That's the value proposition for beta.
