#!/usr/bin/env python3
"""
Pack manager for CertainLogic Verifier.

Handles downloading, installing, and updating fact packs and pre-warmed caches.
Designed for zero-config, hands-off installation.
"""

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

# Default data directory — stores all pack data
_DEFAULT_DATA_DIR = Path(os.getenv(
    "HALLUCINATION_GUARD_DATA",
    Path.home() / ".hallucination-guard"
))

# Pack registry
PACK_REGISTRY_URL = "https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/main/packs/registry.json"

# Free pack is bundled; paid packs are downloaded
BUNDLED_FREE_FACTS = Path(__file__).parent / "facts_db.json"


def get_data_dir() -> Path:
    """Get (and create) the data directory."""
    data_dir = _DEFAULT_DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_active_facts_path() -> Path:
    """Get the path to the currently active facts database."""
    data_dir = get_data_dir()
    active = data_dir / "facts_db.json"
    if not active.exists():
        # Copy bundled free facts as default
        shutil.copy2(BUNDLED_FREE_FACTS, active)
    return active


def get_active_cache_path() -> Path:
    """Get the path to the active cache database."""
    data_dir = get_data_dir()
    return data_dir / "cache.db"


def install_pack(
    pack_name: str = "coder",
    license_key: Optional[str] = None,
    data_dir: Optional[Path] = None,
) -> dict:
    """
    Install a fact pack + pre-warmed cache.

    For free packs: installs bundled facts + sample queries.
    For paid packs: downloads full facts + pre-warmed cache using license key.

    Returns dict with installation details.
    """
    if data_dir is None:
        data_dir = get_data_dir()
    else:
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

    pack_dir = data_dir / "packs" / pack_name
    pack_dir.mkdir(parents=True, exist_ok=True)

    if license_key:
        return _install_paid_pack(pack_name, license_key, data_dir, pack_dir)
    else:
        return _install_free_pack(pack_name, data_dir, pack_dir)


def _install_free_pack(pack_name: str, data_dir: Path, pack_dir: Path) -> dict:
    """Install the free tier: 100 facts + 10 sample queries."""
    # Copy bundled facts as the active DB
    facts_dest = data_dir / "facts_db.json"
    shutil.copy2(BUNDLED_FREE_FACTS, facts_dest)

    # Download sample queries
    sample_url = f"https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/main/sample_queries.json"
    sample_dest = pack_dir / "sample_queries.json"
    try:
        urllib.request.urlretrieve(sample_url, sample_dest)
    except Exception:
        pass  # Sample queries are optional

    # Write pack metadata
    meta = {
        "pack": pack_name,
        "tier": "free",
        "facts_count": _count_facts(facts_dest),
        "cache_warmed": False,
        "installed_at": _now_iso(),
        "facts_path": str(facts_dest),
        "cache_path": str(data_dir / "cache.db"),
    }
    _write_meta(pack_dir / "meta.json", meta)

    # Set environment pointers
    _write_env(data_dir, facts_dest, data_dir / "cache.db")

    return {
        "status": "installed",
        "tier": "free",
        "facts": meta["facts_count"],
        "cache_warmed": False,
        "data_dir": str(data_dir),
        "message": (
            f"Free {pack_name} pack installed: {meta['facts_count']} facts.\n"
            f"Run sample queries from: {sample_dest}\n"
            f"Upgrade to full pack ($69): hallucination-guard install-pack {pack_name} --key YOUR_LICENSE_KEY"
        ),
    }


def _install_paid_pack(
    pack_name: str, license_key: str, data_dir: Path, pack_dir: Path
) -> dict:
    """Install paid tier: full facts + pre-warmed cache."""
    # Validate license and download pack
    pack_data = _download_paid_pack(pack_name, license_key)

    if pack_data is None:
        return {
            "status": "error",
            "message": "Invalid license key or pack not found. Check your key at https://certainlogic.ai/account",
        }

    # Install facts
    facts_dest = data_dir / "facts_db.json"
    with open(facts_dest, "w") as f:
        json.dump(pack_data["facts"], f, indent=2)

    # Install pre-warmed cache
    cache_dest = data_dir / "cache.db"
    if "cache" in pack_data and pack_data["cache"]:
        _install_cache(pack_data["cache"], cache_dest)
        cache_warmed = True
    else:
        cache_warmed = False

    facts_count = _count_facts(facts_dest)

    meta = {
        "pack": pack_name,
        "tier": "paid",
        "license_key_hash": hashlib.sha256(license_key.encode()).hexdigest()[:16],
        "facts_count": facts_count,
        "cache_warmed": cache_warmed,
        "version": pack_data.get("version", "1.0.0"),
        "installed_at": _now_iso(),
        "facts_path": str(facts_dest),
        "cache_path": str(cache_dest),
    }
    _write_meta(pack_dir / "meta.json", meta)

    _write_env(data_dir, facts_dest, cache_dest)

    return {
        "status": "installed",
        "tier": "paid",
        "facts": facts_count,
        "cache_warmed": cache_warmed,
        "version": meta["version"],
        "data_dir": str(data_dir),
        "message": (
            f"Coder Pack installed: {facts_count} facts + pre-warmed cache.\n"
            f"Your system is production-ready — zero cold start.\n"
            f"Set env: export HALLUCINATION_GUARD_DATA={data_dir}"
        ),
    }


def update_pack(
    pack_name: str = "coder",
    data_dir: Optional[Path] = None,
) -> dict:
    """
    Update an installed paid pack to the latest version.
    Requires an active subscription ($9.99/mo).
    """
    if data_dir is None:
        data_dir = get_data_dir()

    pack_dir = data_dir / "packs" / pack_name
    meta_path = pack_dir / "meta.json"

    if not meta_path.exists():
        return {
            "status": "error",
            "message": f"Pack '{pack_name}' not installed. Run: hallucination-guard install-pack {pack_name}",
        }

    with open(meta_path) as f:
        meta = json.load(f)

    if meta.get("tier") != "paid":
        return {
            "status": "error",
            "message": "Updates require a paid pack. Upgrade: hallucination-guard install-pack coder --key YOUR_KEY",
        }

    # Backup current
    _backup_current(data_dir)

    # Re-download latest
    license_key_hash = meta.get("license_key_hash", "")
    result = _download_update(pack_name, license_key_hash)

    if result is None:
        return {
            "status": "error",
            "message": "Update failed. Check your subscription status at https://certainlogic.ai/account",
        }

    # Apply update
    facts_dest = data_dir / "facts_db.json"
    with open(facts_dest, "w") as f:
        json.dump(result["facts"], f, indent=2)

    if "cache" in result:
        _install_cache(result["cache"], data_dir / "cache.db")

    meta["version"] = result.get("version", meta.get("version", "1.0.0"))
    meta["updated_at"] = _now_iso()
    meta["facts_count"] = _count_facts(facts_dest)
    _write_meta(meta_path, meta)

    return {
        "status": "updated",
        "version": meta["version"],
        "facts": meta["facts_count"],
        "message": f"Pack updated to v{meta['version']}: {meta['facts_count']} facts.",
    }


def pack_status(
    pack_name: str = "coder",
    data_dir: Optional[Path] = None,
) -> dict:
    """Get status of installed pack."""
    if data_dir is None:
        data_dir = get_data_dir()

    pack_dir = data_dir / "packs" / pack_name
    meta_path = pack_dir / "meta.json"

    if not meta_path.exists():
        return {"installed": False, "pack": pack_name}

    with open(meta_path) as f:
        meta = json.load(f)

    # Check if cache exists and has entries
    cache_path = Path(meta.get("cache_path", data_dir / "cache.db"))
    cache_entries = 0
    if cache_path.exists():
        try:
            conn = sqlite3.connect(str(cache_path))
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            cache_entries = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass

    return {
        "installed": True,
        **meta,
        "cache_entries": cache_entries,
    }


# --- Internal helpers ---

def _count_facts(facts_path: Path) -> int:
    try:
        with open(facts_path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "facts" in data:
            return len(data["facts"])
        return len(data)
    except Exception:
        return 0


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _write_meta(path: Path, meta: dict):
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)


def _write_env(data_dir: Path, facts_path: Path, cache_path: Path):
    """Write a .env file for easy sourcing."""
    env_path = data_dir / ".env"
    with open(env_path, "w") as f:
        f.write(f"FACTS_DB_PATH={facts_path}\n")
        f.write(f"CACHE_DB_PATH={cache_path}\n")
        f.write(f"HALLUCINATION_GUARD_DATA={data_dir}\n")


def _backup_current(data_dir: Path):
    """Backup current facts and cache before update."""
    backup_dir = data_dir / "backups" / _now_iso().replace(":", "-").split(".")[0]
    backup_dir.mkdir(parents=True, exist_ok=True)
    for f in ["facts_db.json", "cache.db"]:
        src = data_dir / f
        if src.exists():
            shutil.copy2(src, backup_dir / f)


def _download_paid_pack(pack_name: str, license_key: str) -> Optional[dict]:
    """Download paid pack from CertainLogic API. Returns None on failure."""
    # TODO: Implement actual API call to certainlogic.ai/api/packs/download
    # For now, return None (will be connected to Stripe + download API)
    return None


def _download_update(pack_name: str, license_key_hash: str) -> Optional[dict]:
    """Download pack update. Returns None on failure."""
    # TODO: Implement actual API call
    return None


def _install_cache(cache_data, cache_path: Path):
    """Install pre-warmed cache database."""
    # TODO: Handle different cache formats (SQLite blob, JSON seed, etc.)
    pass
