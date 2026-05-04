"""Token Reduction Engine v1.2.0 — Persistent Answer Cache with Hallucination Guard"""

from .tre_client import (
    cache_answer,
    get_cached_answer,
    get_metrics,
    clear_cache,
)

__version__ = "1.2.0"
__all__ = ["cache_answer", "get_cached_answer", "get_metrics", "clear_cache"]
