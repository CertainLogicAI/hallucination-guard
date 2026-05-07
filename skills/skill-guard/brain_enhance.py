"""
Brain Enhancement: skill-guard

Enriches security scanning with brain threat patterns.
"""

import sys
from pathlib import Path

brain_path = Path("/data/.openclaw/workspace/company-brain")
if str(brain_path) not in sys.path:
    sys.path.insert(0, str(brain_path))

try:
    from brain_wrapper import Brain
    _brain = Brain()
except Exception:
    _brain = None


def get_threat_context() -> dict:
    """Query brain for security patterns to watch."""
    if _brain is None:
        return {"enhanced": False, "patterns": []}

    try:
        result = _brain.query("security patterns and anti-patterns to watch")
        if result.get("confidence", 0) > 0.2:
            return {
                "enhanced": True,
                "patterns": result.get("answer", "").split("\n"),
                "confidence": result.get("confidence", 0),
            }
    except Exception:
        pass

    return {"enhanced": False, "patterns": []}


def enhance_guard_scan(legacy_prompt: str) -> str:
    """Inject brain patterns into scan prompt."""
    result = get_threat_context()
    if result["enhanced"]:
        patterns = "\n".join(f"- {p.strip()}" for p in result["patterns"] if p.strip())
        return f"Additional Threat Patterns:\n{patterns}\n\n---\n\n{legacy_prompt}"
    return legacy_prompt
