#!/usr/bin/env python3
"""
Extract Facts - Weekly fact extraction pipeline.
Reads the latest weekly harvest, extracts candidate facts (key-value pairs),
and writes a draft facts file for human review.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = "/data/.openclaw/workspace"
HARVEST_FILE = os.path.join(WORKSPACE, "cache_data", "weekly_harvest.json")
DRAFTS_DIR = os.path.join(WORKSPACE, "drafts")
FACTS_DB = os.path.join(WORKSPACE, "facts_db.json")


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


def load_facts_db():
    data = load_json(FACTS_DB, {})
    return data.get("facts", {})


def extract_candidate_facts(entries):
    """Simple heuristic fact extraction from summaries and text snippets."""
    drafts = []
    for entry in entries:
        text = entry.get("summary", "")
        if not text:
            continue
        # Look for "X is Y" or "X = Y" patterns
        patterns = [
            r"([A-Z][a-zA-Z\s\-]{2,50})\s+is\s+([A-Z][a-zA-Z0-9\s\-]{1,100})",
            r"([a-z][a-z_\-]{2,30})\s*=\s*([0-9.]+(?:\s*[a-zA-Z/%]+)?)",
            r"([A-Z][a-zA-Z\s]{2,40}):\s*([A-Z][a-zA-Z0-9\s\-]{1,80})",
            r"the\s+([a-z\s]{3,40})\s+of\s+([a-zA-Z\s]{2,50})\s+is\s+([0-9.]+(?:\s*[a-zA-Z°/%]+)?)",
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                groups = m.groups()
                if len(groups) == 2:
                    key, val = groups
                elif len(groups) == 3:
                    key = f"{groups[0]} of {groups[1]}"
                    val = groups[2]
                else:
                    continue
                key = key.strip().lower()
                val = val.strip()
                if len(key) < 3 or len(val) < 1 or len(key) > 120:
                    continue
                drafts.append({
                    "key": key,
                    "value": val,
                    "type": "string" if not re.match(r"^[0-9.\-eE]+$", val.split()[0]) else "numeric",
                    "source": entry["source"],
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "status": "draft",
                })
        # Also extract simple "$X cost" or "$X pricing" numeric facts
        for m in re.finditer(r"\$([0-9,]+(?:\.[0-9]+)?)\s*(per|/|month|year|user)?", text):
            price = m.group(1).replace(",", "")
            unit = (m.group(2) or "").strip()
            key_hint = entry.get("source", "unknown").split(":")[-1]
            drafts.append({
                "key": f"price for {key_hint}".lower().replace("/", " ").replace("_", " ")[:80],
                "value": price,
                "type": "numeric",
                "unit": unit or "USD",
                "source": entry["source"],
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "status": "draft",
            })
    return drafts


def deduplicate_against_db(drafts, existing_facts):
    """Remove drafts whose key already exists in facts_db."""
    filtered = []
    for d in drafts:
        if d["key"] not in existing_facts:
            filtered.append(d)
    return filtered


def main():
    harvest = load_json(HARVEST_FILE, {})
    entries = harvest.get("entries", [])
    if not entries:
        print("No harvested entries found. Run harvest_cache.py first.")
        sys.exit(1)

    existing = load_facts_db()
    drafts = extract_candidate_facts(entries)
    drafts = deduplicate_against_db(drafts, existing)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    draft_file = os.path.join(DRAFTS_DIR, f"draft_facts_{today}.json")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_harvest": HARVEST_FILE,
        "draft_count": len(drafts),
        "drafts": drafts,
    }
    save_json(draft_file, report)
    print(f"Extracted {len(drafts)} draft facts")
    print(f"Draft file: {draft_file}")
    return draft_file, len(drafts)


if __name__ == "__main__":
    path, count = main()
    sys.exit(0)
