#!/usr/bin/env python3
"""
IP Leak Guard v2 — Smart Content Checker
Distinguishes marketing references (allowed) from executable Pro code (blocked).
"""

import re, sys, json
from pathlib import Path
from typing import List, Tuple, Set

# ─── What to Block in CODE FILES (never in free packages) ────────────
EXECUTABLE_PRO_PATTERNS = [
    # API infrastructure
    r"api[_-]?key\s*[=:]\s*[\"'][a-zA-Z0-9_\-]{20,}",
    r"auth[_-]?token\s*[=:]\s*[\"'][a-zA-Z0-9_\-]{20,}",
    r"bearer\s+[a-zA-Z0-9_\-]{20,}",
    # Payment / billing code
    r"stripe[_-]?(key|secret|api|webhook)",
    r"payment[_-]?intent",
    r"checkout[_-]?session",
    r"billing[_-]?(api|endpoint|webhook)",
    # Internal infrastructure
    r"api\.certainlogic\.ai",
    r"internal[_-]?endpoint",
    r"prod[_-]?(url|host|server)",
    # License enforcement code
    r"license[_-]?key",
    r"activation[_-]?code",
    r"verify[_-]?license",
    r"check[_-]?subscription",
]

# ─── What to Warn About (even in docs) ───────────────────────────────
SENSITIVE_TERMS = [
    "license key", "activation code", "verify license",
    "check subscription", "billing api", "stripe secret",
]

# ─── Files That Are Code (strict) ────────────────────────────────────
CODE_EXTENSIONS = {"py", "js", "ts", "sh", "bash", "rb", "go", "rs", "java", "cpp", "c"}

# ─── Files That Are Config/Data (moderate) ──────────────────────────
CONFIG_EXTENSIONS = {"json", "yml", "yaml", "toml"}

# ─── Files That Are Docs (allow marketing, moderate on internals) ────
DOC_EXTENSIONS = {"md", "rst", "txt"}

def determine_file_type(fpath: Path) -> str:
    """Classify file for checking strictness."""
    ext = fpath.suffix.lstrip(".").lower()
    if ext in CODE_EXTENSIONS:
        return "code"
    elif ext in CONFIG_EXTENSIONS:
        return "config"
    elif ext in DOC_EXTENSIONS:
        return "doc"
    return "other"

def scan_skill_directory(skill_dir: str, is_free: bool = True) -> Tuple[bool, List[str], List[str]]:
    """Check if free package contains executable Pro code.
    
    Returns: (passed, blocked_items, warnings)
    """
    if not is_free:
        return True, [], []
    
    blocked: List[str] = []
    warnings: List[str] = []
    skill_path = Path(skill_dir)
    
    if not skill_path.exists():
        return False, [f"Directory not found: {skill_dir}"], []
    
    # Patterns that auto-fail regardless of file type
    for fpath in skill_path.rglob("*"):
        if not fpath.is_file():
            continue
        if any(part.startswith(".") for part in fpath.relative_to(skill_path).parts):
            continue
        
        file_type = determine_file_type(fpath)
        text = fpath.read_text(errors="ignore")
        rel = fpath.relative_to(skill_path)
        
        # ALL file types: check executable pro patterns
        for pattern in EXECUTABLE_PRO_PATTERNS:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                blocked.append(f"{rel} [{file_type}]: Pro code detected → {m}")
        
        # Config files: extra checks for infrastructure leaks
        if file_type == "config":
            # Allow price references in paid_products section, block elsewhere
            if fpath.suffix == ".json":
                try:
                    data = json.loads(text)
                    # Check if skills section contains paid-only features
                    for skill in data.get("skills", []):
                        if any(p in str(skill).lower() for p in ["license", "activation", "stripe", "billing"]):
                            blocked.append(f"{rel} [config]: Free skill references paid infrastructure")
                except json.JSONDecodeError:
                    pass
    
    passed = len(blocked) == 0
    if blocked:
        warnings.append(f"BLOCKED: {len(blocked)} executable pro feature(s) found in free package.")
    
    return passed, blocked, warnings

def generate_report(skill_dir: str, passed: bool, blocked: List[str], warnings: List[str]) -> str:
    """Generate a human-readable report."""
    lines = [
        "=" * 60,
        "IP LEAK GUARD v2 — REPORT",
        f"Package: {Path(skill_dir).name}",
        f"Status: {'✅ PASSED' if passed else '❌ BLOCKED'}",
        "=" * 60,
        "",
    ]
    
    lines.append("RULES:")
    lines.append("  ✓ Marketing references to Pro tier → ALLOWED (docs only)")
    lines.append("  ✗ Executable Pro code in free package → BLOCKED (any file)")
    lines.append("  ✗ API keys, Stripe integration, license enforcement → BLOCKED")
    lines.append("")
    
    if blocked:
        lines.append(f"BLOCKED ITEMS ({len(blocked)}):")
        for item in blocked:
            lines.append(f"  • {item}")
        lines.append("")
    
    if warnings:
        lines.append("WARNINGS:")
        for w in warnings:
            lines.append(f"  ⚠ {w}")
        lines.append("")
    
    if passed:
        lines.append("✓ No executable pro features or protected IP detected.")
        lines.append("✓ Marketing references to Pro tier are acceptable.")
        lines.append("✓ Safe to publish as free package.")
    else:
        lines.append("ACTION REQUIRED:")
        lines.append("  1. Remove or comment out all blocked pro code")
        lines.append("  2. Keep marketing references if they stay in docs only")
        lines.append("  3. Re-run IP Leak Guard")
        lines.append("  4. Only publish after PASS")
    
    return "\n".join(lines)

def cli():
    import argparse
    parser = argparse.ArgumentParser(description="IP Leak Guard v2 — Prevent pro code from leaking into free packages")
    parser.add_argument("skill_dir", help="Path to skill source directory")
    parser.add_argument("--pro", action="store_true", help="Treat as pro/paid package (skip checks)")
    parser.add_argument("--json", action="store_true", help="Output as JSON for CI integration")
    args = parser.parse_args()
    
    is_free = not args.pro
    passed, blocked, warnings = scan_skill_directory(args.skill_dir, is_free)
    
    if args.json:
        result = {
            "passed": passed,
            "is_free": is_free,
            "blocked_count": len(blocked),
            "blocked_items": blocked,
            "warnings": warnings,
            "rules": "Marketing references allowed. Executable pro code blocked."
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if passed else 1)
    else:
        report = generate_report(args.skill_dir, passed, blocked, warnings)
        print(report)
        sys.exit(0 if passed else 1)

if __name__ == "__main__":
    cli()
