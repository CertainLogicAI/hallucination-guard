#!/usr/bin/env python3
"""PRE-PUBLISH AUDIT: Verify every claimed feature has working code."""
import json, sys, re, os
from pathlib import Path

def audit_skill(skill_dir):
    """Return (passed, errors)."""
    errors = []
    skill_json = Path(skill_dir) / "skill.json"
    readme = Path(skill_dir) / "README.md"
    skill_md = Path(skill_dir) / "SKILL.md"
    
    if not skill_json.exists():
        errors.append("skill.json not found")
        return False, errors
    
    data = json.load(open(skill_json))
    name = data.get("name", "unknown")
    
    # Check for hidden/unadvertised code
    repo_files = []
    for root, _, files in os.walk(skill_dir):
        for fname in files:
            repo_files.append(Path(root) / fname)
    
    advertises_cli = "scripts/" in str(data) or "entry" in data
    has_scripts_dir = (Path(skill_dir) / "scripts").exists()
    
    for f in repo_files:
        if f.suffix == ".py":
            # Is this Python file mentioned or expected?
            f_str = str(f.relative_to(skill_dir))
            if f_str.startswith("scripts/") and not advertises_cli:
                errors.append(f"Unadvertised .py file: {f_str} (scripts/ exists but skill.json doesn't mention them)")
    
    # Check for pycache
    if (Path(skill_dir) / "scripts" / "__pycache__").exists():
        errors.append("scripts/__pycache__/ found — remove before publish")
    
    for pyc in Path(skill_dir).rglob("*.pyc"):
        errors.append(f"Compiled Python file found: {pyc.relative_to(skill_dir)} — remove before publish")
    
    # Check description matches reality
    desc = data.get("description", "")
    if "knowledge base" in desc.lower() and "API" not in desc.lower():
        # Verify no API claims in docs
        for doc in [readme, skill_md]:
            if doc.exists():
                text = doc.read_text()
                if "catalog API" in text or "query engine" in text or "semantic search" in text:
                    errors.append(f"DOC CLAIMS API/ENGINE but skill.json says '{desc}'")
    
    # Check commands exist in code
    entry = data.get("entry", {})
    cli = entry.get("cli", "")
    if cli:
        cli_file = Path(skill_dir) / cli
        if not cli_file.exists():
            errors.append(f"CLI entrypoint missing: {cli}")
        else:
            code = cli_file.read_text()
            commands = data.get("commands", [])
            for cmd in commands:
                cmd_name = cmd.get("name", "")
                if cmd_name not in code:
                    errors.append(f"Command '{cmd_name}' in skill.json but NOT in {cli_file.name}")
                # Check for stub implementations
                func_match = re.search(rf'def\s+cmd_{cmd_name}\(.*?' + r'\n(    .*\n)*', code, re.DOTALL)
                if func_match:
                    func_body = func_match.group()
                    if 'print("' in func_body and 'stub' in func_body.lower():
                        errors.append(f"Command '{cmd_name}' is a STUB (prints 'stub')")
    
    passed = len(errors) == 0
    return passed, errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 prepublish_audit.py /path/to/skill")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    passed, errors = audit_skill(skill_dir)
    
    print(f"{'='*60}")
    print(f"PRE-PUBLISH AUDIT: {Path(skill_dir).name}")
    print(f"{'='*60}")
    
    if passed:
        print("✅ ALL CHECKS PASSED")
    else:
        print(f"❌ FAILED — {len(errors)} issue(s):")
        for e in errors:
            print(f"  • {e}")
        print("\nFIX BEFORE PUBLISHING.")
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
