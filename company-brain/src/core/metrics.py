"""
Metrics — Brain OS Observability

Lightweight metric recording for brain queries. Logs every query
with latency, intent, confidence, and result status.

Usage:
    from metrics import record_query, get_daily_stats
    
    record_query(query="moat", intent="strategy", confidence=0.34, 
                 latency_ms=45, hit=True, error=None)
    
    stats = get_daily_stats("2026-05-07")
    # {'queries': 42, 'hit_rate': 0.85, 'avg_latency_ms': 45, ...}
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Any

LOG_DIR = Path("/data/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def record_query(query: str, intent: str, confidence: float,
                 latency_ms: float, hit: bool = True,
                 error: Optional[str] = None,
                 brain_sourced: bool = False) -> None:
    """
    Record a single brain query metric.
    
    Args:
        query: The query text (redacted before logging)
        intent: Classified intent
        confidence: Result confidence score
        latency_ms: Query latency in milliseconds
        hit: Whether a result was found above threshold
        error: Error message if query failed
        brain_sourced: Whether result came from brain (not fallback)
    """
    entry = {
        "timestamp": time.time(),
        "query_length": len(query) if query else 0,
        "intent": intent,
        "confidence": confidence,
        "latency_ms": round(latency_ms, 2),
        "hit": hit,
        "error": error,
        "brain_sourced": brain_sourced,
    }

    date = time.strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"brain-metrics-{date}.jsonl"

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_daily_stats(date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Get aggregated stats for a given date.
    
    Args:
        date_str: Date in YYYY-MM-DD format. Defaults to today.
    
    Returns:
        Dictionary with aggregated metrics
    """
    if date_str is None:
        date_str = time.strftime("%Y-%m-%d")

    log_file = LOG_DIR / f"brain-metrics-{date_str}.jsonl"
    if not log_file.exists():
        return {
            "date": date_str,
            "queries": 0,
            "hit_rate": 0.0,
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "brain_sourced_rate": 0.0,
            "top_intents": {},
        }

    queries = []
    with open(log_file) as f:
        for line in f:
            try:
                queries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not queries:
        return {
            "date": date_str,
            "queries": 0,
            "hit_rate": 0.0,
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "brain_sourced_rate": 0.0,
            "top_intents": {},
        }

    total = len(queries)
    hits = sum(1 for q in queries if q.get("hit", False))
    errors = sum(1 for q in queries if q.get("error"))
    sourced = sum(1 for q in queries if q.get("brain_sourced", False))
    latencies = [q.get("latency_ms", 0) for q in queries]

    # Intent distribution
    intents = {}
    for q in queries:
        intent = q.get("intent", "unknown")
        intents[intent] = intents.get(intent, 0) + 1

    return {
        "date": date_str,
        "queries": total,
        "hit_rate": round(hits / total, 4),
        "error_rate": round(errors / total, 4),
        "brain_sourced_rate": round(sourced / total, 4),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
        "p95_latency_ms": round(sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0, 2),
        "top_intents": intents,
    }
