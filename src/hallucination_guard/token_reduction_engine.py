#!/usr/bin/env python3
"""
CertainLogic Verifier - Token Reduction Engine
Deterministic token budgeting, caching, and fallback summarization for LLM queries.
MIT License
"""

import hashlib
import json
import logging
import os
import re
import sqlite3
import threading
import time
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Configuration - all environment-configurable
MAX_TOKENS_PER_QUERY = int(os.getenv("TOKEN_MAX_PER_QUERY", "512"))
CACHE_SIZE_LIMIT = int(os.getenv("CACHE_SIZE_LIMIT", "1000"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
TOKEN_ESTIMATE_RATIO = float(os.getenv("TOKEN_ESTIMATE_RATIO", "0.75"))
SUMMARIZE_THRESHOLD = float(os.getenv("SUMMARIZE_THRESHOLD", "1.2"))

# SQLite cache DB path (default to local directory)
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "./cache.db")

# ---------------------------------------------------------------------------
# SQLite connection (thread-local for thread safety)
# ---------------------------------------------------------------------------
_db_lock = threading.Lock()
_thread_local = threading.local()


def _init_conn(conn: sqlite3.Connection):
    """Apply PRAGMA settings and create schema on a fresh connection."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            query_hash    TEXT PRIMARY KEY,
            result        TEXT NOT NULL,
            token_count   INTEGER NOT NULL,
            created_at    REAL NOT NULL,
            last_accessed REAL NOT NULL,
            access_count  INTEGER DEFAULT 1
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_last_accessed
        ON query_cache(last_accessed)
    """)
    conn.commit()


def _get_conn() -> sqlite3.Connection:
    """Return a per-thread SQLite connection (lazily initialised)."""
    conn = getattr(_thread_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(CACHE_DB_PATH)
        _init_conn(conn)
        _thread_local.conn = conn
    return conn


# ---------------------------------------------------------------------------
# Metrics (in-memory counters — reset on process restart, intentionally)
# ---------------------------------------------------------------------------
_cache_hits = 0
_cache_misses = 0
_total_queries = 0
_tokens_saved = 0
_metrics_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def _estimate_tokens(text: str) -> int:
    """Estimate token count using simple word-based approximation."""
    if not text:
        return 0
    words = len(re.findall(r"\b\w+\b", text))
    return int(words / TOKEN_ESTIMATE_RATIO)


def _hash_query(query: str) -> str:
    """Generate SHA-256 hash of query for cache key."""
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def _get_from_cache(query_hash: str) -> Optional[Tuple[str, int]]:
    """Retrieve cached result if exists and not expired."""
    global _cache_hits, _cache_misses
    try:
        conn = _get_conn()
        now = time.time()
        row = conn.execute(
            "SELECT result, token_count, created_at FROM query_cache WHERE query_hash = ?",
            (query_hash,),
        ).fetchone()
        if row is None:
            with _metrics_lock:
                _cache_misses += 1
            return None
        result, token_count, created_at = row
        # TTL check
        if created_at + CACHE_TTL_SECONDS < now:
            conn.execute("DELETE FROM query_cache WHERE query_hash = ?", (query_hash,))
            conn.commit()
            with _metrics_lock:
                _cache_misses += 1
            return None
        # Update access metadata
        conn.execute(
            "UPDATE query_cache SET last_accessed = ?, access_count = access_count + 1 WHERE query_hash = ?",
            (now, query_hash),
        )
        conn.commit()
        with _metrics_lock:
            _cache_hits += 1
        return result, token_count
    except sqlite3.Error as e:
        logger.warning(f"Cache read error (falling back to miss): {e}")
        with _metrics_lock:
            _cache_misses += 1
        return None


def _store_in_cache(
    query_hash: str,
    result: str,
    token_count: int,
    agent_id: str = "default",
    query_text: str = "",
):
    """Upsert result in SQLite cache, evicting LRU rows if over limit."""
    try:
        conn = _get_conn()
        now = time.time()
        conn.execute(
            """INSERT OR REPLACE INTO query_cache
               (query_hash, result, token_count, created_at, last_accessed, access_count, agent_id)
               VALUES (?, ?, ?, ?, ?, 1, ?)""",
            (query_hash, result, token_count, now, now, agent_id),
        )
        # Store the original query text for semantic lookup (best-effort)
        try:
            conn.execute(
                "UPDATE query_cache SET query=? WHERE query_hash=?",
                (query_text or result, query_hash),
            )
        except Exception:
            pass
        conn.commit()
        # LRU eviction: batch-delete bottom 10% when over limit
        count = conn.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
        if count > CACHE_SIZE_LIMIT:
            evict = max(1, int(CACHE_SIZE_LIMIT * 0.10))
            conn.execute(
                """DELETE FROM query_cache WHERE query_hash IN (
                    SELECT query_hash FROM query_cache
                    ORDER BY last_accessed ASC LIMIT ?
                )""",
                (evict,),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.warning(f"Cache write error (skipping store): {e}")


def _deterministic_fallback(query: str) -> str:
    """
    Deterministic summarization fallback when over budget.
    Uses extractive summarization: take first N sentences.
    """
    sentences = re.split(r"(?<=[.!?])\s+", query.strip())
    kept = []
    tokens_used = 0
    for sent in sentences:
        sent_tokens = _estimate_tokens(sent)
        if tokens_used + sent_tokens > MAX_TOKENS_PER_QUERY:
            break
        kept.append(sent)
        tokens_used += sent_tokens
    if not kept:
        kept = [query[: MAX_TOKENS_PER_QUERY * 4]]
    return " ".join(kept)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def reduce_tokens(
    query: str,
    force_deterministic: bool = False,
    semantic: bool = True,
    agent_id: str = "default",
) -> Dict:
    """
    Main entry point: reduce tokens in query if needed, return reduced query and metadata.

    Args:
        query: Original user query
        force_deterministic: If True, skip LLM routing and use deterministic fallback
        semantic: If True, attempt L2 semantic cache lookup on exact-hash miss
        agent_id: Optional identifier for multi‑tenant caching

    Returns:
        dict with keys:
        - 'reduced_query': query to send to LLM (or deterministic result)
        - 'original_tokens': estimated token count of original
        - 'reduced_tokens': estimated token count of reduced query
        - 'tokens_saved': difference
        - 'cache_hit': bool
        - 'semantic_hit': bool (True if result came from semantic L2 lookup)
        - 'semantic_score': float or None
        - 'method': 'cache', 'semantic', 'deterministic', or 'original'
        - 'routing': 'deterministic' or 'external' (based on force flag)
    """
    global _total_queries, _tokens_saved
    with _metrics_lock:
        _total_queries += 1

    query_hash = _hash_query(query)
    cached = _get_from_cache(query_hash)
    if cached:
        result, token_count = cached
        with _metrics_lock:
            _tokens_saved += MAX_TOKENS_PER_QUERY - token_count
        return {
            "reduced_query": result,
            "original_tokens": token_count,
            "reduced_tokens": token_count,
            "tokens_saved": MAX_TOKENS_PER_QUERY - token_count,
            "cache_hit": True,
            "semantic_hit": False,
            "semantic_score": None,
            "method": "cache",
            "routing": "deterministic",
        }

    # L2: semantic cache lookup (optional)
    if semantic:
        try:
            from semantic_cache import semantic_lookup, store_embedding

            sem_result = semantic_lookup(query)
            if sem_result:
                sem_cached, sem_score = sem_result
                sem_tokens = _estimate_tokens(sem_cached)
                with _metrics_lock:
                    _tokens_saved += MAX_TOKENS_PER_QUERY - sem_tokens
                # Promote to L1 cache for next time
                _store_in_cache(
                    query_hash,
                    sem_cached,
                    sem_tokens,
                    agent_id=agent_id,
                    query_text=query,
                )
                store_embedding(query_hash, query)
                return {
                    "reduced_query": sem_cached,
                    "original_tokens": sem_tokens,
                    "reduced_tokens": sem_tokens,
                    "tokens_saved": MAX_TOKENS_PER_QUERY - sem_tokens,
                    "cache_hit": False,
                    "semantic_hit": True,
                    "semantic_score": round(sem_score, 4),
                    "method": "semantic",
                    "routing": "deterministic",
                }
        except ImportError:
            logger.warning("semantic_cache not installed; semantic lookup disabled.")
        except Exception as e:
            logger.warning(f"Semantic lookup skipped: {e}")

    original_tokens = _estimate_tokens(query)

    if original_tokens <= MAX_TOKENS_PER_QUERY:
        _store_in_cache(
            query_hash, query, original_tokens, agent_id=agent_id, query_text=query
        )
        # Store embedding for future semantic lookups (non-blocking best-effort)
        try:
            from semantic_cache import store_embedding

            store_embedding(query_hash, query)
        except Exception:
            pass
        return {
            "reduced_query": query,
            "original_tokens": original_tokens,
            "reduced_tokens": original_tokens,
            "tokens_saved": 0,
            "cache_hit": False,
            "semantic_hit": False,
            "semantic_score": None,
            "method": "original",
            "routing": "deterministic" if force_deterministic else "external",
        }

    reduced = _deterministic_fallback(query)
    reduced_tokens = _estimate_tokens(reduced)

    _store_in_cache(
        query_hash, reduced, reduced_tokens, agent_id=agent_id, query_text=query
    )
    try:
        from semantic_cache import store_embedding

        store_embedding(query_hash, query)
    except Exception:
        pass

    tokens_saved = original_tokens - reduced_tokens
    with _metrics_lock:
        _tokens_saved += tokens_saved

    return {
        "reduced_query": reduced,
        "original_tokens": original_tokens,
        "reduced_tokens": reduced_tokens,
        "tokens_saved": tokens_saved,
        "cache_hit": False,
        "semantic_hit": False,
        "semantic_score": None,
        "method": "deterministic",
        "routing": "deterministic",
    }


def get_metrics() -> Dict:
    """Return current engine metrics for monitoring."""
    hit_rate = (
        (_cache_hits / (_cache_hits + _cache_misses)) * 100
        if (_cache_hits + _cache_misses) > 0
        else 0
    )
    avg_tokens_saved = (_tokens_saved / _total_queries) if _total_queries > 0 else 0
    try:
        cache_size = (
            _get_conn().execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
        )
    except sqlite3.Error:
        cache_size = 0
    return {
        "total_queries": _total_queries,
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "cache_hit_rate_percent": round(hit_rate, 2),
        "cache_size": cache_size,
        "total_tokens_saved": _tokens_saved,
        "average_tokens_saved_per_query": round(avg_tokens_saved, 2),
    }


def clear_cache():
    """Clear the query cache (truncate table, keep schema). Also resets in-memory counters."""
    global _cache_hits, _cache_misses, _total_queries, _tokens_saved
    try:
        conn = _get_conn()
        conn.execute("DELETE FROM query_cache")
        conn.commit()
    except sqlite3.Error as e:
        logger.warning(f"Cache clear error: {e}")
    with _metrics_lock:
        _cache_hits = _cache_misses = _total_queries = _tokens_saved = 0


def reduce(text: str) -> tuple:
    """
    Standalone pure reduce function — no cache writes, no metrics side effects.
    Returns (compressed_text, token_count).
    """
    token_count = _estimate_tokens(text)
    if token_count <= MAX_TOKENS_PER_QUERY:
        return text, token_count
    compressed = _deterministic_fallback(text)
    return compressed, _estimate_tokens(compressed)


# ---------------------------------------------------------------------------
# Persistent-cache utilities
# ---------------------------------------------------------------------------


def get_cache_stats() -> Dict:
    """Return persistent cache stats."""
    try:
        conn = _get_conn()
        row = conn.execute(
            "SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM query_cache"
        ).fetchone()
        total, oldest_ts, newest_ts = row
        now = time.time()
        db_size = os.path.getsize(CACHE_DB_PATH) if os.path.exists(CACHE_DB_PATH) else 0
        return {
            "total_entries": total or 0,
            "oldest_entry_age_seconds": round(now - oldest_ts, 2) if oldest_ts else 0.0,
            "newest_entry_age_seconds": round(now - newest_ts, 2) if newest_ts else 0.0,
            "db_size_bytes": db_size,
            "db_path": CACHE_DB_PATH,
        }
    except sqlite3.Error as e:
        logger.warning(f"get_cache_stats error: {e}")
        return {
            "total_entries": 0,
            "oldest_entry_age_seconds": 0.0,
            "newest_entry_age_seconds": 0.0,
            "db_size_bytes": 0,
            "db_path": CACHE_DB_PATH,
        }


def export_cache(path: str) -> int:
    """Export cache to a portable JSON file. Returns entry count written."""
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT query_hash, result, token_count, created_at FROM query_cache"
        ).fetchall()
        entries = [
            {"hash": r[0], "result": r[1], "token_count": r[2], "created_at": r[3]}
            for r in rows
        ]
        payload = {
            "version": "1.0",
            "exported_at": time.time(),
            "entries": entries,
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return len(entries)
    except Exception as e:
        logger.warning(f"export_cache error: {e}")
        raise


def import_cache(path: str) -> int:
    """Import cache from a JSON file (exported format). Returns entries imported. Skips duplicates."""
    try:
        with open(path, "r") as f:
            payload = json.load(f)
        entries = payload.get("entries", [])
        conn = _get_conn()
        imported = 0
        now = time.time()
        with _db_lock:
            for entry in entries:
                h = entry.get("hash")
                result = entry.get("result")
                token_count = entry.get("token_count")
                created_at = entry.get("created_at", now)
                if not h or result is None or token_count is None:
                    continue
                existing = conn.execute(
                    "SELECT 1 FROM query_cache WHERE query_hash = ?", (h,)
                ).fetchone()
                if existing:
                    continue
                conn.execute(
                    """INSERT INTO query_cache
                       (query_hash, result, token_count, created_at, last_accessed, access_count)
                       VALUES (?, ?, ?, ?, ?, 1)""",
                    (h, result, token_count, created_at, now),
                )
                imported += 1
        conn.commit()
        return imported
    except Exception as e:
        logger.warning(f"import_cache error: {e}")
        raise


if __name__ == "__main__":
    # Simple CLI for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: token_reduction_engine.py <query>")
        sys.exit(1)
    result = reduce_tokens(sys.argv[1])
    print(json.dumps(result, indent=2))
