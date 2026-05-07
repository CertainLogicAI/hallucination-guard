"""
Brain Enhancement: x-api v2 (trending posts)

Injects product highlights into trending AI post narratives.
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


def get_product_highlight() -> dict:
    """Query brain for current product positioning."""
    if _brain is None:
        return {"enhanced": False, "highlight": "", "confidence": 0}

    try:
        result = _brain.product("what product should we highlight")
        if result.get("confidence", 0) > 0.2:
            return {
                "enhanced": True,
                "highlight": result.get("answer", ""),
                "confidence": result.get("confidence", 0),
            }
    except Exception:
        pass

    return {"enhanced": False, "highlight": "", "confidence": 0}


def enhance_trending_post(post_draft: str) -> str:
    """Append product highlight to trending post if appropriate."""
    result = get_product_highlight()
    if result["enhanced"] and result["confidence"] > 0.3:
        # Only append as a closing CTA if it fits naturally
        highlight = result["highlight"].split(".")[0] + "."
        if len(post_draft) + len(highlight) < 260:
            return f"{post_draft}\n\n{highlight}"
    return post_draft
