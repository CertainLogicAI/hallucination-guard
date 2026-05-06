#!/usr/bin/env python3
"""Coding Query Cache Tracker — Daily hit rate logging."""

import json
import os
import re
from datetime import datetime, date
from pathlib import Path

LOG_DIR = Path("/data/.openclaw/workspace/logs")
LOG_FILE = LOG_DIR / "coding_queries.jsonl"
DAILY_REPORT_DIR = LOG_DIR / "daily_reports"

# Ensure dirs exist
LOG_DIR.mkdir(exist_ok=True)
DAILY_REPORT_DIR.mkdir(exist_ok=True)

# Coding-related keywords for categorization
CODING_PATTERNS = [
    r"\b(code|coding|script|function|class|module|import|debug|refactor|build|compile|deploy|git|commit|pull|push|merge|branch|test|pytest|unit test|integration test|lint|format|prettier|eslint|typescript|javascript|python|go|rust|java|c\+\+|bash|shell|docker|kubernetes|k8s|api|endpoint|route|middleware|database|sql|query|migration|schema|frontend|backend|fullstack|react|vue|angular|node|express|fastapi|django|flask|spring|server|client|http|rest|graphql|websocket|auth|jwt|oauth|token|session|cookie|cache|redis|queue|worker|cron|job|lambda|serverless|cloud|aws|gcp|azure|terraform|ansible|ci/cd|pipeline|github actions|jenkins|travis|circleci|Makefile|cmake|gradle|maven|webpack|vite|rollup|esbuild|parcel|npm|yarn|pnpm|pip|conda|venv|virtualenv|requirements|package\.json|Cargo\.toml|pom\.xml|build\.gradle|dockerfile|docker-compose|helm|chart|namespace|pod|service|ingress|load balancer|ssl|tls|certificate|domain|dns|cdn|proxy|reverse proxy|nginx|apache|caddy)\b",
    r"\b(fix|bug|error|exception|traceback|stack trace|crash|broken|fails?|pass(es)?|fail(ed|ure)?|assert|expected|actual|got|want|should|must|need to|how to (write|create|build|implement|fix|debug|test|deploy))\b"
]

def is_coding_query(query: str) -> bool:
    """Check if query is coding-related."""
    query_lower = query.lower()
    return any(re.search(p, query_lower, re.IGNORECASE) for p in CODING_PATTERNS)

def log_query(query: str, cache_hit: bool, tokens_saved: int = 0, response_time_ms: float = 0.0):
    """Log a query to the daily log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": date.today().isoformat(),
        "query": query[:200],  # Truncate for privacy
        "is_coding": is_coding_query(query),
        "cache_hit": cache_hit,
        "tokens_saved": tokens_saved,
        "response_time_ms": response_time_ms
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_daily_summary(target_date: date = None) -> dict:
    """Generate daily summary for a given date."""
    target_date = target_date or date.today()
    target_str = target_date.isoformat()
    
    coding_queries = 0
    coding_hits = 0
    non_coding_queries = 0
    total_tokens_saved = 0
    total_response_time = 0.0
    
    if not LOG_FILE.exists():
        return {"date": target_str, "error": "No log file"}
    
    with open(LOG_FILE) as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry.get("date") != target_str:
                continue
            
            if entry.get("is_coding"):
                coding_queries += 1
                if entry.get("cache_hit"):
                    coding_hits += 1
            else:
                non_coding_queries += 1
                
            total_tokens_saved += entry.get("tokens_saved", 0)
            total_response_time += entry.get("response_time_ms", 0.0)
    
    total_queries = coding_queries + non_coding_queries
    hit_rate = (coding_hits / coding_queries * 100) if coding_queries > 0 else 0.0
    avg_response_time = (total_response_time / total_queries) if total_queries > 0 else 0.0
    
    return {
        "date": target_str,
        "coding_queries": coding_queries,
        "coding_cache_hits": coding_hits,
        "coding_hit_rate_percent": round(hit_rate, 2),
        "non_coding_queries": non_coding_queries,
        "total_queries": total_queries,
        "total_tokens_saved": total_tokens_saved,
        "avg_response_time_ms": round(avg_response_time, 2)
    }

def save_daily_report(target_date: date = None):
    """Save daily report to file."""
    summary = get_daily_summary(target_date)
    report_file = DAILY_REPORT_DIR / f"coding_queries_{summary['date']}.json"
    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def get_historical_hit_rates(days: int = 7) -> list:
    """Get hit rates for last N days."""
    results = []
    for i in range(days):
        d = date.today() - __import__("datetime").timedelta(days=i)
        summary = get_daily_summary(d)
        results.append({
            "date": summary["date"],
            "coding_queries": summary["coding_queries"],
            "hit_rate": summary["coding_hit_rate_percent"]
        })
    return list(reversed(results))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--today":
        summary = save_daily_report()
        print(json.dumps(summary, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--history":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        history = get_historical_hit_rates(days)
        print(json.dumps(history, indent=2))
    else:
        print("Usage: python3 coding_query_tracker.py --today | --history [days]")
