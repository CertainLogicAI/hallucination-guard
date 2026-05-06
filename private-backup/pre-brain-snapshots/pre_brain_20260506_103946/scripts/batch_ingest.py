#!/usr/bin/env python3
"""Batch ingest existing facts into GBrain Company Brain."""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "company-brain"))
from deterministic_brain import DeterministicBrain, create_intent

BRAIN_API = "http://127.0.0.1:8000"

def get_facts():
    """Fetch facts from Brain API."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"{BRAIN_API}/facts", timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Failed to fetch facts: {e}")
        return None

def ingest_fact(brain, key, value, source="brain-api"):
    """Ingest a single fact into Company Brain."""
    content = f"## {key}\n\n**Value:** {value}\n\n**Source:** {source}\n"
    result = brain.command("brain.put_page", {
        "slug": f"fact/{key.replace(' ', '-').replace('+', 'plus')}",
        "content": content,
        "frontmatter": {
            "title": key,
            "domain": "facts",
            "source": source,
            "type": "fact"
        },
        "source": "batch-ingest"
    })
    return result

def main():
    print("=== Batch Ingest: Brain API → Company Brain ===")
    
    # Ensure intent exists for facts domain
    create_intent("facts", ["brain.put_page", "brain.get_page", "brain.query"], [], [])
    
    brain = DeterministicBrain(domain="facts")
    
    facts_data = get_facts()
    if not facts_data:
        print("❌ Cannot fetch facts from Brain API. Is it running?")
        sys.exit(1)
    
    facts = facts_data.get("facts", {})
    print(f"Found {len(facts)} facts to ingest")
    
    success = 0
    failed = 0
    for key, data in facts.items():
        value = data.get("value", str(data))
        source = data.get("source", "unknown")
        result = ingest_fact(brain, key, value, source)
        if result.get("success"):
            success += 1
            print(f"  ✅ {key}")
        else:
            failed += 1
            print(f"  ❌ {key}: {result.get('error')}")
    
    print(f"\nDone: {success} ingested, {failed} failed")

if __name__ == "__main__":
    main()
