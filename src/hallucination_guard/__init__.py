#!/usr/bin/env python3
"""
Hallucination Guard package.
Deterministic verification for AI-generated content.
"""

from .deterministic_memory_search import search_memory
from .hallucination_detector import HallucinationDetector
from .intent_router import IntentRouter
from .token_reduction_engine import get_metrics, reduce_tokens

__version__ = "0.1.0"

__all__ = [
    "HallucinationDetector",
    "reduce_tokens",
    "get_metrics",
    "search_memory",
    "IntentRouter",
]
