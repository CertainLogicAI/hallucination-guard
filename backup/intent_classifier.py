#!/usr/bin/env python3
"""
CertainLogic Verifier - Intent Classifier
Pure rules‑based intent classification without LLM calls.
Classifies query complexity, domain, and recommended routing.
MIT License
"""

import os
import re
from dataclasses import dataclass
from typing import Optional

# Known facts domains for coverage check — can be overridden via env
DEFAULT_FACTS_DOMAINS = {
    "plc", "l5x", "faulttrace", "fault", "trace",
    "iec", "iso", "nfpa", "osha",
    "compliance", "standard", "standards",
}
FACTS_DOMAINS = set(os.getenv("FACTS_DOMAINS", "").split(",")) if os.getenv("FACTS_DOMAINS") else DEFAULT_FACTS_DOMAINS

# Model names (configurable via env)
MODEL_HAIKU = os.getenv("MODEL_HAIKU", "anthropic/claude-haiku-4-5")
MODEL_SONNET = os.getenv("MODEL_SONNET", "anthropic/claude-sonnet-4-6")
MODEL_OPUS = os.getenv("MODEL_OPUS", "anthropic/claude-opus-4-6")

ESCALATION_MAP = {
    MODEL_HAIKU: MODEL_SONNET,
    MODEL_SONNET: MODEL_SONNET,  # sonnet stays sonnet
    MODEL_OPUS: MODEL_OPUS,
}

# Greeting / status patterns
GREETING_PATTERNS = re.compile(
    r"^(hi|hello|hey|howdy|yo|sup|good\s+\w+|what'?s\s+up|how\s+are\s+you|ping|status|ok\??|okay\??)[\s!?.,]*$",
    re.IGNORECASE,
)

HEARTBEAT_PATTERN = re.compile(
    r"\b(heartbeat|health\s*check|health|alive|ping|are\s+you\s+up|is\s+it\s+running|still\s+running|is\s+the\s+\w+\s+up)\b",
    re.IGNORECASE,
)

CODE_PATTERN = re.compile(
    r"\b(code|build|write|generate|implement|create|develop|script|function|program|refactor|debug|fix|add|document|docs|deploy|test|install|configure|update|migrate|integrate)\b",
    re.IGNORECASE,
)

COMPLIANCE_PATTERN = re.compile(
    r"\b(compliance|audit|safety|plc|l5x|regulation|regulatory|iec|iso|nfpa|osha|standard|standards|faulttrace|fault\s+trace)\b",
    re.IGNORECASE,
)

ARCHITECTURE_PATTERN = re.compile(
    r"\b(architecture|architect|patent|strategy|strategic|design|system\s+design|roadmap|blueprint|infrastructure)\b",
    re.IGNORECASE,
)

MULTI_PART_PATTERN = re.compile(
    r"(\band\b.*\band\b|\bfirst\b.*\bthen\b|\bstep\s+\d|\b\d+\.\s)",
    re.IGNORECASE,
)


@dataclass
class IntentResult:
    complexity: str        # "simple" | "moderate" | "complex"
    domain: str            # "status" | "code" | "compliance" | "creative" | "general"
    openclaw_model: str    # model name (configurable)
    brain_handler: str     # "cache" | "facts" | "llm"
    confidence: float      # 0.0–1.0
    reasoning: str


def _check_facts_coverage(text: str) -> bool:
    """Return True if query has keyword overlap with known facts domains."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return bool(words & FACTS_DOMAINS)


def classify(text: str, token_count: Optional[int] = None) -> IntentResult:
    """
    Classify query intent using pure rules. First match wins.

    Args:
        text: Query text (ideally already compressed)
        token_count: Pre-computed token count; estimated if None

    Returns:
        IntentResult with routing metadata
    """
    if token_count is None:
        # Simple word-based estimate matching token_reduction_engine logic
        words = len(re.findall(r"\b\w+\b", text))
        token_count = int(words / 0.75)

    question_marks = text.count("?")

    result: Optional[IntentResult] = None

    # Domain-specific patterns take priority over length-based rules
    # Rule 1: heartbeat / health (most specific, highest confidence)
    if HEARTBEAT_PATTERN.search(text):
        result = IntentResult(
            complexity="simple",
            domain="status",
            openclaw_model=MODEL_HAIKU,
            brain_handler="cache",
            confidence=0.95,
            reasoning="Heartbeat/health keyword detected; using cache handler.",
        )

    # Rule 2: code / build / generate
    elif CODE_PATTERN.search(text):
        result = IntentResult(
            complexity="moderate",
            domain="code",
            openclaw_model=MODEL_SONNET,
            brain_handler="llm",
            confidence=0.85,
            reasoning="Code/build/generate keyword detected.",
        )

    # Rule 3: compliance / audit / safety / PLC / L5X
    elif COMPLIANCE_PATTERN.search(text):
        result = IntentResult(
            complexity="moderate",
            domain="compliance",
            openclaw_model=MODEL_SONNET,
            brain_handler="facts",
            confidence=0.85,
            reasoning="Compliance/safety/PLC keyword detected; checking facts DB.",
        )

    # Rule 4: architecture / patent / strategy / design
    elif ARCHITECTURE_PATTERN.search(text):
        result = IntentResult(
            complexity="complex",
            domain="general",
            openclaw_model=MODEL_SONNET,
            brain_handler="llm",
            confidence=0.80,
            reasoning="Architecture/strategy/design keyword detected.",
        )

    # Rule 5: simple greeting / very short (after domain patterns)
    elif token_count <= 10 or GREETING_PATTERNS.match(text.strip()):
        result = IntentResult(
            complexity="simple",
            domain="status",
            openclaw_model=MODEL_HAIKU,
            brain_handler="cache",
            confidence=0.9,
            reasoning="Short or greeting-pattern query routed to cache.",
        )

    # Rule 6: long, multi-question, or multi-part
    elif token_count > 200 or question_marks >= 2 or MULTI_PART_PATTERN.search(text):
        result = IntentResult(
            complexity="complex",
            domain="general",
            openclaw_model=MODEL_SONNET,
            brain_handler="llm",
            confidence=0.75,
            reasoning=(
                f"Complex query: token_count={token_count}, "
                f"question_marks={question_marks}, multi_part={bool(MULTI_PART_PATTERN.search(text))}."
            ),
        )

    # Default fallback
    else:
        result = IntentResult(
            complexity="moderate",
            domain="general",
            openclaw_model=MODEL_SONNET,
            brain_handler="llm",
            confidence=0.60,
            reasoning="No specific pattern matched; using default sonnet/llm routing.",
        )

    # Escalation rule: confidence < 0.65 → bump model up one tier
    if result.confidence < 0.65:
        original_model = result.openclaw_model
        result.openclaw_model = ESCALATION_MAP.get(result.openclaw_model, MODEL_SONNET)
        if result.openclaw_model != original_model:
            result.reasoning += f" (escalated from {original_model} due to low confidence)"

    # Facts coverage check
    if result.brain_handler == "facts":
        if not _check_facts_coverage(text):
            result.brain_handler = "llm"
            result.reasoning += " Facts coverage check failed (no domain keyword overlap); downgraded to llm."

    return result