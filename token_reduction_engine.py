#!/usr/bin/env python3
"""
Token Reduction Engine
---------------------
Provides token budgeting, caching, and deterministic fallback for LLM queries.
Designed to run locally before routing to external LLMs.

Features:
- Token counting (approx using whitespace/punctuation)
- LRU cache with hash-based deduplication
- Budget enforcement (max tokens per query)
- Fallback to deterministic summarization when over budget
- Metrics collection for monitoring
"""

import hashlib
import json
import os
import re
import time
from collections import OrderedDict
from typing import Dict, Tuple, Optional

# Configuration
MAX_TOKENS_PER_QUERY = 512          # Hard limit for any query sent to LLM
CACHE_SIZE_LIMIT = 1000             # Number of query-result pairs to keep
CACHE_TTL_SECONDS = 3600            # 1 hour
TOKEN_ESTIMATE_RATIO = 0.75         # Rough estimate: 1 token ~ 0.75 words
SUMMARIZE_THRESHOLD = 1.2           # Trigger summary if estimate > budget * this

# In-memory cache: {query_hash: (result, timestamp, token_count)}
_query_cache: OrderedDict = OrderedDict()
_cache_hits = 0
_cache_misses = 0
_total_queries = 0
_tokens_saved = 0

def _estimate_tokens(text: str) -> int:
    """Estimate token count using simple word-based approximation."""
    if not text:
        return 0
    words = len(re.findall(r'\b\w+\b', text))
    return int(words / TOKEN_ESTIMATE_RATIO)

def _hash_query(query: str) -> str:
    """Generate SHA-256 hash of query for cache key."""
    return hashlib.sha256(query.encode('utf-8')).hexdigest()

def _get_from_cache(query_hash: str) -> Optional[Tuple[str, int]]:
    """Retrieve cached result if exists and not expired."""
    global _cache_hits, _cache_misses
    if query_hash in _query_cache:
        result, timestamp, token_count = _query_cache[query_hash]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            # Move to end (LRU)
            _query_cache.move_to_end(query_hash)
            _cache_hits += 1
            return result, token_count
        else:
            # Expired: remove
            del _query_cache[query_hash]
    _cache_misses += 1
    return None

def _store_in_cache(query_hash: str, result: str, token_count: int):
    """Store result in LRU cache, evicting oldest if needed."""
    global _query_cache
    _query_cache[query_hash] = (result, time.time(), token_count)
    _query_cache.move_to_end(query_hash)
    if len(_query_cache) > CACHE_SIZE_LIMIT:
        _query_cache.popitem(last=False)

def _deterministic_fallback(query: str) -> str:
    """
    Deterministic summarization fallback when over budget.
    Uses extractive summarization: take first N sentences.
    """
    sentences = re.split(r'(?<=[.!?])\s+', query.strip())
    # Keep enough sentences to stay under budget
    kept = []
    tokens_used = 0
    for sent in sentences:
        sent_tokens = _estimate_tokens(sent)
        if tokens_used + sent_tokens > MAX_TOKENS_PER_QUERY:
            break
        kept.append(sent)
        tokens_used += sent_tokens
    if not kept:
        # Extreme case: return first chunk
        kept = [query[:MAX_TOKENS_PER_QUERY * 4]]  # rough char approx
    return ' '.join(kept)

def reduce_tokens(query: str, force_deterministic: bool = False) -> Dict:
    """
    Main entry point: reduce tokens in query if needed, return reduced query and metadata.
    
    Args:
        query: Original user query
        force_deterministic: If True, skip LLM routing and use deterministic fallback
    
    Returns:
        dict with keys:
        - 'reduced_query': query to send to LLM (or deterministic result)
        - 'original_tokens': estimated token count of original
        - 'reduced_tokens': estimated token count of reduced query
        - 'tokens_saved': difference
        - 'cache_hit': bool
        - 'method': 'cache', 'deterministic', or 'original'
        - 'routing': 'deterministic' or 'external' (based on force flag)
    """
    global _total_queries, _tokens_saved
    _total_queries += 1
    
    query_hash = _hash_query(query)
    cached = _get_from_cache(query_hash)
    if cached:
        result, token_count = cached
        _tokens_saved += MAX_TOKENS_PER_QUERY - token_count  # approximation
        return {
            'reduced_query': result,
            'original_tokens': token_count,
            'reduced_tokens': token_count,
            'tokens_saved': MAX_TOKENS_PER_QUERY - token_count,
            'cache_hit': True,
            'method': 'cache',
            'routing': 'deterministic'  # cached results are treated as deterministic
        }
    
    original_tokens = _estimate_tokens(query)
    
    # If under budget, return as-is (but still cache for future)
    if original_tokens <= MAX_TOKENS_PER_QUERY:
        _store_in_cache(query_hash, query, original_tokens)
        return {
            'reduced_query': query,
            'original_tokens': original_tokens,
            'reduced_tokens': original_tokens,
            'tokens_saved': 0,
            'cache_hit': False,
            'method': 'original',
            'routing': 'deterministic' if force_deterministic else 'external'
        }
    
    # Check if forced deterministic and under budget
    if force_deterministic and original_tokens <= MAX_TOKENS_PER_QUERY:
        reduced = query
    else:
        # Apply deterministic fallback (truncate to fit budget)
        reduced = _deterministic_fallback(query)
    reduced_tokens = _estimate_tokens(reduced)
    
    # Store reduced version in cache (so future similar queries get reduced form)
    _store_in_cache(query_hash, reduced, reduced_tokens)
    
    tokens_saved = original_tokens - reduced_tokens
    _tokens_saved += tokens_saved
    
    return {
        'reduced_query': reduced,
        'original_tokens': original_tokens,
        'reduced_tokens': reduced_tokens,
        'tokens_saved': tokens_saved,
        'cache_hit': False,
        'method': 'deterministic',
        'routing': 'deterministic'  # forced deterministic via fallback
    }

def get_metrics() -> Dict:
    """Return current engine metrics for monitoring."""
    hit_rate = (_cache_hits / (_cache_hits + _cache_misses)) * 100 if (_cache_hits + _cache_misses) > 0 else 0
    avg_tokens_saved = (_tokens_saved / _total_queries) if _total_queries > 0 else 0
    return {
        'total_queries': _total_queries,
        'cache_hits': _cache_hits,
        'cache_misses': _cache_misses,
        'cache_hit_rate_percent': round(hit_rate, 2),
        'cache_size': len(_query_cache),
        'total_tokens_saved': _tokens_saved,
        'average_tokens_saved_per_query': round(avg_tokens_saved, 2)
    }

def clear_cache():
    """Clear the query cache."""
    global _query_cache, _cache_hits, _cache_misses, _total_queries, _tokens_saved
    _query_cache.clear()
    _cache_hits = _cache_misses = _total_queries = _tokens_saved = 0

if __name__ == '__main__':
    # Simple CLI test
    import sys
    if len(sys.argv) > 1:
        test_query = ' '.join(sys.argv[1:])
    else:
        test_query = "Explain the theory of relativity in detail, including both special and general relativity, and discuss its implications for modern physics, cosmology, and technology."
    
    result = reduce_tokens(test_query)
    print(json.dumps(result, indent=2))
    print("\n--- Metrics ---")
    print(json.dumps(get_metrics(), indent=2))