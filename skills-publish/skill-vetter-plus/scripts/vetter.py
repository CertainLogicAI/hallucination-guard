#!/usr/bin/env python3
"""
Skill Vetter Plus — Core Scanner
Checks ClawHub/OpenClaw skills for security, honesty, and quality issues.

Usage:
    python3 vetter.py scan <skill-id>          # Free tier: PASS/FAIL/WARN
    python3 vetter.py scan <skill-id> --pro    # Pro tier: Full report + badge
    python3 vetter.py certify <path>           # Certify a local skill
"""

import sys, os, re, json, hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# ─── Configuration ──────────────────────────────────────────────────

class VetterConfig:
    KNOWN_DOMAINS = [
        "github.com", "raw.githubusercontent.com", "pypi.org", "npmjs.com", "clawhub.ai",
        "openclaw.ai", "openrouter.ai", "anthropic.com",
        "openai.com", "googleapis.com", "x.com", "twitter.com",
        "certainlogic.ai", "img.shields.io", "badge.fury.io",
    ]

    DANGEROUS_PATTERNS = {
        "eval_execution": [r'\beval\s*\(', r'\bexec\s*\(', r'\bFunction\s*\('],
        "shell_execution": [
            r'os\.system\s*\(', r'subprocess\.(call|run)\s*\(',
            r'child_process\.(exec|execSync)\s*\('
        ],
        "false_claims": [
            r'\b100\s*%',
            r'\beliminates?\s+(?:all\s+)?(?:hallucinations?|errors?)',
            r'\bguarantees?\s+(?:accuracy|correctness|results?)',
            r'\bzero\s+(?:hallucinations?|errors?|risks?)',
            r'\b(?:always|never)\s+(?:fails?|wrong|inaccurate)',
            r'\b(?:proves?|proof\s+of)\s+(?:truth|correctness|accuracy|the\s+claim)',
            r'\b(?:cryptographic(ally)?\s+)?(?:proof|verification)\s+of\s+(?:truth|correctness)',
            r'\bdeterministic\s+(?:AI|results?|outputs?)',
            r'\b(?:completely|totally)\s+(?:secure|safe|accurate)',
        ],
    }

# ─── Models ─────────────────────────────────────────────────────────

class CheckResult:
    def __init__(self, name: str, passed: bool, findings: List[str], severity: str = "info"):
        self.name = name
        self.passed = passed
        self.findings = findings
        self.severity = severity

class ScanReport:
    def __init__(self, skill_id: str):
        self.skill_id = skill_id
        self.checks: List[CheckResult] = []
        self.overall = "PASS"
        self.timestamp = datetime.now().isoformat()
        self.cert_id = None

    def add(self, result: CheckResult):
        self.checks.append(result)
        if result.severity == "fail":
            self.overall = "FAIL"
        elif result.severity == "warn" and self.overall == "PASS":
            self.overall = "WARN"

    def generate_cert_id(self):
        h = hashlib.sha256(f"{self.skill_id}:{self.timestamp}".encode()).hexdigest()
        self.cert_id = h[:16]
        return self.cert_id

# ─── Check Functions ────────────────────────────────────────────────

def check_code_safety(content: str) -> CheckResult:
    """Check 1: Dangerous eval/exec patterns (context-aware)."""
    findings = []
    for pattern in VetterConfig.DANGEROUS_PATTERNS["eval_execution"]:
        for m in re.finditer(pattern, content, re.I):
            line = content[:m.start()].count('\n') + 1
            findings.append(f"Line {line}: eval/exec pattern")
    for pattern in VetterConfig.DANGEROUS_PATTERNS["shell_execution"]:
        for m in re.finditer(pattern, content, re.I):
            line = content[:m.start()].count('\n') + 1
            snippet = content[m.start():m.start()+200]
            if any(s in snippet for s in ['capture_output', 'timeout=', 'shell=False', 'check=']):
                continue
            findings.append(f"Line {line}: Unrestricted shell execution")
    return CheckResult("Code Safety", len(findings) == 0, findings[:5], "fail" if findings else "info")

def check_claim_honesty(readme: str) -> CheckResult:
    """Check 2: False/misleading marketing claims."""
    findings = []
    lines = readme.splitlines()
    
    # Skip lines in "does NOT", "limitations", or negative context sections
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Skip if line starts with ❌, "does not", "limitations", or is inside a "does NOT" table cell
        if ("does not" in line_lower or "limitations" in line_lower or 
            "❌" in line or "what it does **not**" in line_lower or
            line.strip().startswith("-") or line.strip().startswith("| ❌")):
            continue
        
        # Skip double-quoted phrases containing forbidden terms
        if '"' in line and ('100%' in line or 'eliminate' in line_lower):
            continue
        
        for pattern in VetterConfig.DANGEROUS_PATTERNS["false_claims"]:
            for m in re.finditer(pattern, line, re.I):
                findings.append(f"Line {i+1}: '{line.strip()}'")
    
    return CheckResult("Claim Honesty", len(findings) == 0, findings[:5], "warn" if findings else "info")

def check_network(content: str) -> CheckResult:
    """Check 3: External network calls (whitelists localhost)."""
    findings = []
    for url in re.findall(r'https?://([^/\s"\']+)', content):
        if url in ("localhost", "127.0.0.1", "0.0.0.0") or "localhost:" in url or "127.0.0.1:" in url:
            continue
        known = any(kd in url for kd in VetterConfig.KNOWN_DOMAINS)
        if not known:
            findings.append(f"Unknown domain: {url}")
    return CheckResult("Network Calls", len(findings) <= 2, findings[:5], "warn" if findings else "info")

def check_dependencies(skill_path: str) -> CheckResult:
    """Check 4: Dependency management."""
    findings = []
    req = Path(skill_path) / "requirements.txt"
    if req.exists():
        for line in open(req).readlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "==" not in line and ">=" not in line:
                findings.append(f"Unpinned: {line}")
    return CheckResult("Dependencies", len(findings) == 0, findings[:5], "warn" if findings else "info")

def check_filesystem(content: str) -> CheckResult:
    """Check 5: File system access outside workspace."""
    findings = []
    for m in re.finditer(r'open\s*\(["\']/(etc|usr|root|bin)', content, re.I):
        line = content[:m.start()].count('\n') + 1
        findings.append(f"Line {line}: System path access")
    return CheckResult("File System", len(findings) == 0, findings[:5], "warn" if findings else "info")

# ─── Scanner ────────────────────────────────────────────────────────

def scan_skill(skill_path: str, pro: bool = False) -> ScanReport:
    path = Path(skill_path)
    report = ScanReport(path.name)

    code_files = []
    for ext in ("*.py", "*.js", "*.sh"):
        for f in path.rglob(ext):
            # Skip build artifacts, caches, and test outputs
            parts = f.parts
            if any(skip in parts for skip in ['.build_output', '__pycache__', 'node_modules', '.git', 'test_output', '.pytest_cache', '.mypy_cache', 'dist', 'build']):
                continue
            if f.is_file():
                code_files.append(f)
    all_code = "\n".join(f.read_text() for f in code_files if f.is_file())

    readme_files = list(path.glob("README*")) + list(path.glob("readme*"))
    readme = readme_files[0].read_text() if readme_files else ""

    report.add(check_code_safety(all_code))
    report.add(check_claim_honesty(readme))
    report.add(check_network(all_code))
    report.add(check_filesystem(all_code))
    report.add(check_dependencies(skill_path))

    if report.overall == "PASS":
        report.generate_cert_id()

    return report

# ─── Output ─────────────────────────────────────────────────────────

def print_free(report: ScanReport):
    print(f"\n{'='*50}")
    print(f"Skill Vetter — {report.skill_id}")
    print(f"{'='*50}")
    if report.overall == "PASS":
        print("✅ PASS — Looks clean")
    elif report.overall == "WARN":
        print("⚠️  WARN — Some concerns")
        print("   Run --pro for details")
    else:
        print("❌ FAIL — Issues found")
        print("   Run --pro for details")
    print(f"{'='*50}\n")

def print_pro(report: ScanReport):
    print(f"\n{'='*60}")
    print(f"Skill Vetter Plus — Full Report")
    print(f"Skill: {report.skill_id}")
    print(f"Time: {report.timestamp}")
    print(f"{'='*60}")

    for check in report.checks:
        icon = "✅" if check.passed else ("⚠️" if check.severity == "warn" else "❌")
        print(f"\n{icon} {check.name}")
        for finding in check.findings:
            print(f"   • {finding}")
        if not check.findings:
            print("   • No issues")

    print(f"\n{'='*60}")
    if report.overall == "PASS":
        print(f"✅ CERTIFIED — CertainLogic Certified")
        print(f"Cert ID: {report.cert_id}")
        print(f"\n🏆 Badge (paste into README):")
        from badge_generator import generate_badge, save_certification
        badge = generate_badge(report.skill_id, report.cert_id)
        print(badge)
        # Save to registry
        save_certification(report.skill_id, report.cert_id, {
            "checks": [{"name": c.name, "passed": c.passed, "severity": c.severity} for c in report.checks]
        })
    else:
        print(f"❌ NOT CERTIFIED — {report.overall}")
    print(f"{'='*60}\n")

# ─── CLI ────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Vetter Plus")
    parser.add_argument("command", choices=["scan", "certify"])
    parser.add_argument("target", help="Skill path or ID")
    parser.add_argument("--pro", action="store_true", help="Full report with badge")
    parser.add_argument("--silent", action="store_true", help="Only output on failure (CI mode)")
    args = parser.parse_args()

    try:
        if args.command == "scan":
            report = scan_skill(args.target, args.pro)
            if args.silent:
                if report.overall == "PASS":
                    sys.exit(0)
                else:
                    print(f"FAIL: {report.skill_id} — {report.overall}")
                    sys.exit(1)
            else:
                if args.pro:
                    print_pro(report)
                else:
                    print_free(report)
                sys.exit(0 if report.overall == "PASS" else 1)
        elif args.command == "certify":
            report = scan_skill(args.target, pro=True)
            print_pro(report)
            if report.overall == "PASS":
                print("🏆 This skill can display the CertainLogic Certified badge")
                sys.exit(0)
            else:
                print("❌ Fix issues before certifying")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error scanning {args.target}: {e}", file=sys.stderr)
        sys.exit(126)

if __name__ == "__main__":
    main()
