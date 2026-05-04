#!/usr/bin/env python3
"""
CertainLogic Certified Starter Pack Builder
Scans skills with Vetter Plus, bundles certified ones into 1-download pack.

Usage:
    python3 build_starter_pack.py <pack-name> <skill-dir-1> <skill-dir-2> ...
"""
import sys, os, json, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from vetter import scan_skill

def build_pack(pack_name: str, skill_dirs: list, output_dir: str = "/tmp/starter-packs"):
    """Build a starter pack from certified skills."""
    output = Path(output_dir) / pack_name
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    
    certified_skills = []
    failed_skills = []
    
    print(f"\n{'='*60}")
    print(f"Building Starter Pack: {pack_name}")
    print(f"{'='*60}\n")
    
    for skill_dir in skill_dirs:
        skill_name = Path(skill_dir).name
        print(f"Scanning: {skill_name}...", end=" ")
        
        report = scan_skill(skill_dir)
        
        if report.overall == "PASS":
            print(f"✅ CERTIFIED ({report.cert_id[:8]})")
            certified_skills.append({
                "name": skill_name,
                "path": skill_dir,
                "cert_id": report.cert_id,
            })
            # Copy skill into pack
            shutil.copytree(skill_dir, output / skill_name, dirs_exist_ok=True)
        else:
            print(f"❌ {report.overall}")
            failed_skills.append({
                "name": skill_name,
                "status": report.overall,
            })
    
    if not certified_skills:
        print("\n❌ No skills passed certification. Pack not created.")
        return None
    
    # Generate combined files
    _generate_install_script(output, certified_skills)
    _generate_readme(output, pack_name, certified_skills, failed_skills)
    _generate_manifest(output, pack_name, certified_skills)
    
    print(f"\n{'='*60}")
    print(f"✅ Pack built: {output}")
    print(f"   Skills included: {len(certified_skills)}")
    print(f"   Skills excluded: {len(failed_skills)}")
    print(f"{'='*60}\n")
    
    return output

def _generate_install_script(output: Path, skills: list):
    """Generate one-line install script for all skills."""
    script = f"""#!/bin/bash
# CertainLogic Certified Starter Pack
# Auto-generated installer — installs all certified skills

set -e
PACK_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Installing CertainLogic Certified Starter Pack ==="
echo ""
"""
    for skill in skills:
        script += f"""
echo "📦 Installing {skill['name']}..."
if [ -d "$PACK_DIR/{skill['name']}/scripts" ]; then
    cp -r "$PACK_DIR/{skill['name']}/scripts"/* "$HOME/.openclaw/skills/{skill['name']}/scripts/" 2>/dev/null || true
fi
if [ -f "$PACK_DIR/{skill['name']}/skill.json" ]; then
    mkdir -p "$HOME/.openclaw/skills/{skill['name']}"
    cp "$PACK_DIR/{skill['name']}/skill.json" "$HOME/.openclaw/skills/{skill['name']}/"
fi
echo "   ✅ {skill['name']} installed"
"""
    
    script += """
echo ""
echo "=== All skills installed ==="
echo "Run 'vetter scan <skill>' to verify any time."
"""
    
    install_path = output / "install.sh"
    install_path.write_text(script)
    install_path.chmod(0o755)

def _generate_readme(output: Path, pack_name: str, certified: list, failed: list):
    """Generate combined README for the pack."""
    lines = [
        f"# {pack_name}",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Certified Skills:** {len(certified)}",
        "",
        "## What This Is",
        "A bundle of CertainLogic Certified skills — all scanned for safety and honest claims.",
        "",
        "## Included Skills",
        "",
        "| Skill | Cert ID | Description |",
        "|-------|---------|-------------|",
    ]
    
    for skill in certified:
        skill_json = Path(skill['path']) / "skill.json"
        desc = ""
        if skill_json.exists():
            data = json.load(open(skill_json))
            desc = data.get("description", "")[:50] + "..."
        lines.append(f"| {skill['name']} | `{skill['cert_id'][:8]}` | {desc} |")
    
    if failed:
        lines.extend([
            "",
            "## Excluded (Did Not Pass)",
            "",
        ])
        for skill in failed:
            lines.append(f"- ❌ {skill['name']} — {skill['status']}")
    
    lines.extend([
        "",
        "## Quick Start",
        "```bash",
        "chmod +x install.sh && ./install.sh",
        "```",
        "",
        "## Honest Note",
        "Certified means these skills passed our automated checks. It does NOT mean they are bug-free or perfect.",
        "Always review code before installing anything.",
        "",
        "---",
        "*Built by [CertainLogic](https://certainlogic.ai)*",
    ])
    
    (output / "README.md").write_text("\n".join(lines))

def _generate_manifest(output: Path, pack_name: str, skills: list):
    """Generate pack manifest JSON."""
    manifest = {
        "name": pack_name,
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "skills": [
            {"name": s["name"], "cert_id": s["cert_id"]} for s in skills
        ],
        "certified_by": "Skill Vetter Plus v1.0",
        "disclaimer": "Automated scan only. Not a guarantee of safety.",
    }
    json.dump(manifest, open(output / "pack.json", "w"), indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: build_starter_pack.py <pack-name> <skill-dir-1> [skill-dir-2] ...")
        sys.exit(1)
    
    pack_name = sys.argv[1]
    skill_dirs = sys.argv[2:]
    build_pack(pack_name, skill_dirs)
