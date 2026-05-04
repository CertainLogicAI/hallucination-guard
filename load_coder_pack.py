#!/usr/bin/env python3
"""Load coder_facts_pack into running Brain API."""
import json, requests, sys

PACK_PATH = "/data/.openclaw/workspace/opensource/coder_facts_pack_v1.0.json"
BRAIN_URL = "http://127.0.0.1:8000"

def main():
    with open(PACK_PATH) as f:
        pack = json.load(f)

    facts = pack.get("facts", {})
    print(f"Loading {len(facts)} facts from Coder Pack v1.0...")

    added = 0
    skipped = 0
    for key, fact in facts.items():
        # Check if already exists
        resp = requests.get(f"{BRAIN_URL}/facts/search?q={requests.utils.quote(key)}")
        if resp.status_code == 200 and resp.json().get("count", 0) > 0:
            skipped += 1
            continue

        payload = {
            "key": key,
            "type": fact.get("type", "string"),
            "value": str(fact.get("value", "")),
            "source": fact.get("source", "")
        }
        resp = requests.post(f"{BRAIN_URL}/facts", json=payload)
        if resp.status_code == 201:
            added += 1
        else:
            print(f"  ERROR adding '{key}': {resp.status_code} {resp.text}")

    print(f"\nDone. Added: {added}, Skipped (already present): {skipped}")

if __name__ == "__main__":
    main()
