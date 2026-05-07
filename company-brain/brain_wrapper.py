"""
Deterministic Brain Wrapper — Drop-in replacement for agent brain queries.

Usage:
    from brain_wrapper import Brain
    
    b = Brain()
    
    # Moat query — auto-classifies as strategy, searches concepts/
    result = b.query("what is our moat")
    print(result['answer'])
    
    # Product query — auto-classifies as product, searches projects/
    result = b.query("how does faulttrace parse L5X")
    
    # With explicit intent override
    result = b.query("revenue", intent="operations")

Returns:
    {
        "query": str,
        "intent": str,
        "answer": str,   # compiled truth from top result
        "sources": list of {slug, title, score},
        "confidence": float,
    }
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Import router
sys.path.insert(0, str(Path(__file__).parent))
from certainlogic_router import CertainLogicRouter, classify_intent


class Brain:
    """Simplified brain interface for agent skills."""
    
    def __init__(self):
        self._router = CertainLogicRouter()
    
    def query(self, text: str, intent: Optional[str] = None, limit: int = 3) -> dict:
        """
        Query the brain with automatic intent classification and routing.
        
        Args:
            text: The query text
            intent: Optional intent override (strategy|product|data|operations)
            limit: Max results to consider
            
        Returns:
            Structured answer with source attribution
        """
        detected_intent = intent or classify_intent(text)
        result = self._router.query(text, limit=limit)
        
        # Build concise answer from top results
        sources = result.get("results", [])
        if sources:
            top = sources[0]
            answer = top.get("excerpt", "") or top.get("title", "")
            confidence = top.get("score", 0)
        else:
            answer = "No relevant information found in the brain."
            confidence = 0
        
        return {
            "query": text,
            "intent": detected_intent,
            "answer": answer,
            "sources": [
                {"slug": s["slug"], "title": s["title"], "score": s["score"]}
                for s in sources[:limit]
            ],
            "confidence": confidence,
            "brain_query": result,
        }
    
    def strategy(self, query: str) -> dict:
        """Query specifically for strategy/moat content."""
        return self.query(query, intent="strategy")
    
    def product(self, query: str) -> dict:
        """Query specifically for product content."""
        return self.query(query, intent="product")
    
    def metrics(self, query: str) -> dict:
        """Query specifically for metrics/evidence content."""
        return self.query(query, intent="data")
    
    def ops(self, query: str) -> dict:
        """Query specifically for operations content."""
        return self.query(query, intent="operations")


# Convenience: export Brain class as default
__all__ = ["Brain"]
