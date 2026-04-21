#!/usr/bin/env python3
"""
LangChain integration example for Hallucination Guard.

Demonstrates two patterns:
1. Callback handler — auto-validates every LLM response
2. LCEL Runnable — compose validation into pipelines

Prerequisites:
    pip install hallucination-guard langchain-core langchain-openai

Usage:
    # Pattern 1: Callback (validates silently, logs warnings)
    python examples/langchain_integration.py

    # Set OPENAI_API_KEY to run with a real LLM
"""

from __future__ import annotations


def demo_callback_pattern():
    """Pattern 1: Callback handler — drop-in validation for any LLM."""
    print("=== Pattern 1: Callback Handler ===\n")

    from hallucination_guard.integrations.langchain import HallucinationGuardCallback

    # Create callback that logs hallucinations
    flagged_responses = []

    def on_flag(query, response, result):
        flagged_responses.append(
            {
                "query": query,
                "confidence": result["confidence"],
                "flags": result["flags"],
            }
        )

    callback = HallucinationGuardCallback(
        raise_on_hallucination=False,  # log only, don't raise
        on_flag=on_flag,
    )

    print("Callback created. Attach to any LangChain LLM:")
    print("  llm = ChatOpenAI(callbacks=[callback])")
    print("  llm.invoke('What is 2+2?')  # validated automatically")
    print()

    # Direct validation demo (no LLM needed)
    result = callback._validate(callback, "What is 2+2?", "The answer is 4")
    print(
        f"Validated '2+2 = 4': valid={result['valid']}, confidence={result['confidence']}"
    )

    result = callback._validate(callback, "How much does GPT-5 cost?", "$500/month")
    print(
        f"Validated 'GPT-5 = $500': valid={result['valid']}, "
        f"confidence={result['confidence']}"
    )

    if flagged_responses:
        print(f"\n⚠️ Flagged {len(flagged_responses)} response(s):")
        for f in flagged_responses:
            print(f"  - {f['flags']}")
    print()


def demo_runnable_pattern():
    """Pattern 2: LCEL Runnable — compose into pipelines."""
    print("=== Pattern 2: LCEL Runnable ===\n")

    from hallucination_guard.integrations.langchain import HallucinationGuardChain

    guard = HallucinationGuardChain()

    # Direct validation
    result = guard.validate(
        "The capital of France is Paris", query="What is the capital of France?"
    )
    print(f"Validated 'capital of France = Paris': valid={result['valid']}")

    # As a runnable in a pipeline
    runnable = guard.as_runnable()
    try:
        output = runnable.invoke("The answer is 4")
        print(f"Runnable passed: {output}")
    except ValueError as e:
        print(f"Runnable blocked: {e}")

    print()
    print("Use in LCEL pipeline:")
    print("  chain = ChatOpenAI() | StrOutputParser() | guard.as_runnable()")
    print("  chain.invoke('What is 2+2?')  # hallucinations blocked")


if __name__ == "__main__":
    try:
        demo_callback_pattern()
        demo_runnable_pattern()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install langchain-core")
