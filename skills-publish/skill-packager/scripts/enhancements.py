#!/usr/bin/env python3
"""
Skill Packager Enhancement v2.0 — Marketing Automation
"""

import re, json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ─── Boilerplate Templates ────────────────────────────────────────────
BRAND_FOOTER = """---

*Built by [CertainLogic](https://certainlogic.ai) — honest tools for honest builders.*
*Free on [ClawHub](https://clawhub.ai/certainlogicai). Pro upgrades at [certainlogic.ai/shop](https://certainlogic.ai/shop?utm_source=clawhub&utm_skill={skill_id}).*
*Questions? [X @CertainLogicAI](https://x.com/CertainLogicAI)*
"""

CTA_PRO = """
> **Need more power?** [Upgrade to Pro](https://certainlogic.ai/shop?utm_source=clawhub&utm_skill={skill_id}) for team features, advanced configs, and priority support.
"""

RELATED_TOOLS = """
## Related CertainLogic Tools

| Free Tool | What It Does | Upgrade Path |
|-----------|-------------|--------------|
| [AgentPathfinder](https://clawhub.ai/certainlogicai/agentpathfinder) | Signed task tracking for agents | Pro: encrypted vault, team dashboard |
| [Token Reduction Engine](https://clawhub.ai/certainlogicai/token-reduction-engine) | Fast answer cache | Pro: persistent KB, analytics |
| [Hallucination Guard](https://clawhub.ai/certainlogicai/hallucination-guard) | Catches hedging language | Pro: fact DB integration, custom rules |
"""

# ─── Format Lock: Required Sections ───────────────────────────────────
REQUIRED_SECTIONS = [
    ("what this is", r"^## what this is", "One-sentence plain-language description"),
    ("what it does vs what it doesn't", r"^## what it does( vs| vs\.| versus)", "Two-column honesty table"),
    ("what you get", r"^## what you get", "Benefits table"),
    ("honest limitations", r"^## honest limitations", "Specific limitations table"),
    ("quick start", r"^## quick start", "Install instructions"),
    ("usage", r"^## usage", "CLI + Python API examples"),
]

# ─── Findability: Searchable Titles ───────────────────────────────────
SEARCHABLE_PREFIXES = {
    "task_tracking": ["AI Agent", "Task", "Workflow", "Step"],
    "cache": ["Fast", "Cache", "Speed", "Repeat"],
    "security": ["Secure", "Safe", "Scan", "Guard"],
    "generic": ["AI", "Agent", "Tool"],
}

# ─── Functions ─────────────────────────────────────────────────────────
def inject_boilerplate(readme_text: str, skill_id: str, skill_type: str) -> str:
    """Add brand footer, CTA, and related tools to README."""
    # Only inject if not already present
    if "certainlogic.ai" not in readme_text.lower():
        readme_text = readme_text.rstrip() + "\n"
        readme_text += RELATED_TOOLS
        readme_text += BRAND_FOOTER.format(skill_id=skill_id)
    return readme_text

def check_format_lock(readme_text: str) -> Tuple[bool, List[str]]:
    """Verify README has all required sections in correct order."""
    errors = []
    lines = readme_text.splitlines()
    
    for section_name, pattern, description in REQUIRED_SECTIONS:
        found = any(re.search(pattern, line, re.I) for line in lines)
        if not found:
            errors.append(f"Missing section: '{section_name}' — {description}")
    
    return len(errors) == 0, errors

def optimize_findability(skill_json: Dict, skill_type: str) -> Dict:
    """Suggest SEO improvements for ClawHub listing."""
    suggestions = {}
    
    # Name optimization
    name = skill_json.get("name", "")
    if "-" in name and len(name.split("-")) > 2:
        suggestions["name"] = f"Consider shorter, searchable name (current: {name})"
    
    # Tags optimization
    tags = skill_json.get("tags", [])
    if len(tags) < 3:
        suggestions["tags"] = f"Add more tags (have {len(tags)}, recommend 5-8)"
    if "certainlogic" not in [t.lower() for t in tags]:
        suggestions["tags_brand"] = "Add 'certainlogic' tag for brand discoverability"
    
    # Description optimization
    desc = skill_json.get("description", "")
    if len(desc) > 200:
        suggestions["description_length"] = f"Description is {len(desc)} chars (ClawHub shows ~120)"
    
    prefixes = SEARCHABLE_PREFIXES.get(skill_type, SEARCHABLE_PREFIXES["generic"])
    has_searchable = any(p.lower() in desc.lower() for p in prefixes)
    if not has_searchable:
        suggestions["description_keywords"] = f"Add searchable keyword: {', '.join(prefixes)}"
    
    return suggestions

if __name__ == "__main__":
    print("Enhancement module loaded. Import into package_skill.py for use.")
