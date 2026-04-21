#!/usr/bin/env python3
"""
Hallucination Guard — deterministic verification for AI-generated content.

CertainLogic Verifier catches hallucinations, reduces token costs, and provides
audit-ready logging for regulated industries. Self-hosted, air-gapped, MIT licensed.

Quick start::

    from hallucination_guard import HallucinationDetector

    detector = HallucinationDetector()
    result = detector.validate("What is 2+2?", "4")
    print(result["valid"])  # True
"""

from .deterministic_memory_search import search_memory
from .hallucination_detector import HallucinationDetector
from .intent_router import IntentRouter
from .packs import get_active_cache_path, get_active_facts_path, install_pack, pack_status, update_pack
from .token_reduction_engine import get_metrics, reduce_tokens

__version__ = "0.1.0"

__all__ = [
    "HallucinationDetector",
    "reduce_tokens",
    "get_metrics",
    "search_memory",
    "IntentRouter",
    "install_pack",
    "update_pack",
    "pack_status",
    "get_active_facts_path",
    "get_active_cache_path",
]
