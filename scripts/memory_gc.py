#!/usr/bin/env python3
"""
memory_gc.py — Memory garbage collection
Performs nightly cleanup of the memory directory:
1. Archives memory files older than 30 days
2. Removes stale .bak files older than 7 days
3. Compresses archived files with gzip
4. Clears memory-query cache
5. Rebuilds memory index
"""

import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path("/data/.openclaw/workspace")
MEMORY_DIR = ROOT / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
CACHE_FILE = ROOT / "memory-query-cache.json"
INDEX_FILE = ROOT / "memory-index.json"

ARCHIVE_AGE_DAYS = 30
BAK_AGE_DAYS = 7


def log(msg):
    print(f"[memory-gc] {msg}")


def ensure_dirs():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def parse_date_from_filename(filename):
    """Extract YYYY-MM-DD from filenames like 2026-04-21.md or 2026-04-21-topic.md"""
    stem = Path(filename).stem
    parts = stem.split("-")
    if len(parts) >= 3:
        try:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2].split("_")[0])
            return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
    return None


def archive_old_files():
    cutoff = datetime.now() - timedelta(days=ARCHIVE_AGE_DAYS)
    archived = 0
    for f in MEMORY_DIR.iterdir():
        if not f.is_file() or f.suffix != ".md":
            continue
        file_date = parse_date_from_filename(f.name)
        if file_date and file_date < cutoff:
            dest = ARCHIVE_DIR / f.name
            shutil.move(str(f), str(dest))
            archived += 1
            log(f"Archived {f.name} → archive/")
    return archived


def remove_stale_backups():
    cutoff = datetime.now() - timedelta(days=BAK_AGE_DAYS)
    removed = 0
    for f in MEMORY_DIR.iterdir():
        if f.suffix == ".bak":
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                removed += 1
                log(f"Removed stale backup {f.name}")
    return removed


def compress_archives():
    compressed = 0
    for f in ARCHIVE_DIR.iterdir():
        if f.is_file() and not f.name.endswith(".gz"):
            gz_path = f.with_suffix(f.suffix + ".gz")
            with open(f, "rb") as src, gzip.open(gz_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            f.unlink()
            compressed += 1
            log(f"Compressed archive/{f.name}")
    return compressed


def clear_query_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        log("Cleared memory-query cache.")
        return 1
    return 0


def rebuild_index():
    """Rebuild memory-index.json from current memory files."""
    index = {}
    for f in MEMORY_DIR.iterdir():
        if f.is_file() and f.suffix == ".md":
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                tags = []
                for line in content.splitlines()[:20]:
                    if line.startswith("tags:"):
                        tags = [t.strip() for t in line.replace("tags:", "").split(",") if t.strip()]
                        break
                index[f.name] = {"tags": tags, "modified": f.stat().st_mtime}
            except Exception as e:
                log(f"Warning: could not index {f.name}: {e}")
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")
    log(f"Rebuilt memory index ({len(index)} entries).")
    return len(index)


def main():
    log("Memory garbage collection started.")
    ensure_dirs()
    archived = archive_old_files()
    removed = remove_stale_backups()
    compressed = compress_archives()
    cleared = clear_query_cache()
    indexed = rebuild_index()

    log("Complete.")
    print(json.dumps({
        "status": "ok",
        "archived": archived,
        "backups_removed": removed,
        "compressed": compressed,
        "cache_cleared": bool(cleared),
        "index_entries": indexed,
        "timestamp": datetime.now().isoformat()
    }, indent=2))


if __name__ == "__main__":
    main()
