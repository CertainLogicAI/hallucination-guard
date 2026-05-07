"""
Brain Enhancement: x-api v1 (slot-based posting)

Enriches slot-based X posts with brand messaging from the brain.
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


def get_brand_voice(slot: str = "default") -> dict:
    """Query brain for brand voice appropriate to slot."""
    if _brain is None:
        return {"enhanced": False, "voice": "", "confidence": 0}

    try:
        result = _brain.strategy("brand messaging and voice guidelines")
        if result.get("confidence", 0) > 0.2:
            return {
                "enhanced": True,
                "voice": result.get("answer", ""),
                "confidence": result.get("confidence", 0),
            }

        # Fallback
        result = _brain.strategy("brand voice default")
        if result.get("confidence", 0) > 0.2:
            return {
                "enhanced": True,
                "voice": result.get("answer", ""),
                "confidence": result.get("confidence", 0),
            }
    except Exception:
        pass

    return {"enhanced": False, "voice": "", "confidence": 0}


def enhance_slot_post(legacy_post: str, slot: str = "default") -> str:
    """Inject brand voice guidance into post content if available."""
    result = get_brand_voice(slot)
    if result["enhanced"]:
        voice_line = result["voice"].split("\n")[0]
        return f"{voice_line}\n\n{legacy_post}"
    return legacy_post
