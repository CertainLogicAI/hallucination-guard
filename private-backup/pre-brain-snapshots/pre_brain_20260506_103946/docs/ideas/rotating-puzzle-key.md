# 2026-04-26 — Rotating Key with Hard-Coded Puzzle Structures

## Concept
- Agent contains hard-coded internal structure/map
- Server sends encrypted signal: "use puzzle combination #7"
- Agent uses its internal structure to solve puzzle #7 and derive rotating key
- Multiple paths, randomized puzzle selection per request
- Creates moving target: attacker can't replay because next request uses different puzzle

## Why It Sounds Good
- Rotation = replay attacks fail
- Hard-coded structure = no external storage needed
- Randomized paths = no single key to steal
- Puzzle solving = proves agent "knows" the structure, not just possesses data

## Why It Probably Fails in Software

**1. The "encryption" of the signal is meaningless**
- If agent can decrypt the signal → decryption key exists in agent → extractable
- If attacker intercepts signal + has agent code → they can decrypt too
- Signal tells attacker WHICH puzzle → they can precompute all puzzles offline

**2. Hard-coded structure = extractable secret**
- "Hard-coded" means in the binary/source → strings, disassembly, memory dump
- Once extracted, attacker owns all puzzles forever
- Rotation doesn't help if attacker has the puzzle book

**3. Puzzle solving in software = just another function**
- If the agent can run the puzzle function → attacker can run the same function
- There's no "only the agent can solve this" in pure software
- Physics/hardware creates that boundary, not code

**4. Complexity without security gain**
- This is the same as: server sends nonce, agent derives key from secret + nonce
- The "puzzle" layer adds steps but no actual security
- Attacker with agent binary + intercepted traffic = can compute every possible key

## What Would Actually Work
- **Hardware-bound keys:** TPM, secure enclave, smart card (proves physical possession)
- **Multi-factor:** Agent + human approval (phone push, OTP)
- **Rate-limited trusted execution:** Remote attestation that agent code is unmodified

## Status
Exploratory. Interesting thought experiment. Likely not feasible in pure software without hardware trust anchor.

## Saved For
Future revisit if hardware integration becomes viable or if threat model changes.
