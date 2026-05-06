#!/usr/bin/env python3
"""
Emergency Brain Data Migration
Merge archived facts and queries into active Brain API.
"""

import json
import os
import shutil
from pathlib import Path
from collections import OrderedDict
from datetime import datetime

WORKSPACE = Path("/data/.openclaw/workspace")
ARCHIVE = WORKSPACE / "archive/retired-modules/opensource"
CURRENT_FACTS = WORKSPACE / "facts_db.json"
CURRENT_CACHE = WORKSPACE / "cache_data/answer_cache.json"
PATHFINDER_CACHE = WORKSPACE / ".build_data/build_pathfinder_core/agentpathfinder/cache_data.json"
BACKUP_DIR = WORKSPACE / "brain_migration_backup"

def backup_current():
    """Backup before migration."""
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if CURRENT_FACTS.exists():
        shutil.copy(CURRENT_FACTS, BACKUP_DIR / f"facts_db_pre_migration_{ts}.json")
    if CURRENT_CACHE.exists():
        shutil.copy(CURRENT_CACHE, BACKUP_DIR / f"answer_cache_pre_migration_{ts}.json")
    print(f"Backup saved to {BACKUP_DIR}")

def load_json(path):
    """Load JSON file safely."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  Warning: Could not load {path}: {e}")
        return None

def merge_facts():
    """Merge all archived facts into current facts_db.json."""
    print("\n=== PHASE 1: MERGE FACTS ===")
    
    # Load current
    current = load_json(CURRENT_FACTS) or {"facts": {}}
    current_facts = current.get("facts", {})
    print(f"Current facts: {len(current_facts)}")
    
    # Sources to merge
    sources = [
        (ARCHIVE / "coder_facts_pack_v1.0.json", "coder_pack"),
        (WORKSPACE / "products/coding_agent/coding_facts.json", "coding_agent"),
        (WORKSPACE / ".build_data/build_pathfinder_core/agentpathfinder/new_facts.json", "pathfinder_new"),
    ]
    
    merged = dict(current_facts)
    added_count = 0
    
    for path, source_name in sources:
        data = load_json(path)
        if not data:
            continue
        
        facts = data.get("facts", {})
        print(f"  Loading from {source_name}: {len(facts)} facts")
        
        for key, value in facts.items():
            # Normalize key
            norm_key = key.lower().strip()
            if norm_key not in merged:
                merged[norm_key] = value if isinstance(value, dict) else {
                    "type": "string",
                    "value": str(value),
                    "source": source_name
                }
                added_count += 1
            # If current has it but archive has better data
            elif source_name == "coding_agent" and isinstance(value, dict) and len(str(value.get("value", ""))) > len(str(merged[norm_key].get("value", ""))):
                merged[norm_key] = value
    
    # Save merged
    merged_db = {"facts": merged, "_meta": {
        "version": "2.0",
        "migrated_at": datetime.now().isoformat(),
        "previous_count": len(current_facts),
        "merged_sources": [s[1] for s in sources if load_json(s[0])]
    }}
    
    with open(CURRENT_FACTS, "w") as f:
        json.dump(merged_db, f, indent=2, sort_keys=True)
    
    print(f"  Added {added_count} new facts")
    print(f"  TOTAL FACTS: {len(merged)}")
    return len(merged)

def merge_queries():
    """Merge pathfinder cache into current TRE answer cache."""
    print("\n=== PHASE 2: MERGE QUERIES ===")
    
    # Load current
    current = {"entries": []}
    if CURRENT_CACHE.exists():
        try:
            with open(CURRENT_CACHE) as f:
                current = json.load(f)
        except:
            pass
    
    current_entries = current.get("entries", [])
    print(f"Current cache entries: {len(current_entries)}")
    
    # Load pathfinder cache
    pf_data = load_json(PATHFINDER_CACHE)
    if not pf_data:
        print("  ERROR: No pathfinder cache found")
        return 0
    
    pf_cache = pf_data.get("cache", {})
    print(f"Pathfinder cache entries: {len(pf_cache)}")
    
    # Convert pathfinder entries to TRE format
    new_entries = []
    for query_hash, entry in pf_cache.items():
        query = entry.get("query", "")
        answer = entry.get("answer", entry.get("query", ""))  # Some only have query
        source = entry.get("source", "pathfinder_migration")
        
        new_entries.append({
            "q": query_hash,
            "a": answer,
            "ts": 1778000000.0,  # Approximate migration timestamp
            "tc": len(answer.split()) if answer else 0,
            "source": source,
            "migrated": True
        })
    
    # Merge (deduplicate by hash)
    existing_hashes = {e["q"] for e in current_entries}
    added = 0
    for entry in new_entries:
        if entry["q"] not in existing_hashes:
            current_entries.append(entry)
            existing_hashes.add(entry["q"])
            added += 1
    
    # Save
    merged = {"entries": current_entries, "_meta": {
        "migrated_at": datetime.now().isoformat(),
        "total_entries": len(current_entries),
        "added_from_pathfinder": added
    }}
    
    with open(CURRENT_CACHE, "w") as f:
        json.dump(merged, f, indent=2)
    
    print(f"  Added {added} queries from pathfinder")
    print(f"  TOTAL CACHE ENTRIES: {len(current_entries)}")
    return len(current_entries)

def verify():
    """Verify merge succeeded."""
    print("\n=== VERIFICATION ===")
    
    with open(CURRENT_FACTS) as f:
        facts = json.load(f)
    print(f"facts_db.json: {len(facts.get('facts', {}))} facts")
    
    with open(CURRENT_CACHE) as f:
        cache = json.load(f)
    print(f"answer_cache.json: {len(cache.get('entries', []))} entries")
    
    # Restart brain API to pick up new data
    print("\nRestarting Brain API to pick up merged data...")
    os.system("bash /data/.openclaw/workspace/start-brain.sh")
    
    # Verify API picks it up
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as resp:
            health = json.loads(resp.read())
            print(f"Brain API: Healthy ({health['components']['facts_db']})")
    except Exception as e:
        print(f"Brain API check failed: {e}")

def main():
    print("BRAIN DATA MIGRATION")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    
    backup_current()
    fact_count = merge_facts()
    query_count = merge_queries()
    verify()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print(f"Facts: {fact_count}")
    print(f"Queries: {query_count}")
    print(f"Backup: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
