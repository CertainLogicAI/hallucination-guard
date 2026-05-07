"""
Brain Integration Shim — Shared Layer for All CertainLogic Skills

Provides optional Brain() queries with automatic fallback.
Skills import this module and use its helpers — no direct Brain() imports needed.

Usage:
    from brain_integration import get_brain_context_for_skill, brain_available

    context = get_brain_context_for_skill("cold-outreach")
    if context:
        prompt = f"{context}\n\n{legacy_prompt}"
    else:
        prompt = legacy_prompt
"""

import sys
from pathlib import Path
from typing import Optional

# Lazy singleton
_brain = None

def _load_brain():
    """Lazy-load Brain wrapper. Returns None if unavailable."""
    global _brain
    if _brain is not None:
        return _brain

    try:
        brain_path = Path("/data/.openclaw/workspace/company-brain")
        if str(brain_path) not in sys.path:
            sys.path.insert(0, str(brain_path))
        from brain_wrapper import Brain
        _brain = Brain()
        return _brain
    except Exception:
        return None


def brain_available() -> bool:
    """Check if Brain is available for queries."""
    return _load_brain() is not None


def get_brain():
    """Get the Brain singleton (or None)."""
    return _load_brain()


def safe_brain_query(query_func_name: str, *args, default: Optional[dict] = None, **kwargs) -> dict:
    """
    Execute a Brain query safely, returning default on any failure.

    Args:
        query_func_name: Method name on Brain object (query, strategy, product, etc.)
        *args: Positional args for the query
        default: Fallback dict if brain fails
        **kwargs: Keyword args for the query

    Returns:
        Brain result dict or default dict
    """
    brain = _load_brain()
    if brain is None:
        return default or {"confidence": 0, "answer": "", "sources": [], "error": "brain_unavailable"}

    try:
        func = getattr(brain, query_func_name, brain.query)
        result = func(*args, **kwargs)
        return result if result is not None else default
    except Exception as e:
        return default or {"confidence": 0, "answer": "", "sources": [], "error": str(e)}


# ─── Skill-specific context helpers ────────────────────────────────────────

def get_brain_context_for_skill(skill_name: str) -> Optional[str]:
    """
    Get brain context appropriate for a specific skill.
    Returns None if brain unavailable or no relevant info.
    """
    skill_query_map = {
        "cold-outreach": {
            "method": "strategy",
            "query": "brand voice positioning for outreach messaging",
        },
        "market-research": {
            "method": "query",
            "query": "market research methodology and data sources",
        },
        "seo": {
            "method": "query",
            "query": "SEO strategy and keyword approach",
        },
        "skill-vetter": {
            "method": "strategy",
            "query": "security policy and code review requirements",
        },
        "skill-oracle": {
            "method": "query",
            "query": "skill documentation and catalog standards",
        },
        "skill-guard": {
            "method": "query",
            "query": "security patterns and anti-patterns to watch",
        },
        "x-post-v1": {
            "method": "strategy",
            "query": "brand messaging and voice guidelines",
        },
        "x-post-v2": {
            "method": "product",
            "query": "product highlights and features to promote",
        },
        "pathfinder": {
            "method": "query",
            "query": "audit trail requirements and logging standards",
        },
    }

    mapping = skill_query_map.get(skill_name)
    if not mapping:
        return None

    result = safe_brain_query(mapping["method"], mapping["query"])
    if result.get("confidence", 0) > 0.2:
        return result.get("answer", "")

    return None


def get_brain_enhanced_prompt(skill_name: str, legacy_prompt: str) -> str:
    """
    Convenience: get brain-enhanced prompt or return legacy prompt unchanged.
    """
    context = get_brain_context_for_skill(skill_name)
    if context:
        return f"CertainLogic Context (from verified knowledge base):\n{context}\n\n---\n\n{legacy_prompt}"
    return legacy_prompt
