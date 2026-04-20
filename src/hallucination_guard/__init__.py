#!/usr/bin/env python3
"""
Hallucination Guard package.
Deterministic verification for AI-generated content.
"""

from .hallucination_detector import HallucinationDetector
from .token_reduction_engine import reduce_tokens, get_metrics
from .deterministic_memory_search import search_memory
from .intent_router import IntentRouter
import sys

__version__ = "0.1.0"

__all__ = [
    "HallucinationDetector",
    "reduce_tokens",
    "get_metrics",
    "search_memory",
    "IntentRouter",
]