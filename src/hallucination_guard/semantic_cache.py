#!/usr/bin/env python3
"""
CertainLogic Verifier - Semantic Cache (L2)
Semantic similarity search over cached queries using sentence embeddings.
Requires sentence‑transformers (optional).
MIT License
"""

import json
import logging
import os
import sqlite3
import struct
import threading
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "./cache.db")
DEFAULT_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", "0.92"))
TOP_K = int(os.getenv("SEMANTIC_TOP_K", "5"))
MODEL_NAME = os.getenv("SEMANTIC_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

_model = None
_model_lock = threading.Lock()
_thread_local = threading.local()


# ---------------------------------------------------------------------------
# Model (lazy, singleton)
# ---------------------------------------------------------------------------


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError:
                    raise ImportError(
                        "sentence‑transformers is not installed. "
                        "Install it with `pip install sentence-transformers` "
                        "or set environment variable SEMANTIC_CACHE_ENABLED=false."
                    )
                _model = SentenceTransformer(MODEL_NAME)
    return _model


def encode(text: str) -> np.ndarray:
    """Return a normalized embedding vector for text."""
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.astype(np.float32)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def _get_conn() -> sqlite3.Connection:
    conn = getattr(_thread_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(CACHE_DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        _ensure_schema(conn)
        _thread_local.conn = conn
    return conn


def _ensure_schema(conn: sqlite3.Connection):
    """Add embedding column and index if not present."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(query_cache)").fetchall()]
    if "embedding" not in cols:
        conn.execute("ALTER TABLE query_cache ADD COLUMN embedding BLOB")
    if "query" not in cols:
        conn.execute("ALTER TABLE query_cache ADD COLUMN query TEXT")
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_has_embedding
        ON query_cache(query_hash)
        WHERE embedding IS NOT NULL
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# Encode → bytes (BLOB storage)
# ---------------------------------------------------------------------------


def _vec_to_blob(vec: np.ndarray) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _blob_to_vec(blob: bytes) -> np.ndarray:
    n = len(blob) // 4
    return np.array(struct.unpack(f"{n}f", blob), dtype=np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two already-normalized vectors."""
    return float(np.dot(a, b))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def store_embedding(query_hash: str, query_text: str):
    """
    Compute and store an embedding for a cached query.
    Safe to call even if embedding already exists (no-op).
    """
    try:
        conn = _get_conn()
        existing = conn.execute(
            "SELECT embedding FROM query_cache WHERE query_hash=?", (query_hash,)
        ).fetchone()
        if existing is None:
            return  # entry doesn't exist
        if existing[0] is not None:
            return  # already has embedding
        vec = encode(query_text)
        blob = _vec_to_blob(vec)
        conn.execute(
            "UPDATE query_cache SET embedding=?, query=? WHERE query_hash=?",
            (blob, query_text, query_hash),
        )
        conn.commit()
    except Exception as e:
        logger.warning(f"store_embedding error: {e}")


def semantic_lookup(
    query: str,
    threshold: float = DEFAULT_THRESHOLD,
    top_k: int = TOP_K,
) -> Optional[Tuple[str, float]]:
    """
    Search for a semantically similar cached result.

    Returns (cached_result, similarity_score) if a match above threshold is found.
    Returns None on miss.
    """
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT query_hash, result, embedding FROM query_cache WHERE embedding IS NOT NULL"
        ).fetchall()
        if not rows:
            return None

        query_vec = encode(query)
        best_score = -1.0
        best_result = None

        for row in rows:
            _, result, blob = row
            try:
                cached_vec = _blob_to_vec(blob)
                score = _cosine(query_vec, cached_vec)
                if score > best_score:
                    best_score = score
                    best_result = result
            except Exception:
                continue

        if best_score >= threshold and best_result is not None:
            return best_result, best_score
        return None
    except Exception as e:
        logger.warning(f"semantic_lookup error: {e}")
        return None


def backfill_embeddings(batch_size: int = 50, dry_run: bool = False) -> dict:
    """
    Backfill embeddings for all cache entries that have a query text but no embedding.
    Safe to call repeatedly — skips already-embedded entries.

    Returns stats dict.
    """
    try:
        conn = _get_conn()
        # Use query text if available, fallback to result text for legacy entries
        rows = conn.execute(
            """SELECT query_hash, COALESCE(query, result) AS text
               FROM query_cache
               WHERE embedding IS NULL AND COALESCE(query, result) IS NOT NULL"""
        ).fetchall()
    except Exception as e:
        return {"error": str(e), "processed": 0, "skipped": 0}

    processed = 0
    skipped = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        for query_hash, query_text in batch:
            if not query_text or not query_text.strip():
                skipped += 1
                continue
            if dry_run:
                processed += 1
                continue
            try:
                vec = encode(query_text)
                blob = _vec_to_blob(vec)
                conn.execute(
                    "UPDATE query_cache SET embedding=? WHERE query_hash=?",
                    (blob, query_hash),
                )
                processed += 1
            except Exception as e:
                logger.warning(f"backfill error for {query_hash[:8]}: {e}")
                skipped += 1
        if not dry_run:
            conn.commit()

    return {
        "processed": processed,
        "skipped": skipped,
        "total_candidates": len(rows),
        "dry_run": dry_run,
    }


def get_semantic_stats() -> dict:
    """Return embedding coverage stats."""
    try:
        conn = _get_conn()
        total = conn.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
        with_emb = conn.execute(
            "SELECT COUNT(*) FROM query_cache WHERE embedding IS NOT NULL"
        ).fetchone()[0]
        without_emb = total - with_emb
        return {
            "total_entries": total,
            "with_embedding": with_emb,
            "without_embedding": without_emb,
            "coverage_pct": round((with_emb / total * 100) if total else 0, 1),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: semantic_cache.py <query> [threshold]")
        sys.exit(1)
    query = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_THRESHOLD
    result = semantic_lookup(query, threshold)
    if result:
        cached, score = result
        print(
            json.dumps(
                {"found": True, "cached_result": cached, "score": score}, indent=2
            )
        )
    else:
        print(json.dumps({"found": False}, indent=2))
