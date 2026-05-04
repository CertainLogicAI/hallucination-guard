#!/usr/bin/env python3
"""
TRE Client v1.2.0 — Persistent Answer Cache with Hallucination Guard
==============================================================================
Caches LLM responses so repeated queries return instantly (~100ms vs 1-4s).
Hallucination Guard gates cache: uncertain answers are shown but NOT stored.
Cache persists to disk — survives process restarts.

Usage:
  tre_client cache "What is Python?" "Python is a programming language."
  tre_client get "What is Python?"
  tre_client metrics
  tre_client clear
"""

import hashlib
import json
import os
import re
import sys
import time
from collections import OrderedDict
from typing import Dict, Tuple, Optional

# ── Configuration ──────────────────────────────────────────────────────
MAX_TOKENS_PER_QUERY = 512
CACHE_SIZE_LIMIT = 1000
CACHE_TTL_SECONDS = 3600
TOKEN_ESTIMATE_RATIO = 0.75

CACHE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache_data")
CACHE_PERSISTENCE_FILE = os.path.join(CACHE_DATA_DIR, "answer_cache.json")

# ── Hallucination Guard (minimal inline, no Brain API dependency) ──────
class HallucinationGuard:
    """Minimal linguistic quality gate. Catches hedging language.
    
    LIMITATION: Only detects uncertainty patterns ("maybe", "I think").
    Does NOT verify factual truth. Confident falsehoods pass through.
    """
    UNCERTAINTY_PATTERNS = [
        r"\b(i'm not sure|i think|maybe|perhaps|could|possibly|likely)\b",
        r"\b(unsure|doubt|question)\b",
        r"\b(could be|might be|sometimes|often)\b",
        r"\b(perhaps|probably)\b",
        r"\b(not sure\s+maybe|not sure\s+or\s+maybe)\b",
        r"\b(i guess|i suppose|not certain)\b",
    ]
    
    def is_uncertain(self, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        for pattern in self.UNCERTAINTY_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

_guard = HallucinationGuard()

# ── Answer Cache State ─────────────────────────────────────────────────
_answer_cache: OrderedDict = OrderedDict()
_cache_hits = 0
_cache_misses = 0
_total_queries = 0
_flagged_count = 0

# ── Internal ───────────────────────────────────────────────────────────
def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    words = len(re.findall(r'\b\w+\b', text))
    return int(words / TOKEN_ESTIMATE_RATIO)

def _hash_query(query: str) -> str:
    return hashlib.sha256(query.encode('utf-8')).hexdigest()

def _save_cache_to_disk():
    """Persist answer cache to disk (user cache only — NOT Facts DB)."""
    try:
        os.makedirs(CACHE_DATA_DIR, exist_ok=True)
        data = {
            "entries": [
                {"q": query_hash, "a": answer, "ts": ts, "tc": tc}
                for query_hash, (answer, ts, tc) in _answer_cache.items()
            ]
        }
        with open(CACHE_PERSISTENCE_FILE, "w") as fh:
            json.dump(data, fh, indent=2)
    except Exception:
        pass

def _load_cache_from_disk():
    """Load persisted answer cache on startup."""
    global _answer_cache
    if not os.path.exists(CACHE_PERSISTENCE_FILE):
        return
    try:
        with open(CACHE_PERSISTENCE_FILE, "r") as fh:
            data = json.load(fh)
        for entry in data.get("entries", []):
            _answer_cache[entry["q"]] = (entry["a"], entry["ts"], entry["tc"])
    except Exception:
        _answer_cache.clear()

def _get_from_cache(query_hash: str) -> Optional[Tuple[str, int]]:
    global _cache_hits, _cache_misses
    if query_hash in _answer_cache:
        answer, ts, tc = _answer_cache[query_hash]
        if time.time() - ts < CACHE_TTL_SECONDS:
            _answer_cache.move_to_end(query_hash)
            _cache_hits += 1
            return answer, tc
        else:
            del _answer_cache[query_hash]
    _cache_misses += 1
    return None

def _store_in_cache(query_hash: str, answer: str, token_count: int) -> Dict:
    global _answer_cache, _flagged_count
    if _guard.is_uncertain(answer):
        _flagged_count += 1
        return {
            "cached": False,
            "flagged": True,
            "reason": "Contains uncertain language (e.g., 'maybe', 'I think', 'not sure')",
            "warning": "⚠️ Response contains hedging language. Not cached."
        }
    _answer_cache[query_hash] = (answer, time.time(), token_count)
    _answer_cache.move_to_end(query_hash)
    if len(_answer_cache) > CACHE_SIZE_LIMIT:
        _answer_cache.popitem(last=False)
    _save_cache_to_disk()
    return {"cached": True, "flagged": False, "reason": "Guard passed"}

# ── Public API ─────────────────────────────────────────────────────────
def cache_answer(query: str, answer: str) -> Dict:
    """Store an answer in the persistent cache (if Guard passes)."""
    query_hash = _hash_query(query)
    token_count = _estimate_tokens(answer)
    return _store_in_cache(query_hash, answer, token_count)

def get_cached_answer(query: str) -> Optional[Tuple[str, int]]:
    """Retrieve cached answer if exists and not expired."""
    query_hash = _hash_query(query)
    return _get_from_cache(query_hash)

def get_metrics() -> Dict:
    global _cache_hits, _cache_misses
    total = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total * 100) if total > 0 else 0
    return {
        "total_queries": total,
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "cache_hit_rate_percent": round(hit_rate, 2),
        "cache_size": len(_answer_cache),
        "flagged_responses": _flagged_count,
        "guard_loaded": True,
        "persisted": os.path.exists(CACHE_PERSISTENCE_FILE),
    }

def clear_cache():
    global _answer_cache, _cache_hits, _cache_misses, _total_queries, _flagged_count
    _answer_cache.clear()
    _cache_hits = _cache_misses = _total_queries = _flagged_count = 0
    try:
        if os.path.exists(CACHE_PERSISTENCE_FILE):
            os.remove(CACHE_PERSISTENCE_FILE)
    except Exception:
        pass

# Auto-load on import
_load_cache_from_disk()

# ── CLI ────────────────────────────────────────────────────────────────
def _cli():
    if len(sys.argv) < 2:
        print("Usage: tre_client <cache|get|metrics|clear> [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "cache":
        if len(sys.argv) < 4:
            print("Usage: tre_client cache <query> <answer>")
            sys.exit(1)
        result = cache_answer(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: tre_client get <query>")
            sys.exit(1)
        result = get_cached_answer(sys.argv[2])
        if result:
            answer, tc = result
            print(json.dumps({"cached": True, "answer": answer, "tokens": tc}, indent=2))
        else:
            print(json.dumps({"cached": False, "answer": None}, indent=2))
    
    elif cmd == "metrics":
        print(json.dumps(get_metrics(), indent=2))
    
    elif cmd == "clear":
        clear_cache()
        print(json.dumps({"cleared": True}, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: tre_client <cache|get|metrics|clear>")
        sys.exit(1)

if __name__ == "__main__":
    _cli()
