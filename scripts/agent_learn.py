#!/usr/bin/env python3
"""
Agent Learning Loop — seeds per-agent cache into Brain API.

Looks for *_cache_seed.json files, seeds facts into Brain API
with --limit per agent (--limit 20 default). --all iterates all agents.
"""
import argparse
import json
import os
import requests
import sys
import glob
from datetime import datetime, timezone

BRAIN_URL = "http://127.0.0.1:8000"
WORKSPACE = "/data/.openclaw/workspace"
SEED_PATTERN = os.path.join(WORKSPACE, "*_cache_seed.json")
LOG_PATH = os.path.join(WORKSPACE, "brain-internal", "agent_learn.log")


def log(msg):
    ts = datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def check_exists(key):
    try:
        resp = requests.get(f"{BRAIN_URL}/facts/search", params={"q": key}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("count", 0) > 0
    except Exception:
        pass
    return False


def seed_fact(key, entry, agent_tag):
    payload = {
        "key": key,
        "type": entry.get("type", "string"),
        "value": str(entry.get("value", "")),
        "source": entry.get("source", f"{agent_tag}_cache_seed"),
    }
    resp = requests.post(f"{BRAIN_URL}/facts", json=payload, timeout=10)
    return resp.status_code == 201


def agent_from_filename(path):
    """coding_cache_seed.json → coder, marketing_cache_seed.json → marketing"""
    fname = os.path.basename(path)
    return fname.replace("_cache_seed.json", "")


def process_agent(agent_name, seed_path, limit):
    with open(seed_path, "r") as f:
        data = json.load(f)

    facts = data.get("facts", {})
    candidates = list(facts.items())[:limit]

    added = 0
    skipped = 0
    failed = 0

    for key, entry in candidates:
        if check_exists(key):
            skipped += 1
            continue
        try:
            if seed_fact(key, entry, agent_name):
                added += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            log(f"ERROR seeding '{key}' for {agent_name}: {e}")

    return added, skipped, failed, len(facts)


def main():
    parser = argparse.ArgumentParser(description="Agent Learning Loop")
    parser.add_argument("--all", action="store_true", help="Run for all agents")
    parser.add_argument("--limit", type=int, default=20, help="Max entries per agent")
    parser.add_argument("--agents", nargs="+", default=[], help="Specific agent names")
    args = parser.parse_args()

    if not (args.all or args.agents):
        parser.print_help()
        sys.exit(1)

    # Collect agent seed files
    all_seeds = glob.glob(SEED_PATTERN)
    agent_map = {agent_from_filename(p): p for p in all_seeds}

    # Determine which agents to run
    if args.all:
        targets = sorted(agent_map.keys())
    else:
        targets = [a for a in args.agents if a in agent_map]

    log(f"Starting agent learning loop — limit={args.limit}, agents={targets}")

    results = {}
    for agent in targets:
        path = agent_map[agent]
        added, skipped, failed, total = process_agent(agent, path, args.limit)
        results[agent] = {
            "seeded": added,
            "skipped": skipped,
            "failed": failed,
            "candidates": total,
        }
        log(f"Agent '{agent}': seeded={added}, skipped={skipped}, failed={failed}, candidates={total}")

    # Print report
    print("\n**Agent Learning Loop Report** — {} UTC\n".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")))
    if not results:
        print("No agents processed.")
        return
    print("Seeded counts per agent:")
    total_seeded = 0
    for agent, res in sorted(results.items()):
        print(f"- **{agent}**: {res['seeded']} (candidates: {res['candidates']}, skipped: {res['skipped']}, failed: {res['failed']})")
        total_seeded += res['seeded']
    print(f"\n**Total**: {total_seeded} entries seeded")


if __name__ == "__main__":
    main()
