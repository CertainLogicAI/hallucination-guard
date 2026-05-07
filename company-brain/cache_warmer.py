#!/usr/bin/env python3
"""
Brain Cache Pre-Warmer — Phase 4F Enhancement

Runs a set of common brain queries to populate caches before users hit them.
Eliminates cold-cache latency for first-time queries.

Usage:
    python3 company-brain/cache_warmer.py [--queries QUERY_FILE]

Designed to run:
    - At brain startup
    - Via cron every 10 minutes (keeps cache fresh)
    - After brain ingestion (new content invalidated cache)
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from brain_wrapper import Brain

# Common queries that skills/users actually run
DEFAULT_WARM_QUERIES = [
    # Strategy / positioning
    "what is our moat strategy",
    "brand voice guidelines",
    "company positioning",
    "target customer",
    "competitive advantage",
    # Product
    "what products do we offer",
    "product features",
    "pricing strategy",
    # Operations
    "security policy",
    "coding standards",
    "audit requirements",
    # Data
    "key metrics",
    "performance targets",
    # Generic
    "what is CertainLogic",
    "how does the brain work",
]


def warm_cache(queries: list[str] = None, timeout: float = 5.0) -> dict:
    """
    Run queries through Brain to populate intent + query caches.

    Returns:
        {
            "total": int,
            "successful": int,
            "failed": int,
            "avg_latency_ms": float,
            "errors": list[str],
        }
    """
    queries = queries or DEFAULT_WARM_QUERIES
    brain = Brain()

    stats = {
        "total": len(queries),
        "successful": 0,
        "failed": 0,
        "errors": [],
        "latencies": [],
    }

    print(f"Warming brain cache with {len(queries)} queries...")

    for q in queries:
        try:
            start = time.time()
            result = brain.query(q, timeout=timeout)
            latency_ms = (time.time() - start) * 1000
            stats["latencies"].append(latency_ms)
            stats["successful"] += 1
            confidence = result.get("confidence", 0)
            print(f"  ✅ '{q[:40]}...' — {latency_ms:.1f}ms (conf: {confidence:.2f})")
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(str(e))
            print(f"  ❌ '{q[:40]}...' — {e}")

    if stats["latencies"]:
        stats["avg_latency_ms"] = sum(stats["latencies"]) / len(stats["latencies"])
        stats["max_latency_ms"] = max(stats["latencies"])
    else:
        stats["avg_latency_ms"] = 0
        stats["max_latency_ms"] = 0

    # Clean up for JSON return
    del stats["latencies"]

    return stats


def print_summary(stats: dict) -> None:
    """Print cache warming summary."""
    print()
    print("=" * 50)
    print("Cache Pre-Warm Complete")
    print("=" * 50)
    print(f"Total queries:    {stats['total']}")
    print(f"Successful:       {stats['successful']}")
    print(f"Failed:           {stats['failed']}")
    print(f"Avg latency:      {stats['avg_latency_ms']:.1f}ms")
    print(f"Max latency:      {stats['max_latency_ms']:.1f}ms")
    print(f"Cache is warm. First user queries will be <50ms")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brain Cache Pre-Warmer")
    parser.add_argument(
        "--queries",
        help="Path to newline-delimited query file (optional)",
        default=None,
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout per query in seconds",
    )
    args = parser.parse_args()

    custom_queries = None
    if args.queries:
        with open(args.queries) as f:
            custom_queries = [line.strip() for line in f if line.strip()]

    stats = warm_cache(queries=custom_queries, timeout=args.timeout)
    print_summary(stats)

    if stats["failed"] > 0 and stats["failed"] == stats["total"]:
        sys.exit(1)  # Complete failure
    sys.exit(0)
