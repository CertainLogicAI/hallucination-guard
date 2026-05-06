#!/usr/bin/env python3
"""
Harvest Cache - Weekly cache harvester.
Scans workspace-cache.json, memory files, docs, brain-internal, and conversations
for new or updated entries since last harvest.
Writes a harvested entries file for downstream fact extraction.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = "/data/.openclaw/workspace"
CACHE_FILE = os.path.join(WORKSPACE, "workspace-cache.json")
FACTS_DB = os.path.join(WORKSPACE, "facts_db.json")
HARVEST_DIR = os.path.join(WORKSPACE, "cache_data")
HARVEST_FILE = os.path.join(HARVEST_DIR, "weekly_harvest.json")

# Directories to scan beyond workspace-cache
EXTRA_DIRS = ["memory", "docs", "brain-internal", "articles", "content_output", "logs"]


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_last_harvest_time():
    prev = load_json(HARVEST_FILE, {})
    ts = prev.get("harvested_at", "")
    if ts:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            pass
    # Default: 7 days ago
    return datetime.now(timezone.utc) - timedelta(days=7)


def harvest_from_workspace_cache(last_harvest):
    entries = []
    cache = load_json(CACHE_FILE, {})
    files = cache.get("files", [])
    for item in files:
        mtime_str = item.get("modified", "")
        try:
            mtime = datetime.fromisoformat(mtime_str.replace("Z", "+00:00"))
        except Exception:
            continue
        if mtime >= last_harvest:
            entries.append({
                "source": f"workspace-cache:{item.get('path', '')}",
                "summary": item.get("summary", ""),
                "tags": item.get("read_when", []),
                "modified": mtime_str,
                "size": item.get("size", 0),
            })
    return entries


def harvest_from_directories(last_harvest):
    entries = []
    for dirname in EXTRA_DIRS:
        dirpath = os.path.join(WORKSPACE, dirname)
        if not os.path.isdir(dirpath):
            continue
        for root, _, files in os.walk(dirpath):
            # Skip hidden dirs
            if any(part.startswith(".") for part in Path(root).parts):
                continue
            for fname in files:
                if fname.endswith((".json", ".md", ".txt", ".log")):
                    fpath = os.path.join(root, fname)
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc)
                    except Exception:
                        continue
                    if mtime >= last_harvest:
                        try:
                            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                                text = f.read(2000)
                        except Exception:
                            text = ""
                        rel = os.path.relpath(fpath, WORKSPACE)
                        entries.append({
                            "source": f"dir:{rel}",
                            "summary": text[:300].replace("\n", " ").strip(),
                            "tags": [],
                            "modified": mtime.isoformat(),
                            "size": os.path.getsize(fpath),
                        })
    return entries


def main():
    now = datetime.now(timezone.utc)
    last_harvest = get_last_harvest_time()

    entries = []
    entries.extend(harvest_from_workspace_cache(last_harvest))
    entries.extend(harvest_from_directories(last_harvest))

    # Deduplicate by source
    seen = set()
    unique = []
    for e in entries:
        src = e["source"]
        if src not in seen:
            seen.add(src)
            unique.append(e)

    report = {
        "harvested_at": now.isoformat(),
        "last_harvest": last_harvest.isoformat(),
        "entries_count": len(unique),
        "entries": unique,
    }
    save_json(HARVEST_FILE, report)
    print(f"Harvested {len(unique)} entries since {last_harvest.isoformat()}")
    print(f"Written to: {HARVEST_FILE}")
    return len(unique)


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count >= 0 else 1)
