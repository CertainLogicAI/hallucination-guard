#!/usr/bin/env python3
"""
CertainLogic Verifier - Pack Manager
Zero-friction install for free and paid tiers.
"""

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

# Default data directory
_DEFAULT_DATA_DIR = Path(os.getenv(
    "HALLUCINATION_GUARD_DATA",
    Path.home() / ".hallucination-guard"
))

# Free tier is bundled with the package
FREE_TIER_PATH = Path(__file__).parent / "free_tier_facts.json"
# Full paid tier is also bundled (this IS the open source repo)
FULL_FACTS_PATH = Path(__file__).parent / "facts_db.json"


def get_data_dir() -> Path:
    """Get (and create) the data directory."""
    data_dir = _DEFAULT_DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_active_facts_path() -> Path:
    """Get path to active facts database."""
    data_dir = get_data_dir()
    active = data_dir / "facts_db.json"
    if not active.exists() and FREE_TIER_PATH.exists():
        shutil.copy2(FREE_TIER_PATH, active)
    return active


def get_active_cache_path() -> Path:
    """Get path to active cache database."""
    data_dir = get_data_dir()
    cache = data_dir / "cache.db"
    if not cache.exists():
        _init_cache(cache)
    return cache


# ---------------------------------------------------------------------------
# Simple one-call install (new API)
# ---------------------------------------------------------------------------

def install(tier: str = "free", license_key: Optional[str] = None, data_dir: Optional[Path] = None) -> dict:
    """
    Zero-friction install. One call, works offline, production-ready.

    Free tier (default):
        $ hallucination-guard install
        → 100 verified facts, 15 sample queries, works offline

    Paid tier:
        $ hallucination-guard install --paid --key XXXX
        → 333 facts + pre-warmed cache, zero cold start
    """
    return install_pack("coder", license_key=license_key if tier == "paid" else None, data_dir=data_dir)


# ---------------------------------------------------------------------------
# Full pack manager (backward compatible)
# ---------------------------------------------------------------------------

def install_pack(
    pack_name: str = "coder",
    license_key: Optional[str] = None,
    data_dir: Optional[Path] = None,
) -> dict:
    """Install a fact pack. Free if no key, paid if key provided."""
    if data_dir is None:
        data_dir = get_data_dir()
    else:
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

    if license_key:
        return _install_paid(data_dir, license_key)
    return _install_free(data_dir)


def update_pack(pack_name: str = "coder", data_dir: Optional[Path] = None) -> dict:
    """Update paid pack ($9.99/mo subscription)."""
    if data_dir is None:
        data_dir = get_data_dir()

    meta_path = data_dir / "meta.json"
    if not meta_path.exists():
        return {"status": "error", "message": "No pack installed. Run: hallucination-guard install"}

    with open(meta_path) as f:
        meta = json.load(f)

    if meta.get("tier") != "paid":
        return {
            "status": "error",
            "message": "Updates require paid tier. Upgrade at https://certainlogic.ai/shop"
        }

    # Re-install from full facts (will pull latest in production)
    return _install_paid(data_dir, meta.get("license_key_hash", ""))


def pack_status(pack_name: str = "coder", data_dir: Optional[Path] = None) -> dict:
    """Get installation status."""
    if data_dir is None:
        data_dir = get_data_dir()

    meta_path = data_dir / "meta.json"
    if not meta_path.exists():
        return {"installed": False}

    with open(meta_path) as f:
        meta = json.load(f)

    cache_entries = 0
    cache_path = data_dir / "cache.db"
    if cache_path.exists():
        try:
            conn = sqlite3.connect(str(cache_path))
            cursor = conn.execute("SELECT COUNT(*) FROM query_cache")
            cache_entries = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass

    return {
        "installed": True,
        "pack": pack_name,
        **meta,
        "cache_entries": cache_entries,
    }


# ---------------------------------------------------------------------------
# Internal installers
# ---------------------------------------------------------------------------

def _install_free(data_dir: Path) -> dict:
    """Free tier: 100 essential facts + 15 sample queries."""
    facts_dest = data_dir / "facts_db.json"
    cache_dest = data_dir / "cache.db"

    # Install facts
    if FREE_TIER_PATH.exists():
        shutil.copy2(FREE_TIER_PATH, facts_dest)
        with open(FREE_TIER_PATH) as f:
            pack_data = json.load(f)
        facts = pack_data.get("facts", {})
        sample_queries = pack_data.get("sample_queries", [])
    else:
        facts = _create_minimal_facts()
        sample_queries = []
        with open(facts_dest, "w") as f:
            json.dump({"facts": facts}, f, indent=2)

    # Init cache
    _init_cache(cache_dest)

    # Save sample queries
    queries_dest = data_dir / "sample_queries.json"
    with open(queries_dest, "w") as f:
        json.dump(sample_queries, f, indent=2)

    # Metadata
    meta = {
        "pack": "coder",
        "tier": "free",
        "facts_count": len(facts),
        "sample_queries": len(sample_queries),
        "cache_entries": 0,
        "cache_warmed": False,
        "installed_at": _now_iso(),
    }
    _write_meta(data_dir / "meta.json", meta)
    _write_env(data_dir, facts_dest, cache_dest)

    # Run samples
    results = _run_samples(facts, sample_queries[:5])
    hit_count = sum(1 for r in results if r["hit"])

    return {
        "status": "ok",
        "tier": "free",
        "facts": len(facts),
        "sample_queries": len(sample_queries),
        "sample_hits": hit_count,
        "sample_total": len(results),
        "cache_warmed": False,
        "data_dir": str(data_dir),
        "message": (
            f"✅ Free Coder Pack installed\n"
            f"   • {len(facts)} verified facts (Python, HTTP, Git, Docker, SQL, JS/TS, Security)\n"
            f"   • {len(sample_queries)} sample queries\n"
            f"   • {hit_count}/{len(results)} sample queries hit on first run\n"
            f"\n   Start: hallucination-guard serve\n"
            f"   Upgrade: hallucination-guard install --paid --key YOUR_KEY"
        ),
    }


def _install_paid(data_dir: Path, license_key: str) -> dict:
    """Paid tier: 333 facts + pre-warmed cache."""
    facts_dest = data_dir / "facts_db.json"
    cache_dest = data_dir / "cache.db"

    # Install full facts
    if FULL_FACTS_PATH.exists():
        shutil.copy2(FULL_FACTS_PATH, facts_dest)
        with open(FULL_FACTS_PATH) as f:
            pack_data = json.load(f)
        facts = pack_data.get("facts", pack_data)
    else:
        return {
            "status": "error",
            "message": (
                "Full facts not found.\n"
                "Download: https://certainlogic.ai/shop/coder-pack\n"
                "Or start free: hallucination-guard install"
            ),
        }

    # Init + warm cache
    _init_cache(cache_dest)
    _warm_cache(cache_dest, facts)

    # Metadata
    meta = {
        "pack": "coder",
        "tier": "paid",
        "facts_count": len(facts),
        "cache_entries": len(facts),
        "cache_warmed": True,
        "installed_at": _now_iso(),
    }
    if license_key and len(license_key) > 8:
        meta["license_key_hash"] = hashlib.sha256(license_key.encode()).hexdigest()[:16]

    _write_meta(data_dir / "meta.json", meta)
    _write_env(data_dir, facts_dest, cache_dest)

    return {
        "status": "ok",
        "tier": "paid",
        "facts": len(facts),
        "cache_entries": len(facts),
        "cache_warmed": True,
        "data_dir": str(data_dir),
        "message": (
            f"✅ Coder Pack Pro installed\n"
            f"   • {len(facts)} verified developer facts\n"
            f"   • {len(facts)} pre-warmed cache entries (zero cold start)\n"
            f"   • Production-ready immediately\n"
            f"\n   Start: hallucination-guard serve\n"
            f"   Update: hallucination-guard update ($9.99/mo optional)"
        ),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_cache(cache_path: Path):
    """Initialize SQLite cache database."""
    conn = sqlite3.connect(str(cache_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            query_hash TEXT PRIMARY KEY,
            query TEXT,
            response TEXT,
            embedding BLOB,
            created_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_query ON query_cache(query_hash)")
    conn.commit()
    conn.close()


def _warm_cache(cache_path: Path, facts: dict):
    """Pre-warm cache with all facts for zero cold start."""
    import time
    conn = sqlite3.connect(str(cache_path))
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for query, data in facts.items():
        if isinstance(data, dict):
            answer = data.get("value", data.get("answer", str(data)))
        else:
            answer = str(data)

        query_hash = hashlib.sha256(query.encode()).hexdigest()
        conn.execute(
            "INSERT OR REPLACE INTO query_cache (query_hash, query, response, created_at) VALUES (?, ?, ?, ?)",
            (query_hash, query, answer, now)
        )

    conn.commit()
    conn.close()


def _run_samples(facts: dict, samples: list) -> list:
    """Run sample queries and report hit rate."""
    results = []
    for sample in samples:
        query = sample.get("query", "")
        expected = sample.get("expected_fact", "")
        hit = expected in facts
        if not hit:
            # Try partial match
            hit = any(expected in k for k in facts)
        results.append({"query": query[:60], "hit": hit, "fact": expected[:50] if hit else None})
    return results


def _create_minimal_facts() -> dict:
    """Fallback minimal facts."""
    return {
        "python current stable version": {"value": "3.13", "source": "docs.python.org"},
        "python list is mutable": {"value": "True — lists can be modified in-place", "source": "python_docs"},
        "python tuple is immutable": {"value": "True — tuples cannot be modified after creation", "source": "python_docs"},
    }


def _write_meta(path: Path, meta: dict):
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)


def _write_env(data_dir: Path, facts_path: Path, cache_path: Path):
    env_path = data_dir / ".env"
    with open(env_path, "w") as f:
        f.write(f"FACTS_DB_PATH={facts_path}\n")
        f.write(f"CACHE_DB_PATH={cache_path}\n")
        f.write(f"HALLUCINATION_GUARD_DATA={data_dir}\n")


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
