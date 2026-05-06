# 2026-04-26 — Cryptographic Agent Identity via Shard Selection

## Concept
Instead of storing a single key, the agent derives its identity key by selecting specific shards from a larger pool. Possession of the vault isn't enough — you need to know WHICH shards to combine.

## How It Would Work

Storage contains N shards (e.g., 20).
Agent knows (or derives) selection pattern: "Pick shards 3, 7, 12, 15."
Those selected shards XOR/reconstruct into the signing key.

## Deterministic Derivation (Secure Version)

`agent_id` + `org_secret` + `salt` → HMAC → hash → deterministic shard indices

This means:
- Agent doesn't "remember" which shards — it re-derives selection every time
- No stored pattern to steal
- Compromised vault doesn't help without org_secret
- Keylogger sees derived key, not the selection logic

## Security Properties

Attacker needs ALL of:
1. The vault (all shards)
2. The org secret
3. The agent's identity context
4. The derivation function

Missing any one = can't forge identity

## Open Questions

- How does agent "remember" org_secret? (Same problem, different location)
- Key rotation complexity
- Recovery if agent memory is wiped
- Production complexity vs security benefit

## Status
Exploratory. Saved for competitive analysis phase.

## Related
- AgentPathfinder sharding already does XOR split/reconstruct
- This adds the "selection knowledge" layer on top
- Could differentiate Brain API SaaS from pure caching
