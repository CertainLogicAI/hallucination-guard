#!/usr/bin/env python3
"""
Key Registry Verifier — Run this before claiming any key status.
Checks all known credential locations and reports actual findings.
"""

import json
import os
import subprocess
from pathlib import Path

REGISTRY = Path("/data/.openclaw/workspace/KEY_REGISTRY.json")

def check_github_tokens():
    """Check all git repos for embedded tokens."""
    found = []
    workspace = Path("/data/.openclaw/workspace")
    
    for git_dir in workspace.rglob(".git"):
        if not git_dir.is_dir():
            continue
        config = git_dir / "config"
        if not config.exists():
            continue
            
        text = config.read_text(errors="ignore")
        # Look for ghp_ tokens in git remotes
        import re
        tokens = re.findall(r'ghp_[A-Za-z0-9_]+', text)
        for token in tokens:
            repo = git_dir.parent.name
            found.append({"repo": repo, "token": token, "source": str(config)})
    
    return found

def check_file_keys():
    """Check secrets directory and other known locations."""
    found = []
    
    # X credentials
    x_file = Path("/data/.openclaw/workspace/secrets/x_credentials.json")
    if x_file.exists():
        content = x_file.read_text()
        if "YOUR_API_KEY_HERE" in content:
            found.append({"service": "X_API", "status": "PLACEHOLDER", "file": str(x_file)})
        else:
            found.append({"service": "X_API", "status": "CONFIGURED", "file": str(x_file)})
    
    # Key registry itself
    if REGISTRY.exists():
        found.append({"service": "KEY_REGISTRY", "status": "EXISTS", "file": str(REGISTRY)})
    
    return found

def verify():
    print("=" * 60)
    print("KEY REGISTRY VERIFICATION")
    print("=" * 60)
    print()
    
    # Check GitHub tokens in git configs
    print("GitHub Tokens (from git remotes):")
    gh_tokens = check_github_tokens()
    if gh_tokens:
        for t in gh_tokens:
            print(f"  ✓ {t['repo']}: ghp_...{t['token'][-6:]} (in {t['source']})")
    else:
        print("  ✗ None found in any .git/config")
    print()
    
    # Check file-based keys
    print("File-based Credentials:")
    files = check_file_keys()
    if files:
        for f in files:
            status_icon = "✓" if f['status'] == "CONFIGURED" else "⚠"
            print(f"  {status_icon} {f['service']}: {f['status']} ({f['file']})")
    else:
        print("  ✗ None found")
    print()
    
    # Load registry to show expected vs actual
    if REGISTRY.exists():
        try:
            reg = json.load(open(REGISTRY))
            print("Registered Services:")
            for service, info in reg.items():
                if isinstance(info, dict) and 'status' in info:
                    print(f"  • {service}: {info['status']}")
            print()
        except:
            pass
    
    print("=" * 60)
    print("Run this script before making ANY claims about key availability.")
    print("Reported above = ACTUAL state. No assumptions.")
    print("=" * 60)

if __name__ == "__main__":
    verify()
