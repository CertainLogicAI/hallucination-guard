#!/usr/bin/env python3
"""
Tests for deterministic_brain.py
Run: python3 -m pytest tests/test_deterministic_brain.py -v
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "company-brain"))

from deterministic_brain import (
    compute_hash, compute_family_hash, _store_hash, _get_stored_hash,
    verify_page_hash, check_intent, create_intent, DeterministicBrain,
    VALID_COMMANDS, gbrain_cli
)

# ── Fixtures ──────────────────────────────────────────────────────────────
class TestDeterministicBrain:
    """Comprehensive tests for deterministic company brain shim."""

    def setup_method(self):
        """Reset state before each test."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="brain_test_"))
        os.environ["CERTAINLOGIC_DATA"] = str(self.tmpdir)
        # Reset module globals by reimporting or monkeypatching
        import deterministic_brain
        deterministic_brain.CERTAINLOGIC_DATA = self.tmpdir
        deterministic_brain.INTENT_PATH = self.tmpdir / "intent"
        deterministic_brain.INTENT_PATH.mkdir(parents=True, exist_ok=True)
        deterministic_brain.HASH_DB = self.tmpdir / "page_hashes.jsonl"

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ── Hash Tests ──────────────────────────────────────────────────
    def test_compute_hash_consistent(self):
        """Same inputs produce same hash."""
        h1 = compute_hash("Hello world", {"type": "note"})
        h2 = compute_hash("Hello world", {"type": "note"})
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex length

    def test_compute_hash_different(self):
        """Different inputs produce different hashes."""
        h1 = compute_hash("Hello")
        h2 = compute_hash("World")
        assert h1 != h2

    def test_compute_hash_content_matters(self):
        """Content changes hash."""
        h1 = compute_hash("A", {"x": 1})
        h2 = compute_hash("B", {"x": 1})
        assert h1 != h2

    def test_compute_hash_frontmatter_matters(self):
        """Frontmatter changes hash."""
        h1 = compute_hash("A", {"x": 1})
        h2 = compute_hash("A", {"x": 2})
        assert h1 != h2

    def test_compute_family_hash_consistent(self):
        """Family hash deterministic for same members."""
        h1 = compute_family_hash(["a", "b"], ["hash1", "hash2"])
        h2 = compute_family_hash(["a", "b"], ["hash1", "hash2"])
        assert h1 == h2

    def test_compute_family_hash_different(self):
        """Different family = different root hash."""
        h1 = compute_family_hash(["a"], ["hash1"])
        h2 = compute_family_hash(["a", "b"], ["hash1", "hash2"])
        assert h1 != h2

    # ── Hash Storage Tests ──────────────────────────────────────────
    def test_store_and_get_hash(self):
        """Store hash, retrieve it later."""
        _store_hash("test/page", "content", {"type": "note"})
        stored = _get_stored_hash("test/page")
        assert stored is not None
        assert len(stored) == 64

    def test_get_hash_missing(self):
        """Missing slug returns None."""
        result = _get_stored_hash("nonexistent")
        assert result is None

    def test_store_overwrites(self):
        """Latest store wins for same slug."""
        _store_hash("page", "v1")
        _store_hash("page", "v2")  # overwrite
        # get_stored_hash returns LAST match
        stored = _get_stored_hash("page")
        expected = compute_hash("v2")
        assert stored == expected

    def test_store_includes_family_and_audit(self):
        """Store includes metadata."""
        _store_hash("page", "c", family="fam1", audit_id="audit123")
        # Verify by reading raw JSONL
        with open(os.environ["CERTAINLOGIC_DATA"] + "/page_hashes.jsonl") as f:
            entry = json.loads(f.readlines()[-1])
        assert entry["slug"] == "page"
        assert entry["family"] == "fam1"
        assert entry["audit_id"] == "audit123"
        assert "_ts" in entry

    # ── Verify Page Tests ───────────────────────────────────────────
    def test_verify_valid_content(self):
        """Unchanged content verifies."""
        content = "Original content"
        fm = {"type": "note"}
        _store_hash("page", content, fm)
        valid, stored, computed = verify_page_hash("page", content, fm)
        assert valid is True
        assert stored == computed

    def test_verify_tampered_content(self):
        """Tampered content fails verification."""
        content = "Original content"
        _store_hash("page", content)
        valid, stored, computed = verify_page_hash("page", "Tampered", {})
        assert valid is False
        assert stored != computed

    def test_verify_never_stored(self):
        """Never-stored page can't verify."""
        valid, stored, computed = verify_page_hash("newpage", "content", {})
        assert valid is False
        assert stored == ""  # Never stored = empty
        assert len(computed) == 64

    # ── Intent Tests ────────────────────────────────────────────────
    def test_intent_blocks_forbidden(self):
        """Globally forbidden commands blocked."""
        allowed, reason = check_intent("brain.delete_brain", {}, "any")
        assert allowed is False
        assert "globally forbidden" in reason

    def test_intent_allows_read(self):
        """Read ops allowed without intent."""
        allowed, reason = check_intent("brain.query", {"query": "x"}, "default")
        assert allowed is True
        assert "read-only" in reason

    def test_intent_blocks_mutate_without_domain(self):
        """Mutating ops blocked if no intent exists."""
        allowed, reason = check_intent("brain.put_page", {"slug": "x"}, "unknown_domain")
        assert allowed is False
        assert "No intent defined" in reason

    def test_intent_allows_in_list(self):
        """Allowed ops pass when intent exists."""
        create_intent("testdomain", ["brain.query"], ["brain.put_page"], ["source"])
        allowed, reason = check_intent("brain.query", {"query": "x", "source": "s"}, "testdomain")
        assert allowed is True
        assert "Intent check passed" in reason

    def test_intent_blocks_not_in_list(self):
        """Ops not in allowed list blocked."""
        create_intent("testdomain", ["brain.query"], [], [])
        allowed, reason = check_intent("brain.put_page", {"slug": "x"}, "testdomain")
        assert allowed is False
        assert "not in allowed list" in reason

    def test_intent_blocks_by_forbidden_list(self):
        """Ops in forbidden list blocked even if not otherwise restricted."""
        create_intent("testdomain", ["brain.query", "brain.put_page"], ["brain.put_page"], [])
        allowed, reason = check_intent("brain.put_page", {"slug": "x"}, "testdomain")
        assert allowed is False
        assert "forbidden by intent" in reason

    def test_intent_checks_required_fields(self):
        """Missing required fields blocked."""
        create_intent("testdomain", ["brain.query"], [], ["source"])
        allowed, reason = check_intent("brain.query", {"query": "x"}, "testdomain")  # missing source
        assert allowed is False
        assert "Missing required field" in reason

    # ── Command Validation Tests ────────────────────────────────────
    def test_unknown_command_rejected(self):
        """Unknown commands return error."""
        brain = DeterministicBrain()
        result = brain.command("brain.unknown", {})
        assert result["success"] is False
        assert "Unknown command" in result["error"]
        assert "audit_id" in result

    def test_valid_command_checks_intent(self):
        """Valid command still blocked by intent."""
        create_intent("readonly", ["brain.query"], ["brain.put_page"], [])
        brain = DeterministicBrain(domain="readonly")
        result = brain.command("brain.put_page", {"slug": "x", "content": "y", "source": "s"})
        assert result["success"] is False
        assert "blocked" in result.get("error", "").lower() or "forbidden" in result.get("error", "").lower()

    # ── Audit Tests ─────────────────────────────────────────────────
    def test_audit_entry_format(self):
        """Audit entries contain required fields."""
        brain = DeterministicBrain()
        result = brain.command("brain.unknown", {})
        # Check audit log
        audit_file = Path(os.environ["CERTAINLOGIC_DATA"]) / "audit.jsonl"
        assert audit_file.exists()
        with open(audit_file) as f:
            entry = json.loads(f.readlines()[-1])
        assert "_ts" in entry
        assert "domain" in entry
        assert "cmd" in entry
        assert entry["cmd"] == "brain.unknown"

    def test_audit_id_unique(self):
        """Different calls get different audit IDs."""
        brain = DeterministicBrain()
        r1 = brain.command("brain.unknown", {})
        r2 = brain.command("brain.unknown", {})
        assert r1["audit_id"] != r2["audit_id"]

    # ── create_intent Tests ─────────────────────────────────────────
    def test_create_intent_file(self):
        """Intent file created with correct format."""
        path = create_intent("mydomain", ["a"], ["b"], ["c"], "Desc")
        assert Path(path).exists()
        content = Path(path).read_text()
        assert "allowed_ops: a" in content
        assert "forbidden_ops: b" in content
        assert "required_fields: c" in content
        assert "Desc" in content

    def test_create_intent_parsed_back(self):
        """Created intent can be parsed."""
        from deterministic_brain import get_intent, _parse_intent
        create_intent("roundtrip", ["op1", "op2"], ["op3"], ["field1"], "Test desc")
        intent = get_intent("roundtrip")
        assert intent is not None
        assert "op1" in intent["allowed_ops"]
        assert "op3" in intent["forbidden_ops"]
        assert "field1" in intent["required_fields"]


# ── Live GBrain Integration (Optional) ────────────────────────
class TestLiveGBrainIntegration:
    """Skipped if GBrain not installed — these hit the real PGLite DB."""

    def setup_method(self):
        self.brain = DeterministicBrain(domain="test")
        # Probe gbrain availability
        result = gbrain_cli(["--help"])
        self.gbrain_available = result.get("success", False) and "gbrain" in result.get("output", "")

    def test_live_put_and_get(self):
        if not self.gbrain_available:
            pytest.skip("GBrain not installed or not configured")
        
        # Create intent for test domain to allow put_page
        create_intent("test", ["brain.put_page", "brain.get_page"], [], [])
        
        slug = f"live-test-{time.time():.0f}"
        content = "Live integration test page."
        
        # PUT
        result = self.brain.command("brain.put_page", {
            "slug": slug,
            "content": content,
            "frontmatter": {"domain": "test"},
            "source": "test"
        })
        assert result["success"], f"Put failed: {result.get('error')}"
        assert "hash" in result
        
        # VERIFY (get + hash + HMAC check)
        verify = self.brain.verify(slug)
        assert verify.get("hash_verified"), f"Hash mismatch: stored={verify['stored_hash']}, computed={verify['computed_hash']}"
        assert verify["stored_hash"] == result["hash"], "Stored hash should match returned hash"
        assert verify.get("hmac_signature") is not None, "HMAC signature should be stored in frontmatter"
        assert verify.get("hmac_verified"), "HMAC should verify successfully"

# ── Run directly ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
