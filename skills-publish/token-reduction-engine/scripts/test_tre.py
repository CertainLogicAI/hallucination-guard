#!/usr/bin/env python3
"""Minimal test runner for TRE CLI."""
import subprocess, json, sys, os

# Basic arg parsing
def test_basic():
    # 1. help
    r = subprocess.run([sys.executable, "scripts/hguard_client.py", "status"],
        capture_output=True, text=True, cwd="/data/.openclaw/workspace/skills-publish/token-reduction-engine")
    # status fails (no server), but should show error not crash
    assert "Brain API" in r.stdout or "unreachable" in r.stdout, f"Unexpected: {r.stdout}"
    print("✅ status OK")

    # 2. validate requires args
    r = subprocess.run([sys.executable, "scripts/hguard_client.py", "validate"],
        capture_output=True, text=True, cwd="/data/.openclaw/workspace/skills-publish/token-reduction-engine")
    assert "Usage" in r.stdout, f"Expected Usage, got: {r.stdout}"
    print("✅ validate args OK")

def test_import():
    import sys
    sys.path.insert(0, "/data/.openclaw/workspace/skills-publish/token-reduction-engine/scripts")
    from hguard_client import HGuardClient
    client = HGuardClient(api_url="http://localhost:9999")
    assert client.api_url == "http://localhost:9999"
    print("✅ import + constructor OK")

    # no default localhost without env
    os.environ.pop("CERTAINLOGIC_API", None)
    client2 = HGuardClient()
    assert client2.api_url == "http://localhost:8000"  # fallback
    print("✅ fallback OK")

if __name__ == "__main__":
    test_import()
    test_basic()
    print("\nAll tests passed.")
