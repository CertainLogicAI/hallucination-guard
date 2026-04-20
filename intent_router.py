#!/usr/bin/env python3
"""
CertainLogic Verifier - Intent Router
Thin orchestration layer: reduce → classify → return routing decision.
MIT License
"""

from token_reduction_engine import reduce
from intent_classifier import classify, IntentResult


class IntentRouter:
    """Orchestrates token reduction and intent classification."""

    def route(self, text: str) -> dict:
        """
        Route a query through reduction + classification.

        Returns:
            dict with original, compressed, token_count, intent, openclaw_model, brain_handler
        """
        compressed, token_count = reduce(text)
        result: IntentResult = classify(compressed, token_count)
        return {
            "original": text,
            "compressed": compressed,
            "token_count": token_count,
            "intent": result,
            "openclaw_model": result.openclaw_model,
            "brain_handler": result.brain_handler,
        }

    def route_for_brain(self, text: str) -> str:
        """Convenience method — returns just the brain_handler string."""
        return self.route(text)["brain_handler"]