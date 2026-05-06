# Crypto Provenance Integration: AgentPathfinder → GBrain

## Overview
Every GBrain write is HMAC-signed using AgentPathfinder's shard-based signing. 
Every read returns the HMAC signature for third-party verification.

## What This Gives Us
- Tamper-evident knowledge: If a page changes, its HMAC signature won't verify
- Third-party audit: Anyone with the public shard can verify provenance
- Chain of custody: Every edit is cryptographically linked to its author/audit ID

## Integration Points

### 1. Write Signing (brain.put_page, brain.ingest)
Before GBrain writes to PGLite:
1. Deterministic shim generates page content + frontmatter
2. AgentPathfinder signs: `hmac_sha256(page_content, shard)`
3. Signature stored as `hmac_signature` field in page metadata
4. Signature also stored in off-page audit log

### 2. Read Verification (brain.get_page, brain.query)
After GBrain reads from PGLite:
1. Return page content + `hmac_signature` from metadata
2. Optional: Re-verify on read (compute hash of content, compare to stored sig)
3. Failed verification = flagged response with audit alert

### 3. Audit Chain
- Every write: `audit_id` → `hmac` → `page_id` → `timestamp`
- Every read: `audit_id` → `hmac_verified` → `page_id` → `timestamp`

## MVP Implementation
Reuse existing AgentPathfinder `hmac_sign()` and shard infrastructure.
Single new module: `company-brain/crypto_provenance.py`

## Files Changed
- `deterministic_brain.py`: Wrap _gbrain_put with signing
- GBrain metadata schema: Add `hmac_signature` field
- New: `crypto_provenance.py`: Signing helpers + verification
