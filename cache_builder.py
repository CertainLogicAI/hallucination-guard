#!/usr/bin/env python3
"""
Cache Builder - Smart incremental cache updater for workspace files.
Rebuilds workspace-cache.json with summaries, tags, and read_when triggers.
"""

import os
import sys
import json
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path

CACHE_FILE = "/data/.openclaw/workspace/workspace-cache.json"
FACTS_DB = "/data/.openclaw/workspace/facts_db.json"
WORKSPACE = "/data/.openclaw/workspace"

# Priority directories (higher = more important)
PRIORITY_DIRS = {
    "memory": 100,
    "docs": 90,
    "skills": 80,
    "articles": 70,
    "brain-internal": 60,
    "projects": 50,
    "memory-index": 60,
}

# Keywords to extract for read_when tags
TAG_KEYWORDS = [
    "memory", "cache", "llm", "token", "optimization", "business",
    "deterministic", "guardrail", "patent", "faulttrace", "l5x",
    "pricing", "api", "docker", "skills", "openclaw", "security",
    "performance", "consulting", "reference", "domains", "plc",
    "monetization", "cost", "idea", "flush", "pre-compaction",
    "routing", "hallucination", "verification", "stress", "test",
    "benchmark", "compliance", "regulatory", "backup", "cron",
    "workspace", "strategy", "mcp", "agent", "pipeline",
]


def log(msg, *, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def get_priority(rel_path):
    parts = Path(rel_path).parts
    for part in parts:
        if part in PRIORITY_DIRS:
            return PRIORITY_DIRS[part]
    return 0


def extract_tags(text):
    text_lower = text.lower()
    found = []
    for kw in TAG_KEYWORDS:
        if kw in text_lower:
            found.append(kw)
    return sorted(set(found))[:15]  # cap tags


def file_summary(path, rel_path, size, max_chars=500):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(max_chars * 3)
    except Exception:
        return f"File: {rel_path}"

    # First line as summary candidate
    first_line = content.split('\n')[0].strip()
    if len(first_line) > 10 and len(first_line) < 200:
        summary = first_line
    else:
        summary = f"{rel_path} ({size} bytes)"

    # If content starts with YAML frontmatter, skip it for summary
    if content.startswith('---'):
        try:
            end = content.find('---', 3)
            if end != -1:
                body = content[end+3:max_chars*3].strip()
                if body:
                    summary = body.split('\n')[0].strip()[:200]
        except Exception:
            pass

    return summary


def list_source_files(limit=None, smart=False):
    """
    Scan workspace for cache-worthy files.
    --smart: skip build artifacts, node_modules, large binaries, etc.
    """
    exclude_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules',
        '.openclaw', 'cron', 'backup_local', 'tests', 'test-results',
        'archive', 'artifacts', 'conversation_logs', 'logs', 'TESTS',
    }
    exclude_exts = {'.zip', '.tar.gz', '.tgz', '.png', '.jpg', '.jpeg',
                    '.gif', '.webp', '.mp4', '.mp3', '.pdf', '.woff',
                    '.woff2', '.ttf', '.eot', '.ico'}

    candidates = []
    for root, dirs, files in os.walk(WORKSPACE):
        # Filter directories in-place for os.walk efficiency
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in exclude_exts or fname.endswith('.tar.gz') or fname.endswith('.tgz'):
                continue

            full = os.path.join(root, fname)
            rel = os.path.relpath(full, WORKSPACE)

            # Skip hidden files and backup-style names
            if fname.startswith('.') or fname.endswith('~'):
                continue

            try:
                stat = os.stat(full)
                size = stat.st_size
                mtime = stat.st_mtime
            except OSError:
                continue

            # Skip very large files (>2MB)
            if size > 2_000_000:
                continue

            priority = get_priority(rel)
            candidates.append((priority, mtime, size, full, rel))

    # Sort: higher priority first, then newest
    candidates.sort(key=lambda x: (-x[0], -x[1]))

    if limit:
        candidates = candidates[:limit]

    return candidates


def load_existing_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            log("Could not parse existing cache; starting fresh.", level="WARN")
    return {"files": [], "index": {}, "generated": None}


def build_cache(limit=50, smart=False, enable_log=False):
    log("Starting cache builder...")
    log(f"Args: limit={limit}, smart={smart}")

    existing = load_existing_cache()
    existing_files = {entry.get("path"): entry for entry in existing.get("files", [])}

    candidates = list_source_files(limit=limit, smart=smart)
    log(f"Found {len(candidates)} candidate files")

    new_entries = []
    updated_count = 0
    skipped_count = 0
    index = {k: list(v) for k, v in existing.get("index", {}).items()}

    for priority, mtime, size, full_path, rel_path in candidates:
        existing_entry = existing_files.get(rel_path)

        if existing_entry:
            # Skip if not modified and smart mode
            prev_mtime = existing_entry.get("modified")
            if smart and prev_mtime:
                try:
                    prev = datetime.fromisoformat(prev_mtime.replace('Z', '+00:00')).timestamp()
                except Exception:
                    prev = 0
                if mtime <= prev:
                    skipped_count += 1
                    continue

        # Generate entry
        summary = file_summary(full_path, rel_path, size)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(5000)
        except Exception:
            sample = ""

        tags = extract_tags(sample or summary)
        entry = {
            "path": rel_path,
            "summary": summary[:300],
            "read_when": tags,
            "size": size,
            "modified": datetime.fromtimestamp(mtime, tz=datetime.now().astimezone().tzinfo).isoformat(),
        }

        if existing_entry:
            updated_count += 1
            if enable_log:
                log(f"Updated: {rel_path}")
        else:
            if enable_log:
                log(f"Added:   {rel_path}")

        new_entries.append(entry)

        # Update inverted index
        for tag in tags:
            if tag not in index:
                index[tag] = []
            if rel_path not in index[tag]:
                index[tag].append(rel_path)

    # Merge: keep old entries for files we didn't process (unless over limit)
    processed_paths = {e["path"] for e in new_entries}
    retained = [e for e in existing.get("files", []) if e["path"] not in processed_paths]

    # Assemble final cache
    final_entries = new_entries + retained

    # If overall count exceeds hard limit, trim oldest / lowest priority
    if limit and len(final_entries) > limit:
        # Sort by priority heuristic: has tags > no tags, then newer > older
        def sort_key(e):
            has_tags = len(e.get("read_when", []))
            ts = 0
            try:
                ts = datetime.fromisoformat(e.get("modified", "").replace('Z', '+00:00')).timestamp()
            except Exception:
                pass
            return (-has_tags, -ts)

        final_entries.sort(key=sort_key)
        removed = final_entries[limit:]
        final_entries = final_entries[:limit]

        # Clean index of removed paths
        removed_paths = {r["path"] for r in removed}
        for tag in list(index.keys()):
            index[tag] = [p for p in index[tag] if p not in removed_paths]
            if not index[tag]:
                del index[tag]

    cache_data = {
        "generated": datetime.now().isoformat(),
        "files": final_entries,
        "index": index,
    }

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)

    # Also update hash for integrity
    with open(CACHE_FILE, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    cache_data["_metadata"] = {
        "cache_hash": h,
        "version": "2.2",
        "last_built": int(time.time()),
        "entries_count": len(final_entries),
        "updated": updated_count,
        "added": len(new_entries) - updated_count,
        "skipped": skipped_count,
    }

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)

    log(f"Cache built: {len(final_entries)} entries total")
    log(f"  New: {len(new_entries) - updated_count}, Updated: {updated_count}, Skipped: {skipped_count}")
    log(f"  Tags indexed: {len(index)}")
    log(f"  Cache hash: {h[:16]}...")
    log("Done.")
    return cache_data


def main():
    parser = argparse.ArgumentParser(description="Smart workspace cache builder")
    parser.add_argument("--limit", type=int, default=50, help="Max entries to process/retain")
    parser.add_argument("--smart", action="store_true", help="Skip unmodified files and build artifacts")
    parser.add_argument("--log", action="store_true", help="Enable per-file logging")
    args = parser.parse_args()

    build_cache(limit=args.limit, smart=args.smart, enable_log=args.log)


if __name__ == "__main__":
    main()
