#!/usr/bin/env python3
"""
Intent Classification Cache — Phase 4F

Caches query text → intent classification results.
In-memory LRU with TTL (queries re-classified if stale).

Used by brain_wrapper to avoid re-classifying identical queries.
"""

import time
from collections import OrderedDict
from typing import Optional

MAX_ENTRIES = 1000
TTL_SECONDS = 3600  # 1 hour


class IntentCache:
    """
    Thread-safe* LRU cache for intent classification results.
    
    *Note: Not strictly thread-safe. brain_wrapper uses single-threaded
calls; add threading.Lock if concurrent access needed.
    """

    def __init__(self, max_entries: int = MAX_ENTRIES, ttl: int = TTL_SECONDS):
        self.max_entries = max_entries
        self.ttl = ttl
        self._cache: OrderedDict[str, dict] = OrderedDict()

    def get(self, query_text: str) -> Optional[dict]:
        """
        Get cached intent. Returns None if miss or expired.
        
        On hit, moves key to end (LRU update).
        """
        if query_text not in self._cache:
            return None

        entry = self._cache[query_text]
        if time.time() - entry["ts"] > self.ttl:
            del self._cache[query_text]
            return None

        # LRU update: move to end
        self._cache.move_to_end(query_text)
        return entry["result"]

    def put(self, query_text: str, result: dict) -> None:
        """Store intent classification result. Evicts oldest if over limit."""
        if query_text in self._cache:
            self._cache.move_to_end(query_text)

        self._cache[query_text] = {
            "ts": time.time(),
            "result": result,
        }

        if len(self._cache) > self.max_entries:
            self._cache.popitem(last=False)

    def invalidate_all(self) -> int:
        """Clear all entries. Returns count cleared."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Remove entries matching a regex pattern (if regex module available).
        Returns count removed.
        """
        try:
            import re
            regex = re.compile(pattern)
            to_remove = [k for k in self._cache if regex.search(k)]
            for k in to_remove:
                del self._cache[k]
            return len(to_remove)
        except Exception:
            return 0

    def stats(self) -> dict:
        """Return cache statistics."""
        now = time.time()
        valid = sum(1 for e in self._cache.values() if now - e["ts"] <= self.ttl)
        expired = len(self._cache) - valid
        return {
            "total": len(self._cache),
            "valid": valid,
            "expired": expired,
            "max": self.max_entries,
            "ttl": self.ttl,
        }


# Global singleton for brain_wrapper
_intent_cache = IntentCache()


def get_intent_cache() -> IntentCache:
    """Get the global intent cache singleton."""
    return _intent_cache
