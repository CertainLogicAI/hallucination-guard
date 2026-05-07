#!/usr/bin/env python3
"""
Query Result Cache — Phase 4F

Caches full query results (query_text + detail_level + limit → results).
SQLite on disk with TTL. Invalidated on brain write operations.

Why SQLite not in-memory: cache must survive brain_wrapper restarts
and be shared across skill processes.
"""

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB = "/data/.openclaw/workspace/company-brain-data/query_cache.db"
TTL_SECONDS = 300  # 5 minutes
MAX_ENTRIES = 10000


class QueryCache:
    """
    Disk-backed cache for brain query results with TTL and size limits.
    """

    def __init__(self, db_path: str = DEFAULT_DB, ttl: int = TTL_SECONDS, max_entries: int = MAX_ENTRIES):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.max_entries = max_entries
        self._init_db()

    def _init_db(self):
        """Create cache table if not exists."""
        with sqlite3.connect(self.db_path, timeout=5) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_cache (
                    key TEXT PRIMARY KEY,
                    result TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created ON query_cache(created_at)"
            )
            conn.commit()

    def _make_key(self, query_text: str, detail_level: str, limit: int) -> str:
        """Hash the query parameters into a cache key."""
        raw = f"{query_text}|{detail_level}|{limit}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, query_text: str, detail_level: str = "auto", limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached query result. Returns None if miss or expired.
        Also increments access_count for LRU eviction.
        """
        key = self._make_key(query_text, detail_level, limit)

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            row = conn.execute(
                "SELECT result, created_at FROM query_cache WHERE key = ?",
                (key,),
            ).fetchone()

            if not row:
                return None

            result_json, created_at = row
            if time.time() - created_at > self.ttl:
                conn.execute("DELETE FROM query_cache WHERE key = ?", (key,))
                conn.commit()
                return None

            # Update access count
            conn.execute(
                "UPDATE query_cache SET access_count = access_count + 1 WHERE key = ?",
                (key,),
            )
            conn.commit()

            return json.loads(result_json)

    def put(self, query_text: str, result: List[Dict[str, Any]], detail_level: str = "auto", limit: int = 10) -> None:
        """Store query result. Evicts oldest entries if over limit."""
        key = self._make_key(query_text, detail_level, limit)
        result_json = json.dumps(result, default=str)
        now = int(time.time())

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO query_cache (key, result, created_at, access_count)
                VALUES (?, ?, ?, 0)""",
                (key, result_json, now),
            )

            # Size enforcement: evict oldest records by created_at
            count = conn.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
            if count > self.max_entries:
                excess = count - self.max_entries
                conn.execute(
                    "DELETE FROM query_cache WHERE key IN (SELECT key FROM query_cache ORDER BY created_at ASC LIMIT ?)",
                    (excess,),
                )

            conn.commit()

    def invalidate_all(self) -> int:
        """Clear all entries. Returns count cleared."""
        with sqlite3.connect(self.db_path, timeout=5) as conn:
            count = conn.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
            conn.execute("DELETE FROM query_cache")
            conn.commit()
            return count

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        with sqlite3.connect(self.db_path, timeout=5) as conn:
            total = conn.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
            if total == 0:
                return {"total": 0, "valid": 0, "expired": 0, "max": self.max_entries, "ttl": self.ttl}

            now = int(time.time())
            valid = conn.execute(
                "SELECT COUNT(*) FROM query_cache WHERE ? - created_at <= ?",
                (now, self.ttl),
            ).fetchone()[0]

            return {
                "total": total,
                "valid": valid,
                "expired": total - valid,
                "max": self.max_entries,
                "ttl": self.ttl,
            }


# Global singleton for brain_wrapper
_query_cache = QueryCache()


def get_query_cache() -> QueryCache:
    """Get the global query cache singleton."""
    return _query_cache
