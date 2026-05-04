#!/usr/bin/env python3
"""
Skill Packaging Automation v1.0 — Internal Process
--------------------------------------------------
Automates the CertainLogic marketplace packaging workflow:
  1. Fetch marketplace rules
  2. Validate skill structure against rules
  3. Simplify language (jargon-free benefits)
  4. Generate submission-ready package
  5. Pre-flight checklist before publish

Usage:
    python3 package_skill.py /path/to/skill-source /path/to/output

Rules enforced:
- No jargon in README (HMAC, cryptographic, deterministic, etc.)
- Benefits table must be present and plain-language
- Honesty section required ("What it does NOT do")
- All marketplace-required files present
- Semver versioning
"""

import sys, os, json, re, shutil, argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ─── Configuration ─────────────────────────────────────────────────
REQUIRED_FILES = ["skill.json", "README.md", "SAFETY.md"]
REQUIRED_SKILL_FIELDS = ["id", "name", "version", "description"]

JARGON_PATTERNS = [
    (r"\bHMAC[- ]SHA[- ]?256\b", "Use 'signed' or 'proof of who said what'"),
    (r"\bcryptographic(cally)?\b", "Use 'secure' or 'tamper-proof'"),
    (r"\bciphertext\b", "Remove entirely — users don't need to know this"),
    (r"\bshard\b", "Use 'part of the key' or remove"),
    (r"\bXOR\b", "Remove entirely — implementation detail"),
    (r"\bidempotency\b", "Use 'safe to run twice' or remove"),
    (r"\bdeterministic\b", "Use 'consistent' or explain without the word"),
    (r"\batomic(ity)?\b", "Use 'all-or-nothing' or remove"),
    (r"\badvisory (lock|file)\b", "Use 'prevents conflicts' or remove"),
    (r"\btamper[- ]evident\b", "Use 'tamper-proof' or 'shows if edited'"),
    (r"\bcrash recovery\b", "Use 'resume where you left off'"),
    (r"\bproof of\b", "Use 'shows who' or 'records what'"),
    (r"\bzero[- ]dependency\b", "Use 'works offline' or 'no install needed'"),
]

BENEFITS_SECTION_PATTERNS = [
    r"^## [Bb]enefits",
    r"^## [Ww]hat [Yy]ou [Gg]et",
    r"^## [Ff]eatures",
]

# ─── Helpers ──────────────────────────────────────────────────────────
def _error(msg: str):
    print(f"  ❌ {msg}")

def _ok(msg: str):
    print(f"  ✅ {msg}")

def _warn(msg: str):
    print(f"  ⚠️  {msg}")

def _header(title: str):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def _subheader(title: str):
    print(f"\n── {title} ──")

# ─── Phase 1: Fetch Marketplace Rules ─────────────────────────────────
def fetch_marketplace_rules(marketplace: str) -> Dict:
    """Return minimum requirements for known marketplaces."""
    rules = {
        "clawhub": {
            "required_files": ["skill.json", "README.md"],
            "required_skill_fields": ["id", "displayName", "version", "description"],
            "optional": ["repository", "license", "author", "entrypoints", "exports", "safety"],
            "max_description_length": 500,
            "requires_semver": True,
        },
        "skillsmp": {
            "required_files": ["README.md"],
            "required_yaml_fields": ["name", "author", "repository", "description"],
            "optional": ["tags", "license"],
        },
        "lobehub": {
            "required_files": ["README.md"],
            "max_description": 200,
        },
        "generic": {
            "required_files": REQUIRED_FILES,
            "required_skill_fields": REQUIRED_SKILL_FIELDS,
            "optional": ["repository", "license", "author"],
        },
    }
    return rules.get(marketplace, rules["generic"])

# ─── Phase 2: Validate Structure ──────────────────────────────────────
def validate_skill_structure(skill_dir: str, rules: Dict) -> Tuple[bool, List[str]]:
    """Check skill directory against marketplace rules."""
    errors = []
    warnings = []
    skill_path = Path(skill_dir)
    
    for fname in rules.get("required_files", REQUIRED_FILES):
        fpath = skill_path / fname
        if not fpath.exists():
            errors.append(f"Missing required file: {fname}")
        elif fpath.stat().st_size == 0:
            errors.append(f"Empty file: {fname}")
    
    skill_json = skill_path / "skill.json"
    if skill_json.exists():
        try:
            data = json.load(open(skill_json))
            for field in rules.get("required_skill_fields", REQUIRED_SKILL_FIELDS):
                if field not in data:
                    errors.append(f"skill.json missing '{field}'")
            if rules.get("requires_semver") and "version" in data:
                version = data["version"]
                if not re.match(r"^\d+\.\d+\.\d+$", version):
                    errors.append(f"Invalid semver: {version}")
            if "description" in data:
                desc = data["description"]
                for pattern, suggestion in JARGON_PATTERNS:
                    if re.search(pattern, desc, re.I):
                        warnings.append(f"skill.json description jargon: {pattern} — {suggestion}")
        except json.JSONDecodeError as e:
            errors.append(f"skill.json invalid JSON: {e}")
    
    return len(errors) == 0, errors + warnings

# ─── Phase 3: Language Simplification Audit ────────────────────────────
def audit_readme_language(readme_path: str) -> Tuple[List[str], List[str]]:
    """Check README for jargon and missing benefits sections."""
    errors = []
    suggestions = []
    
    if not Path(readme_path).exists():
        return ["README.md not found"], []
    
    text = open(readme_path).read()
    lines = text.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        for pattern, suggestion in JARGON_PATTERNS:
            match = re.search(pattern, line, re.I)
            if match:
                errors.append(f"Line {line_num}: Jargon '{match.group(0)}' — {suggestion}")
    
    has_benefits = any(re.search(p, line) for p in BENEFITS_SECTION_PATTERNS for line in lines)
    if not has_benefits:
        suggestions.append("README missing benefits/features section. Add '## What You Get' with plain-language benefits.")
    
    if "what it does not" not in text.lower() and "does not" not in text.lower():
        suggestions.append("README missing limitations/honesty section. Add a clear table of what the tool does NOT do.")
    
    return errors, suggestions

# ─── Phase 4: Benefits Template Generator ─────────────────────────────
def generate_benefits_template(skill_type: str) -> str:
    """Return a benefits section template based on skill category."""
    templates = {
        "task_tracking": """
## What You Get (Free Forever)

| Feature | What It Means |
|---------|-------------|
| ✅ **Unlimited tasks** | Make as many checklists as you want. No caps. |
| 🔒 **Proof of who did what** | Every step is signed. You know which agent worked on what. |
| 📋 **Tamper-proof records** | If someone edits the history, you'll know. |
| 🔄 **Resume where you left off** | If your process gets interrupted, pick up from the exact step. |
| 🖥️ **Dashboard** (static) | One-page report of all tasks. No server needed. |
| 🧠 **Optional integrations** | Connects to your knowledge base if you have one. |
""",
        "cache": """
## What You Get (Free Forever)

| Feature | What It Means |
|---------|-------------|
| ⚡ **Instant repeat answers** | Same question → instant return. No waiting. |
| 💰 **Zero cost for repeats** | No API tokens spent on cache hits. |
| 📊 **Consistent results** | Same question → same answer, every time. |
| 🛡️ **Quality guard** | Uncertain answers are shown but NOT cached. |
| 💾 **Survives restarts** | Cache persists to disk. No warm-up needed. |
""",
        "security": """
## What You Get (Free Forever)

| Feature | What It Means |
|---------|-------------|
| 🔍 **Scan anything** | Checks skills/apps before you install them. |
| 🛡️ **Catch problems early** | Flags risky code before it runs on your system. |
| 📊 **Clear scores** | PASS / WARNING / BLOCK — easy to understand. |
| 🔒 **No server needed** | Runs on your machine. Your data stays local. |
""",
        "generic": """
## What You Get

| Feature | What It Means |
|---------|-------------|
| [Feature 1] | [Plain-language benefit] |
| [Feature 2] | [Plain-language benefit] |
""",
    }
    return templates.get(skill_type, templates["generic"])

# ─── Phase 5: Package Builder ────────────────────────────────────────
def build_package(skill_dir: str, output_dir: str, marketplace: str = "generic"):
    """Copy skill to output, injecting standardization."""
    _header(f"Building package for: {marketplace}")
    
    src = Path(skill_dir)
    dst = Path(output_dir)
    dst.mkdir(parents=True, exist_ok=True)
    
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            tgt = dst / rel
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, tgt)
    
    _ok(f"Copied all files to {output_dir}")
    
    checklist = generate_preflight_checklist(marketplace)
    checklist_path = dst / "PUBLISH_CHECKLIST.md"
    checklist_path.write_text(checklist)
    _ok(f"Generated PUBLISH_CHECKLIST.md")
    
    return True

# ─── Phase 6: Install Script Generation ───────────────────────────────
def generate_install_script(skill_dir: str, output_dir: str):
    """Generate one-line install script if skill doesn't have one."""
    src = Path(skill_dir)
    dst = Path(output_dir)
    
    # Check if install.sh already exists
    existing = src / "install.sh"
    if existing.exists():
        shutil.copy2(existing, dst / "install.sh")
        _ok("Found existing install.sh — copied to output")
        return
    
    # Try to detect main script from skill.json
    entry = "main.py"  # default
    skill_json = src / "skill.json"
    if skill_json.exists():
        try:
            data = json.load(open(skill_json))
            # Try to find entrypoint
            if "entry" in data and isinstance(data["entry"], dict):
                cmd = data["entry"].get("command", [])
                if cmd:
                    entry = cmd[-1]  # last element is usually the script
            elif "entry" in data and isinstance(data["entry"], str):
                entry = data["entry"]
            elif "bin" in data and isinstance(data["bin"], dict):
                entry = list(data["bin"].values())[0]
        except Exception:
            pass
    
    # Find the script in scripts/ directory
    scripts_dir = src / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        if py_files:
            # Prefer one that matches the detected entry, else first
            entry_file = None
            for f in py_files:
                if entry in f.name:
                    entry_file = f.name
                    break
            if not entry_file:
                entry_file = py_files[0].name
            entry = f"scripts/{entry_file}"
    
    script_name = Path(entry).stem
    
    install_sh = f'''#!/usr/bin/env bash
# {script_name} — One-line installer
# Usage: curl -fsSL <url> | bash

set -e

REPO="https://raw.githubusercontent.com/CertainLogicAI/{script_name}/main"
SCRIPT_URL="${{REPO}}/{entry}"

echo "=== {script_name} Installer ==="
echo ""

# Detect install target
if [ -w /usr/local/bin ]; then
    BIN_DIR="/usr/local/bin"
elif [ -d "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
else
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

# Download
INSTALL_PATH="${{BIN_DIR}}/{script_name}"
echo "→ Downloading to ${{INSTALL_PATH}} ..."

if command -v curl >/dev/null 2>&1; then
    curl -fsSL "${{SCRIPT_URL}}" -o "${{INSTALL_PATH}}"
elif command -v wget >/dev/null 2>&1; then
    wget -q "${{SCRIPT_URL}}" -O "${{INSTALL_PATH}}"
else
    echo "❌ curl or wget required."
    exit 1
fi

chmod +x "${{INSTALL_PATH}}"

# Verify Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 not found. Install Python 3.10+ and retry."
    exit 1
fi

echo ""
echo "✅ Installed: ${{INSTALL_PATH}}"
echo ""

# Check PATH
if [[ ":$PATH:" != *":${{BIN_DIR}}:"* ]]; then
    echo "⚠️  ${{BIN_DIR}} is not in your PATH."
    echo "   Add this to ~/.bashrc or ~/.zshrc:"
    echo "      export PATH=\"${{BIN_DIR}}:\$PATH\""
    echo ""
fi

echo "Test it: {script_name} --help"
'''
    
    script_path = dst / "install.sh"
    script_path.write_text(install_sh)
    script_path.chmod(0o755)
    _ok(f"Generated install.sh for one-line curl | bash install")
    _warn(f"Update SCRIPT_URL in install.sh with your actual repo URL")

def check_install_documentation(readme_path: str) -> Tuple[bool, List[str]]:
    """Check if README documents low-friction install methods."""
    if not Path(readme_path).exists():
        return False, ["README.md not found"]
    
    text = open(readme_path).read().lower()
    issues = []
    
    if "curl" not in text and "pip install" not in text and "clawhub install" not in text:
        issues.append("README missing install instructions. Add one-line install, pip, or ClawHub.")
    
    if "pip install" in text and "curl" not in text:
        issues.append("README has pip install but no one-line curl option. Add curl | bash for lowest friction.")
    
    has_quickstart = "## quick start" in text or "## install" in text or "## getting started" in text
    if not has_quickstart:
        issues.append("README missing Quick Start or Install section. Users need to know how to begin.")
    
    return len(issues) == 0, issues
    rules = fetch_marketplace_rules(marketplace)
    lines = ["# Pre-flight Checklist", f"Marketplace: **{marketplace}**", "", "## Before You Publish", ""]
    lines.append("- [ ] Anton has personally installed and tested the product")
    lines.append("- [ ] Every claimed feature has been verified by Anton")
    lines.append("- [ ] No jargon in README (no HMAC, cryptographic, deterministic, etc.)")
    lines.append("- [ ] Benefits table is clear and simple")
    lines.append("- [ ] 'What It Does NOT' table is present and honest")
    lines.append("- [ ] No '100%', 'eliminates', 'guarantees', 'proves' language")
    lines.append("- [ ] Version follows semver (X.Y.Z)")
    lines.append("- [ ] skill.json is valid JSON")
    lines.append("- [ ] All required files present:")
    for f in rules.get("required_files", REQUIRED_FILES):
        lines.append(f"  - [ ] `{f}`")
    lines.append("")
    lines.append("## After Publish")
    lines.append("")
    lines.append("- [ ] Test install from marketplace (not dev environment)")
    lines.append("- [ ] Verify listed features work from clean install")
    lines.append("- [ ] Monitor for issues for 48 hours")
    lines.append("")
    lines.append("---")
    lines.append("*Generated by CertainLogic Skill Packager v1.0*")
    return "\n".join(lines)

def generate_preflight_checklist(marketplace: str) -> str:
    rules = fetch_marketplace_rules(marketplace)
    lines = ["# Pre-flight Checklist", f"Marketplace: **{marketplace}**", "", "## Before You Publish", ""]
    lines.append("- [ ] Anton has personally installed and tested the product")
    lines.append("- [ ] Every claimed feature has been verified by Anton")
    lines.append("- [ ] No jargon in README (no HMAC, cryptographic, deterministic, etc.)")
    lines.append("- [ ] Benefits table is clear and simple")
    lines.append("- [ ] 'What It Does NOT' table is present and honest")
    lines.append("- [ ] No '100%', 'eliminates', 'guarantees', 'proves' language")
    lines.append("- [ ] Version follows semver (X.Y.Z)")
    lines.append("- [ ] skill.json is valid JSON")
    lines.append("- [ ] All required files present:")
    for f in rules.get("required_files", REQUIRED_FILES):
        lines.append(f"  - [ ] `{f}`")
    lines.append("")
    lines.append("## After Publish")
    lines.append("")
    lines.append("- [ ] Test install from marketplace (not dev environment)")
    lines.append("- [ ] Verify listed features work from clean install")
    lines.append("- [ ] Monitor for issues for 48 hours")
    lines.append("")
    lines.append("---")
    lines.append("*Generated by CertainLogic Skill Packager v2.0*")
    return "\n".join(lines)

# ─── CLI ──────────────────────────────────────────────────────────────
def cli():
    parser = argparse.ArgumentParser(
        description="Package CertainLogic skills for marketplace publication"
    )
    parser.add_argument("source", help="Path to skill source directory")
    parser.add_argument("output", help="Path to output directory")
    parser.add_argument("--marketplace", default="clawhub",
                         choices=["clawhub", "skillsmp", "lobehub", "generic"],
                         help="Target marketplace (default: clawhub)")
    parser.add_argument("--skill-type", default="generic",
                         choices=["task_tracking", "cache", "security", "generic"],
                         help="Category for benefits template")
    args = parser.parse_args()
    
    _header("CertainLogic Skill Packager v1.0")
    
    _subheader("Phase 1: Marketplace Rules")
    rules = fetch_marketplace_rules(args.marketplace)
    _ok(f"Loaded rules for {args.marketplace}")
    print(f"  Required files: {rules.get('required_files', [])}")
    
    _subheader("Phase 2: Structure Validation")
    valid, issues = validate_skill_structure(args.source, rules)
    for issue in issues:
        if "Missing" in issue or "Empty" in issue or "invalid" in issue.lower():
            _error(issue)
        else:
            _warn(issue)
    if not valid:
        print("\n❌ Validation FAILED. Fix errors before packaging.")
        sys.exit(1)
    _ok("Structure validation passed")
    
    _subheader("Phase 3: Language Audit")
    readme_path = Path(args.source) / "README.md"
    jargon_errors, suggestions = audit_readme_language(str(readme_path))
    if jargon_errors:
        for e in jargon_errors:
            _error(e)
        print("\n❌ Jargon found. Simplify language before packaging.")
        sys.exit(1)
    if suggestions:
        for s in suggestions:
            _warn(s)
    _ok("Language audit passed")
    
    _subheader("Phase 4: Format Lock Check")
    from enhancements import check_format_lock
    format_ok, format_errors = check_format_lock(open(readme_path).read())
    if format_errors:
        for e in format_errors:
            _warn(e)
    else:
        _ok("Format lock: all required sections present")
    
    _subheader("Phase 5: Benefits Template")
    benefits = generate_benefits_template(args.skill_type)
    template_path = Path(args.output) / "BENEFITS_TEMPLATE.md"
    print(f"  Generated {args.skill_type} benefits template")
    _warn("Paste the appropriate benefits table into README.md before publishing")
    
    _subheader("Phase 6: Build Package")
    build_package(args.source, args.output, args.marketplace)
    
    _subheader("Phase 7: Install Script Generation")
    generate_install_script(args.source, args.output)
    
    _subheader("Phase 8: Install Documentation Check")
    install_ok, install_issues = check_install_documentation(readme_path)
    if install_issues:
        for issue in install_issues:
            _warn(issue)
    else:
        _ok("README has install instructions")
    
    _subheader("Phase 9: Boilerplate Injection")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from enhancements import inject_boilerplate, optimize_findability
        
        skill_json_path = Path(args.source) / "skill.json"
        skill_id = "unknown"
        if skill_json_path.exists():
            data = json.load(open(skill_json_path))
            skill_id = data.get("id", data.get("name", "unknown"))
        
        # Inject boilerplate into README
        readme_text = open(readme_path).read()
        enhanced = inject_boilerplate(readme_text, skill_id, args.skill_type)
        if enhanced != readme_text:
            enhanced_path = Path(args.output) / "README.md"
            enhanced_path.write_text(enhanced)
            _ok("Brand boilerplate injected into README.md")
        else:
            _ok("Brand boilerplate already present")
        
        # Findability optimizer
        if skill_json_path.exists():
            data = json.load(open(skill_json_path))
            suggestions = optimize_findability(data, args.skill_type)
            if suggestions:
                _warn("Findability suggestions:")
                for k, v in suggestions.items():
                    print(f"    [{k}] {v}")
            else:
                _ok("Findability optimized")
        
    except ImportError:
        _warn("enhancements.py not found — skipping boilerplate injection")
    except Exception as e:
        _warn(f"Boilerplate injection error: {e}")
    
    _header("Packaging Complete")
    _ok(f"Output: {args.output}")
    _ok(f"Marketplace: {args.marketplace}")
    print(f"\n📦 Package includes:")
    print(f"  • All skill files (copied from source)")
    print(f"  • PUBLISH_CHECKLIST.md (Anton verification checklist)")
    print(f"  • BENEFITS_TEMPLATE.md (copy-paste into README)")
    print(f"  • install.sh (one-line curl | bash script)")
    print(f"  • README.md (with CertainLogic brand boilerplate)")
    print(f"\nNext steps:")
    print(f"  1. Update install.sh SCRIPT_URL with your actual GitHub repo URL")
    print(f"  2. Review BENEFITS_TEMPLATE.md in output folder")
    print(f"  3. Paste benefits table into README.md")
    print(f"  4. Complete PUBLISH_CHECKLIST.md")
    print(f"  5. Await Anton's explicit 'approved' after 24-hour hold")
    print(f"  6. Publish via: clawhub publish {args.output}")

if __name__ == "__main__":
    cli()
