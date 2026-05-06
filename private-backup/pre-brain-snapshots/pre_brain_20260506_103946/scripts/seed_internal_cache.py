#!/usr/bin/env python3
"""
Coder Cache Seeder - Seeds coding cache entries into Brain API
Reads /data/.openclaw/workspace/coding_cache_seed.json
Reports how many queries were newly seeded (0 = silent)
"""
import json, requests, sys, os
from datetime import datetime

SEED_PATH = "/data/.openclaw/workspace/coding_cache_seed.json"
BRAIN_URL = "http://127.0.0.1:8000"
LOG_PATH = "/data/.openclaw/workspace/brain-internal/seed.log"

def log(msg):
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def check_exists(key):
    try:
        resp = requests.get(
            f"{BRAIN_URL}/facts/search",
            params={"q": key},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("count", 0) > 0:
                return True
    except Exception:
        pass
    return False

def seed_fact(key, entry):
    payload = {
        "key": key,
        "type": entry.get("type", "string"),
        "value": str(entry.get("value", "")),
        "source": entry.get("source", "coding_cache_seed")
    }
    resp = requests.post(f"{BRAIN_URL}/facts", json=payload, timeout=10)
    return resp.status_code == 201

def main():
    if not os.path.exists(SEED_PATH):
        log(f"ERROR: seed file not found: {SEED_PATH}")
        sys.exit(1)

    try:
        with open(SEED_PATH, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f"ERROR: invalid JSON in seed file: {e}")
        sys.exit(1)

    facts = data.get("facts", {})
    log(f"Loaded {len(facts)} candidate facts from cache seed")

    added = 0
    skipped = 0
    failed = 0

    for key, entry in facts.items():
        if check_exists(key):
            skipped += 1
            continue
        try:
            if seed_fact(key, entry):
                added += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            log(f"ERROR seeding '{key}': {e}")

    if added > 0:
        log(f"SEEDED: {added} new queries | skipped: {skipped} | failed: {failed}")
    else:
        log(f"No new entries. Skipped: {skipped}, Failed: {failed}")

    return added

if __name__ == "__main__":
    added = main()
    if added > 0:
        print(f"\nCoder cache seeder: {added} queries seeded.")
    else:
        # Silent if 0 new entries as per cron spec
        pass
