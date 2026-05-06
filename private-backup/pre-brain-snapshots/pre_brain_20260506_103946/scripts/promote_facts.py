#!/usr/bin/env python3
"""
Promote Facts - Promotes reviewed draft facts into facts_db.json.
Usage:
  python3 promote_facts.py <draft_file>
  python3 promote_facts.py drafts/draft_facts_YYYY-MM-DD.json

Prints a prompt for Anton with the draft summary and promotion command.
"""

import json
import os
import sys
from datetime import datetime, timezone

WORKSPACE = "/data/.openclaw/workspace"
FACTS_DB = os.path.join(WORKSPACE, "facts_db.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_facts_db():
    if not os.path.exists(FACTS_DB):
        return {"_meta": {"version": "1.0", "last_updated": ""}, "facts": {}}
    return load_json(FACTS_DB)


def promote_drafts(draft_path, dry_run=False):
    if not os.path.exists(draft_path):
        print(f"ERROR: Draft file not found: {draft_path}")
        sys.exit(1)

    draft_data = load_json(draft_path)
    drafts = draft_data.get("drafts", [])
    db = load_facts_db()
    promoted = 0
    skipped = 0

    for d in drafts:
        key = d.get("key", "").strip().lower()
        if not key:
            continue
        if key in db.get("facts", {}):
            skipped += 1
            continue
        fact_entry = {
            "type": d.get("type", "string"),
            "value": d.get("value", ""),
            "source": d.get("source", "draft-import"),
        }
        if d.get("unit"):
            fact_entry["unit"] = d["unit"]
        if d.get("tolerance") is not None:
            fact_entry["tolerance"] = d["tolerance"]
        db["facts"][key] = fact_entry
        promoted += 1

    db["_meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not dry_run:
        save_json(FACTS_DB, db)

    return promoted, skipped, len(drafts)


def print_prompt(draft_path, total, promoted, skipped):
    print("=" * 60)
    print("📝  FACT REVIEW PROMPT FOR ANTON")
    print("=" * 60)
    print(f"Draft file: {draft_path}")
    print(f"Total draft facts: {total}")
    print(f"Ready to promote: {promoted}")
    print(f"Already in DB (will skip): {skipped}")
    print("")
    print("Command to promote reviewed facts:")
    print(f"  python3 {os.path.join(WORKSPACE, 'scripts/promote_facts.py')} {draft_path}")
    print("")
    print("To review first, open the draft file and edit the 'drafts' list.")
    print("Remove any entries you don't want promoted, then run the above.")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 promote_facts.py <draft_file>")
        sys.exit(1)

    draft_path = sys.argv[1]
    if not os.path.isabs(draft_path):
        draft_path = os.path.join(WORKSPACE, draft_path)

    dry_run = "--dry-run" in sys.argv

    promoted, skipped, total = promote_drafts(draft_path, dry_run=dry_run)

    if dry_run:
        print(f"[DRY RUN] Would promote {promoted}, skip {skipped} out of {total}")
    else:
        print(f"Promoted {promoted} facts, skipped {skipped} duplicates.")
        print(f"Updated: {FACTS_DB}")

    print_prompt(draft_path, total, promoted, skipped)


if __name__ == "__main__":
    main()
