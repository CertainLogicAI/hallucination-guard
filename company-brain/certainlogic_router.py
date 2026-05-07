#!/usr/bin/env python3
"""
CertainLogic Brain Router — Python bridge for skills → brain integration.

Wraps the TypeScript router (certainlogic-router.ts) to provide a clean
Python API for the agent: classify intent, query brain with boosts,
return structured results with source attribution.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from deterministic brain for shared types
sys.path.insert(0, str(Path(__file__).parent))
from deterministic_brain import DeterministicBrain, gbrain_cli


def classify_intent(query: str) -> str:
    """
    Classify intent using the TypeScript intent classifier.
    Returns one of: strategy, product, data, operations, general
    """
    gbrain_path = os.getenv("GBRAIN_PATH", "/data/.openclaw/workspace/company-brain")
    
    # Run the TypeScript intent classifier standalone
    # We create a small TS snippet that imports and calls classifyCertainLogicIntent
    ts_code = f"""
import {{ classifyCertainLogicIntent }} from './src/core/search/certainlogic-intent.ts';
console.log(classifyCertainLogicIntent("{query.replace('"', '\\"')}") || "general");
"""
    
    try:
        cmd = ["bun", "run", "-e", ts_code]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=gbrain_path,
        )
        intent = result.stdout.strip()
        return intent if intent else "general"
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: keyword-based intent detection
        return _keyword_intent(query)


def _keyword_intent(query: str) -> str:
    """Fallback keyword-based intent classification."""
    q_lower = query.lower()
    
    strategy_keywords = ['moat', 'strategy', 'competitive', 'advantage', 'flywheel',
                        'trade secret', 'patent', 'ip strategy']
    product_keywords = ['faulttrace', 'brain api', 'deterministic', 'agentpathfinder',
                       'l5x', 'plc', 'schematic']
    data_keywords = ['benchmark', 'metric', 'accuracy', 'cache hit', 'token saving',
                    'hallucination', 'alignment score', 'performance']
    ops_keywords = ['funding', 'pricing', 'partner', 'yc', 'hackathon', 'team',
                   'revenue', 'roadmap']
    
    for kw in strategy_keywords:
        if kw in q_lower:
            return 'strategy'
    for kw in product_keywords:
        if kw in q_lower:
            return 'product'
    for kw in data_keywords:
        if kw in q_lower:
            return 'data'
    for kw in ops_keywords:
        if kw in q_lower:
            return 'operations'
    
    return 'general'


class CertainLogicRouter:
    """
    Skills router for CertainLogic brain queries.
    
    Usage:
        router = CertainLogicRouter()
        result = router.query("what is our moat strategy")
        # result -> {answer, source_pages, intent, confidence}
    """
    
    def __init__(self, brain: Optional[DeterministicBrain] = None):
        self.brain = brain or DeterministicBrain(domain="default")
    
    def query(self, text: str, limit: int = 5, min_relevance: float = 0.1) -> Dict[str, Any]:
        """
        Execute a routed brain query.
        
        1. Classify intent
        2. Query brain with appropriate source boosts
        3. Return structured result with source attribution
        
        Args:
            text: The user's query
            limit: Max results to return
            min_relevance: Minimum score threshold for results
            
        Returns:
            {
                "query": str,
                "intent": str,
                "results": list of {slug, title, score, excerpt},
                "source_attribution": str,
                "brain_searched": bool,
                "detail_level": str,
            }
        """
        intent = classify_intent(text)
        
        # Map intent to detail level and source boosts
        detail_map = {
            'strategy': 'high',
            'product': 'high',
            'data': 'high',
            'operations': 'medium',
            'general': 'medium',
        }
        detail = detail_map.get(intent, 'medium')
        
        # Source boost prefixes based on intent
        boost_map = {
            'strategy': 'concepts/certainlogic-',
            'product': 'projects/',
            'data': 'family/work/metrics/',
            'operations': 'family/work/',
            'general': 'family/work/',
        }
        boost_prefix = boost_map.get(intent, 'family/work/')
        
        # Execute GBrain query with appropriate detail level
        # GBrain CLI: query <text> [--detail low|medium|high] [--limit N]
        try:
            result = gbrain_cli(["query", text, "--detail", detail, "--limit", str(limit)])
            
            if not result.get("success"):
                return {
                    "query": text,
                    "intent": intent,
                    "results": [],
                    "source_attribution": "brain query failed",
                    "brain_searched": False,
                    "detail_level": detail,
                    "error": result.get("error", "unknown error"),
                }
            
            # Parse results from GBrain output
            raw_output = result.get("output", "")
            parsed_results = self._parse_query_results(raw_output, min_relevance)
            
            # Determine source attribution
            if parsed_results:
                top_prefix = self._get_top_prefix(parsed_results)
                source_attribution = f"brain search ({len(parsed_results)} results, intent: {intent})"
            else:
                source_attribution = "brain search returned no relevant results"
            
            return {
                "query": text,
                "intent": intent,
                "results": parsed_results,
                "source_attribution": source_attribution,
                "brain_searched": True,
                "detail_level": detail,
                "boost_prefix": boost_prefix,
            }
            
        except Exception as e:
            return {
                "query": text,
                "intent": intent,
                "results": [],
                "source_attribution": "query execution error",
                "brain_searched": False,
                "detail_level": detail,
                "error": str(e),
            }
    
    def _parse_query_results(self, raw_output: str, min_relevance: float) -> List[Dict[str, Any]]:
        """Parse GBrain query output into structured results."""
        results = []
        
        # GBrain query output format: [score] slug -- title
        # Example: [0.3404] family/work/evidence/... -- It protects you...
        if isinstance(raw_output, str):
            lines = raw_output.strip().split('\n')
        elif isinstance(raw_output, list):
            lines = [str(item) for item in raw_output]
        else:
            lines = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Try to parse [score] slug -- title
            if line.startswith('[') and ']' in line:
                score_part = line[1:line.index(']')]
                try:
                    score = float(score_part)
                except ValueError:
                    score = 0.0
                
                rest = line[line.index(']')+1:].strip()
                if ' -- ' in rest:
                    slug, title = rest.split(' -- ', 1)
                    slug = slug.strip()
                    title = title.strip()
                    
                    if score >= min_relevance:
                        results.append({
                            "slug": slug,
                            "title": title[:200],  # Truncate long titles
                            "score": score,
                            "excerpt": title,
                        })
        
        return results
    
    def _get_top_prefix(self, results: List[Dict[str, Any]]) -> str:
        """Determine the dominant source prefix from results."""
        if not results:
            return "unknown"
        
        # Get prefix (first 2 path segments) of highest-scoring result
        top_slug = results[0]["slug"]
        parts = top_slug.split('/')
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}/"
        return "unknown"


def test_router():
    """Self-test the router."""
    print("CertainLogic Router — Self Test\n")
    
    router = CertainLogicRouter()
    
    test_queries = [
        "what is our moat strategy",
        "how does faulttrace work",
        "what is our benchmark accuracy",
        "when is our next hackathon",
        "random unrelated query",
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 50}")
        print(f"Query: {query}")
        result = router.query(query, limit=3)
        print(f"Intent: {result['intent']}")
        print(f"Detail: {result['detail_level']}")
        print(f"Boost: {result.get('boost_prefix', 'none')}")
        print(f"Brain searched: {result['brain_searched']}")
        print(f"Source: {result['source_attribution']}")
        print(f"Results: {len(result['results'])}")
        for r in result['results'][:2]:
            print(f"  • [{r['score']:.4f}] {r['slug']} — {r['title'][:60]}...")


if __name__ == "__main__":
    import sys
    test_router()
