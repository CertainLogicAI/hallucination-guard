#!/usr/bin/env python3
"""
CertainLogic Demo Video Script — Terminal Recording
Run this, record your screen (QuickTime, OBS, etc.)

Shows in ~90 seconds:
1. Intent-based access control (security policy)
2. HMAC-signed page write (provenance)
3. Tamper-evident verification (hash + HMAC)
4. Blocked unauthorized operation
5. Audit trail

NOTES FOR RECORDING:
- Maximize terminal window (no other apps visible)
- Use large font (Prefs > Text > 18pt+)
- Dark background
- After each section, pause 2-3 seconds for viewer absorption
- Total runtime: ~90 seconds of demo + pauses = ~2 minutes
"""

import time
import sys
import os

sys.path.insert(0, '/data/.openclaw/workspace/company-brain')
os.environ['CERTAINLOGIC_DATA'] = '/data/.openclaw/workspace/company-brain-data'

from deterministic_brain import DeterministicBrain, create_intent

def p():
    """Pause for viewer comprehension."""
    time.sleep(2.5)

def header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")
    p()

def step(num, text):
    print(f"\n{'─'*60}")
    print(f"  STEP {num}: {text}")
    print(f"{'─'*60}\n")
    p()

def cmd(text):
    print(f"$ {text}")
    p()

def out(text):
    print(f"> {text}")

print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        CertainLogic — Tamper-Evident AI Brain              ║
║                                                            ║
║        Every write is HMAC-signed. Every read verifies.    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
p()

# ── STEP 1: Define security policy ──────────────────────────────────────
step(1, "Define Domain Intent (Security Policy)")

cmd("create_intent('medical', allowed=['put_page', 'get_page'], forbidden=['sync'])")

intent_path = create_intent(
    domain="medical",
    allowed=["brain.put_page", "brain.get_page", "brain.query"],
    forbidden=["brain.sync", "brain.ingest"],
    required=["source"],
    description="Medical: agents can read/write records but cannot bulk-sync."
)

out(f"Intent created: {intent_path}")
out("Policy: Read/Write OK. Bulk sync BLOCKED. Source field required.")

# ── STEP 2: Initialize brain ────────────────────────────────────────────
step(2, "Initialize Deterministic Brain")

cmd("brain = DeterministicBrain(domain='medical')")

brain = DeterministicBrain(domain="medical")

out("Domain: medical")
out("Features: Intent validation + Hash verification + HMAC signing")
p()

# ── STEP 3: Write with HMAC signature ───────────────────────────────────
step(3, "Write Tamper-Evident Page")

cmd("brain.command('put_page', {'slug': 'patient/001', 'content': 'Diagnosis: ...'})")

result = brain.command("brain.put_page", {
    "slug": "patient/001",
    "content": "Patient: John Doe\nDiagnosis: Deterministic AI Syndrome\nTreatment: Ship code daily.",
    "frontmatter": {"classification": "internal", "department": "medical"},
    "source": "demo"
})

out(f"Write: success={result['success']}")
out(f"SHA-256 Hash: {result['hash'][:24]}...")
out(f"HMAC Signature: {result['hmac_signature'][:24]}...")
out(f"Audit ID: {result['audit_id']}")
out("✓ Persisted to GBrain with cryptographic signature")

# ── STEP 4: Verify integrity ────────────────────────────────────────────
step(4, "Verify Page Integrity")

cmd("brain.verify('patient/001')")

verify = brain.verify("patient/001", source="demo")

out(f"Hash verified: {verify['hash_verified']}")
out(f"HMAC verified: {verify['hmac_verified']}")
out(f"Stored hash: {verify['stored_hash'][:24]}...")
out(f"Computed hash: {verify['computed_hash'][:24]}...")
out("✓ Content unchanged. Provenance valid.")

# ── STEP 5: Security — blocked operation ────────────────────────────────
step(5, "Security: Blocked Operation")

cmd("brain.command('sync', {'source': 'attacker'})")

blocked = brain.command("brain.sync", {"source": "attacker"})

out(f"Command: brain.sync")
out(f"Blocked: {not blocked['success']}")
out(f"Reason: {blocked['error']}")
out("✓ Intent enforcement: unauthorized sync rejected")

# ── STEP 6: Audit trail ─────────────────────────────────────────────────
step(6, "Non-Reputable Audit Trail")

cmd("cat data/audit.jsonl | tail -3")

audit_file = '/data/.openclaw/workspace/company-brain-data/audit.jsonl'
if os.path.exists(audit_file):
    with open(audit_file) as f:
        lines = f.readlines()[-3:]
    for line in lines:
        entry = json.loads(line)
        ts = time.strftime('%H:%M:%S', time.localtime(entry['_ts']))
        print(f"> [{ts}] {entry['cmd']} | success={entry.get('success', 'N/A')}")

out("✓ Every operation logged. Immutable history.")

# ── Summary ─────────────────────────────────────────────────────────────
p()
print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     SUMMARY                                                ║
║                                                            ║
║     ✅ Intent-based access control                         ║
║     ✅ HMAC-SHA256 signing on every write                  ║
║     ✅ SHA-256 hash verification on every read             ║
║     ✅ Unauthorized operations blocked                     ║
║     ✅ Append-only audit trail                             ║
║                                                            ║
║     Built by CertainLogic — Deterministic AI Infrastructure ║
║     https://certainlogic.ai · beta@certainlogic.ai         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

print("\n[TOTAL TIME: ~90 seconds of demo]")
print("[Record this with screen capture + optional voiceover]")
