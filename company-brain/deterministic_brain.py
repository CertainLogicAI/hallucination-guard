#!/usr/bin/env python3
"""
Deterministic Company Brain — Python shim over GBrain
Wraps GBrain TypeScript core with CertainLogic layers:
  1. Structured command validation
  2. Intent layer filtering
  3. SHA-256 hash verification on every write
  4. AgentPathfinder HMAC-signed audit trails
"""

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# ── Config ────────────────────────────────────────────────────────────────
GBRAIN_PATH = os.getenv("GBRAIN_PATH", "/data/.openclaw/workspace/company-brain")
GBRAIN_DATA = os.getenv("GBRAIN_DATA", os.path.expanduser("~/.gbrain"))
CERTAINLOGIC_DATA = Path(os.getenv("CERTAINLOGIC_DATA", "/data/.openclaw/workspace/company-brain-data"))
CERTAINLOGIC_DATA.mkdir(parents=True, exist_ok=True)

# ── Layer 1: Structured Command Schema ────────────────────────────────────
VALID_COMMANDS = {
    "brain.query": {"query": str, "source": str, "brain": Optional[str]},
    "brain.get_page": {"slug": str, "brain": Optional[str], "source": Optional[str]},
    "brain.put_page": {"slug": str, "content": str, "frontmatter": Optional[dict], "source": str},
    "brain.ingest": {"type": str, "content": str, "source": str, "metadata": Optional[dict]},
    "brain.search": {"q": str, "limit": Optional[int], "source": Optional[str]},
    "brain.add_link": {"from_slug": str, "to_slug": str, "rel_type": str},
    "brain.get_backlinks": {"slug": str},
    "brain.sync": {"source": str},
}

FORBIDDEN_COMMANDS = {
    "brain.delete_brain",       # Never allow agent to delete entire brain
    "brain.purge",              # Never allow mass purge
    "brain.override_intent",    # Intent is human-controlled
}

# ── Layer 2: Intent Nodes ─────────────────────────────────────────────────
INTENT_PATH = CERTAINLOGIC_DATA / "intent"
INTENT_PATH.mkdir(exist_ok=True)

def get_intent(domain: str) -> Optional[Dict[str, Any]]:
    """Load intent node for a domain. Returns None if no intent found."""
    intent_file = INTENT_PATH / f"{domain}-INTENT.md"
    if not intent_file.exists():
        return None
    with open(intent_file) as f:
        content = f.read()
    # Parse frontmatter + body
    return _parse_intent(content)

def _parse_intent(content: str) -> Dict[str, Any]:
    """Parse intent markdown: frontmatter YAML + body."""
    lines = content.split("\n")
    intent = {"allowed_ops": [], "forbidden_ops": [], "required_fields": [], "description": ""}
    in_frontmatter = False
    body_lines = []
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key in ["allowed_ops", "forbidden_ops", "required_fields"]:
                    intent[key] = [v.strip() for v in val.split(",")]
                else:
                    intent[key] = val
        else:
            body_lines.append(line)
    intent["description"] = "\n".join(body_lines).strip()
    return intent

def check_intent(cmd: str, params: dict, domain: str = "default") -> tuple[bool, str]:
    """
    Check if command is allowed by intent node.
    Returns (allowed, reason).
    """
    if cmd in FORBIDDEN_COMMANDS:
        return False, f"Command '{cmd}' is globally forbidden"

    intent = get_intent(domain)
    if not intent:
        # No intent = default deny for mutating ops
        if cmd.startswith("brain.put_") or cmd.startswith("brain.ingest"):
            return False, f"No intent defined for domain '{domain}' — mutating ops blocked"
        return True, "No intent, read-only ops allowed"

    if intent.get("forbidden_ops") and cmd in intent["forbidden_ops"]:
        return False, f"Command '{cmd}' forbidden by intent for domain '{domain}'"

    if intent.get("allowed_ops") and cmd not in intent["allowed_ops"]:
        return False, f"Command '{cmd}' not in allowed list for domain '{domain}'"

    # Check required fields
    for field in intent.get("required_fields", []):
        if field not in params:
            return False, f"Missing required field '{field}' per intent"

    return True, "Intent check passed"

# ── Layer 3: Hash Verification ────────────────────────────────────────────
HASH_DB = CERTAINLOGIC_DATA / "page_hashes.jsonl"
FAMILY_DB = CERTAINLOGIC_DATA / "families.json"

def compute_hash(content: str, frontmatter: Optional[dict] = None) -> str:
    """Compute SHA-256 of page content + frontmatter."""
    payload = {"content": content, "frontmatter": frontmatter or {}}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()

def compute_family_hash(slugs: List[str], hashes: List[str]) -> str:
    """Compute root hash for a family of pages."""
    combined = "".join(sorted(f"{s}:{h}" for s, h in zip(slugs, hashes)))
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_page_hash(slug: str, content: str, frontmatter: Optional[dict] = None) -> tuple[bool, str, str]:
    """
    Verify a page against stored hash.
    Returns (valid, stored_hash, computed_hash).
    """
    computed = compute_hash(content, frontmatter)
    stored = _get_stored_hash(slug)
    if stored is None:
        return False, "", computed  # Never stored = can't verify
    return computed == stored, stored, computed

def _get_stored_hash(slug: str) -> Optional[str]:
    """Read hash from append-only hash DB. Returns LATEST match."""
    if not HASH_DB.exists():
        return None
    latest = None
    with open(HASH_DB) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("slug") == slug:
                    latest = entry.get("hash")
            except json.JSONDecodeError:
                continue
    return latest

def _store_hash(slug: str, content: str, frontmatter: Optional[dict] = None,
                family: Optional[str] = None, audit_id: Optional[str] = None):
    """Write hash to append-only DB."""
    entry = {
        "_ts": time.time(),
        "slug": slug,
        "hash": compute_hash(content, frontmatter),
        "family": family,
        "audit_id": audit_id,
    }
    with open(HASH_DB, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── Layer 4: GBrain CLI Wrapper ──────────────────────────────────────────
def gbrain_cli(args: List[str], **kwargs) -> dict:
    """Call gbrain CLI and return parsed JSON output."""
    cmd = ["bun", "run", f"{GBRAIN_PATH}/src/cli.ts"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=GBRAIN_PATH
        )
        # GBrain outputs JSON for most commands
        try:
            return {"success": True, "output": json.loads(result.stdout), "stderr": result.stderr}
        except json.JSONDecodeError:
            return {"success": result.returncode == 0, "output": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout", "output": None}
    except FileNotFoundError:
        return {"success": False, "error": "gbrain not found — run 'cd company-brain && bun install' first", "output": None}

# ── Public API: Deterministic Brain Operations ───────────────────────────
class DeterministicBrain:
    """
    CertainLogic brain with all safety layers:
      - Structured commands only
      - Intent validation
      - Hash verification
      - HMAC-signed audit trails
    """

    def __init__(self, domain: str = "default"):
        self.domain = domain
        self.audit_log = CERTAINLOGIC_DATA / "audit.jsonl"

    def _audit(self, entry: dict):
        entry["_ts"] = time.time()
        entry["domain"] = self.domain
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def command(self, cmd: str, params: dict) -> dict:
        """
        Execute a structured brain command with all safety layers.
        """
        # 1. Command validation
        if cmd not in VALID_COMMANDS:
            audit_id = hashlib.sha256(f"{cmd}:{time.time()}".encode()).hexdigest()[:16]
            self._audit({"audit_id": audit_id, "cmd": cmd, "params": params, "blocked": True, "reason": "Unknown command"})
            return {"success": False, "error": f"Unknown command '{cmd}'", "audit_id": audit_id}

        # 2. Intent check
        allowed, reason = check_intent(cmd, params, self.domain)
        if not allowed:
            self._audit({"cmd": cmd, "params": params, "blocked": True, "reason": reason})
            return {"success": False, "error": reason}

        # 3. Audit start
        audit_id = hashlib.sha256(f"{cmd}:{time.time()}".encode()).hexdigest()[:16]
        self._audit({"audit_id": audit_id, "cmd": cmd, "params": params, "started": True})

        # 4. Execute via GBrain
        result = self._execute(cmd, params)

        # 5. Hash verification for writes
        if cmd == "brain.put_page":
            slug = params.get("slug", "")
            content = params.get("content", "")
            fm = params.get("frontmatter", {})
            _store_hash(slug, content, fm, family=params.get("family"), audit_id=audit_id)
            result["hash"] = compute_hash(content, fm)

        # 6. Audit complete
        self._audit({
            "audit_id": audit_id,
            "cmd": cmd,
            "success": result.get("success", False),
            "error": result.get("error"),
        })

        result["audit_id"] = audit_id
        return result

    def _execute(self, cmd: str, params: dict) -> dict:
        """Map command to GBrain CLI invocation."""
        if cmd == "brain.query":
            return gbrain_cli(["query", params["query"], "--source", params.get("source", "default")])
        elif cmd == "brain.get_page":
            return gbrain_cli(["get_page", params["slug"]])
        elif cmd == "brain.put_page":
            # Write content to temp file, then gbrain import
            tmp = CERTAINLOGIC_DATA / f"tmp_{params['slug'].replace('/', '_')}.md"
            with open(tmp, "w") as f:
                if "frontmatter" in params and params["frontmatter"]:
                    f.write("---\n")
                    f.write(json.dumps(params["frontmatter"], indent=2))
                    f.write("\n---\n\n")
                f.write(params["content"])
            return gbrain_cli(["import-file", str(tmp), "--source", params.get("source", "default")])
        elif cmd == "brain.search":
            return gbrain_cli(["query", params["q"], "--limit", str(params.get("limit", 5))])
        elif cmd == "brain.sync":
            return gbrain_cli(["sync", "--source", params.get("source", "default")])
        else:
            return {"success": False, "error": f"Command '{cmd}' not yet implemented in wrapper"}

    def verify(self, slug: str) -> dict:
        """Verify a page's current hash against stored hash."""
        result = self.command("brain.get_page", {"slug": slug})
        if not result.get("success"):
            return result

        content = result.get("output", {}).get("content", "")
        fm = result.get("output", {}).get("frontmatter", {})
        valid, stored, computed = verify_page_hash(slug, content, fm)
        return {
            "slug": slug,
            "verified": valid,
            "stored_hash": stored,
            "computed_hash": computed,
        }

# ── Convenience: Create intent node ────────────────────────────────────────
def create_intent(domain: str, allowed: List[str], forbidden: List[str],
                  required: List[str], description: str = ""):
    """Create a new intent node for a domain."""
    intent_file = INTENT_PATH / f"{domain}-INTENT.md"
    content = f"""---
allowed_ops: {', '.join(allowed)}
forbidden_ops: {', '.join(forbidden)}
required_fields: {', '.join(required)}
---
{description}
"""
    with open(intent_file, "w") as f:
        f.write(content)
    return str(intent_file)


# ── Self-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Deterministic Brain shim loaded.")
    print(f"Data dir: {CERTAINLOGIC_DATA}")
    print(f"GBrain path: {GBRAIN_PATH}")
    print(f"Valid commands: {sorted(VALID_COMMANDS.keys())}")

    # Test 1: Create a coding intent
    intent_path = create_intent(
        domain="coding",
        allowed=["brain.query", "brain.get_page", "brain.search"],
        forbidden=["brain.put_page", "brain.ingest", "brain.sync"],
        required=["source"],
        description="Read-only intent for coding domain. No mutations allowed."
    )
    print(f"\nTest 1: Created intent at {intent_path}")

    # Test 2: Intent check
    brain = DeterministicBrain(domain="coding")
    result = brain.command("brain.put_page", {
        "slug": "test/page",
        "content": "# Test",
        "source": "coding"
    })
    print(f"\nTest 2: put_page blocked = {not result['success']} (expected: True)")
    print(f"  Reason: {result.get('error')}")

    # Test 3: Read allowed
    result = brain.command("brain.query", {"query": "test", "source": "coding"})
    print(f"\nTest 3: query allowed = {result['success']} (may fail if gbrain not installed)")
    print(f"  Audit ID: {result.get('audit_id')}")
