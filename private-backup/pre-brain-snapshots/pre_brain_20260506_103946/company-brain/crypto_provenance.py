#!/usr/bin/env python3
"""
Crypto Provenance Layer — AgentPathfinder HMAC over GBrain writes
Every page write is signed; every read can be verified by third parties.
Uses SHA-256(content) + HMAC for robustness against frontmatter reformatting.
"""

import hmac
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────
CERTAINLOGIC_DATA = Path(os.getenv("CERTAINLOGIC_DATA", "/data/.openclaw/workspace/company-brain-data"))
PROVENANCE_DB = CERTAINLOGIC_DATA / "provenance_log.jsonl"
MASTER_KEY_ENV = "CERTAINLOGIC_MASTER_KEY"

# Derive a stable signing key from environment or generate one
_signing_key: Optional[bytes] = None

def _get_signing_key() -> bytes:
    """Get or create the HMAC signing key."""
    global _signing_key
    if _signing_key is None:
        key_hex = os.getenv(MASTER_KEY_ENV)
        if key_hex:
            _signing_key = bytes.fromhex(key_hex)
        else:
            key_path = CERTAINLOGIC_DATA / ".signing_key"
            CERTAINLOGIC_DATA.mkdir(parents=True, exist_ok=True)
            if key_path.exists():
                _signing_key = bytes.fromhex(key_path.read_text().strip())
            else:
                _signing_key = os.urandom(32)
                key_path.write_text(_signing_key.hex())
                os.chmod(key_path, 0o600)
    return _signing_key

def sign_page(slug: str, content: str, frontmatter: Optional[dict] = None,
               audit_id: Optional[str] = None) -> str:
    """HMAC-SHA256 sign a page write. Returns hex signature.
    
    Signs content_hash (stripped) + slug. Frontmatter and audit_id excluded
    because GBrain may modify both on retrieval.
    """
    key = _get_signing_key()
    content_normalized = content.strip()
    content_hash = hashlib.sha256(content_normalized.encode()).hexdigest()
    
    payload = {
        "slug": slug,
        "content_hash": content_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sig = hmac.new(key, canonical.encode(), hashlib.sha256).hexdigest()
    
    # Log to provenance DB
    PROVENANCE_DB.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "_ts": time.time(),
        "slug": slug,
        "signature": sig,
        "content_hash": content_hash,
        "audit_id": audit_id,
        "public_key_hash": hashlib.sha256(key).hexdigest()[:16],
    }
    with open(PROVENANCE_DB, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return sig

def verify_page(slug: str, content: str, frontmatter: Optional[dict] = None,
                signature: str = "", audit_id: Optional[str] = None) -> bool:
    """Verify a page's HMAC signature."""
    if not signature:
        return False
    
    key = _get_signing_key()
    content_normalized = content.strip()
    content_hash = hashlib.sha256(content_normalized.encode()).hexdigest()
    
    payload = {
        "slug": slug,
        "content_hash": content_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(key, canonical.encode(), hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def get_latest_signature(slug: str) -> Optional[str]:
    """Read the latest known signature for a slug from provenance DB."""
    if not PROVENANCE_DB.exists():
        return None
    latest = None
    with open(PROVENANCE_DB) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("slug") == slug:
                    latest = entry.get("signature")
            except json.JSONDecodeError:
                continue
    return latest

def verify_raw_page(raw_markdown: str, slug: str, expected_sig: str) -> bool:
    """Verify raw markdown against a signature (legacy compat)."""
    if not expected_sig:
        return False
    key = _get_signing_key()
    content_hash = hashlib.sha256(raw_markdown.encode()).hexdigest()
    payload = {"slug": slug, "content_hash": content_hash, "frontmatter_hash": ""}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(key, canonical.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, expected_sig)

if __name__ == "__main__":
    sig = sign_page("test/crypto", "Hello provenance", {"domain": "test"}, "audit-123")
    print(f"Signature: {sig[:16]}...")
    valid = verify_page("test/crypto", "Hello provenance", {"domain": "test"}, sig, "audit-123")
    print(f"Verify: {valid}")
