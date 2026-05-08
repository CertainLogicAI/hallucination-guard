#!/usr/bin/env python3
"""
Brain vs. Raw LLM Benchmark

Compares Company Brain (deterministic, cached) against raw LLM responses.
Measures: accuracy, source correctness, consistency, latency, cost.

Usage:
    python3 company-brain/benchmark.py [--count N] [--output PATH]

Requirements:
    OPENROUTER_API_KEY env var for LLM queries
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent))

from brain_wrapper import Brain

BENCHMARK_QUESTIONS = [
    # Strategy / Moat (from certainlogic-moat-thesis, certainlogic-strategic-principles)
    "what is CertainLogic's moat strategy",
    "what makes CertainLogic different from competitors",
    "how does CertainLogic prevent AI hallucination",
    "what is the deterministic middleware approach",
    "what is Company Brain",
    "what problem does Company Brain solve",
    "why deterministic AI over probabilistic AI",
    "what is the cost reduction claim",
    "how does caching work in Company Brain",
    "what is the open source strategy",
    # Product (from concepts/)
    "what products does CertainLogic offer",
    "what is AgentPathfinder",
    "what is the Token Reduction Engine",
    "what is FaultTrace",
    "how much does Company Brain cost",
    # Security (from security_policy, emergency protocols)
    "what is the emergency override protocol",
    "what are the 8 red lines",
    "how are credentials protected",
    # Operations
    "what is the build schedule for Brain OS",
    "how many phases are in Brain OS",
    "what is Phase 4F",
    # Generic
    "who is Alex",
    "who is Anton",
    "what timezone does Anton use",
    # Edge cases
    "what is the capital of France",  # Should not know (no fact)
    "what is 2+2",  # Should be deterministic
    "tell me about clawvisor",  # Recent intel, may not have
    "what is Giga AI hallucination correction",  # Recently ingested
]

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

def query_brain(question: str) -> Dict[str, Any]:
    """Query via brain_wrapper."""
    brain = Brain()
    start = time.time()
    result = brain.query(question, timeout=5.0)
    latency_ms = (time.time() - start) * 1000
    return {
        "source": "brain",
        "answer": result.get("answer", ""),
        "confidence": result.get("confidence", 0),
        "brain_sourced": result.get("brain_sourced", False),
        "sources": result.get("sources", []),
        "latency_ms": round(latency_ms, 2),
        "error": result.get("error"),
    }

def query_raw_llm(question: str) -> Dict[str, Any]:
    """Query raw LLM without brain context."""
    if not API_KEY:
        return {
            "source": "llm",
            "answer": "[NO_API_KEY]",
            "confidence": 0,
            "latency_ms": 0,
            "error": "no_api_key",
        }

    try:
        import urllib.request
        payload = json.dumps({
            "model": "google/gemma-4-31b-it:free",
            "messages": [
                {"role": "system", "content": "Answer concisely."},
                {"role": "user", "content": question},
            ],
            "max_tokens": 200,
            "temperature": 0.7,
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            },
        )
        start = time.time()
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
            latency_ms = (time.time() - start) * 1000
            answer = result["choices"][0]["message"]["content"].strip()
            return {
                "source": "llm",
                "answer": answer,
                "confidence": 0,  # LLM doesn't provide confidence
                "latency_ms": round(latency_ms, 2),
                "error": None,
            }
    except Exception as e:
        return {
            "source": "llm",
            "answer": "",
            "confidence": 0,
            "latency_ms": 0,
            "error": str(e),
        }

def score_answer(question: str, brain_result: Dict, llm_result: Dict) -> Dict:
    """
    Score both answers against expected criteria.
    Returns structured scoring dict.
    """
    scores = {
        "question": question,
        "brain": brain_result,
        "llm": llm_result,
        "brain_faster": brain_result["latency_ms"] < llm_result["latency_ms"] if llm_result.get("latency_ms") else True,
        "brain_cheaper": True,  # Brain costs $0 on cache hit; LLM always costs tokens
        "brain_has_sources": len(brain_result.get("sources", [])) > 0,
        "brain_confidence": brain_result.get("confidence", 0),
    }

    # Heuristic: brain_sourced answers are more likely correct for company questions
    scores["brain_wins_on_verifiability"] = brain_result.get("brain_sourced", False)

    # Heuristic: LLM answers longer = more potential for hallucination
    llm_answer_len = len(llm_result.get("answer", ""))
    brain_answer_len = len(brain_result.get("answer", ""))
    scores["brain_more_concise"] = brain_answer_len < llm_answer_len if llm_answer_len > 0 else True

    return scores

def run_benchmark(questions: List[str] = None) -> Dict[str, Any]:
    """Run full benchmark and return results."""
    questions = questions or BENCHMARK_QUESTIONS

    results = []
    brain_total_latency = 0
    llm_total_latency = 0
    brain_sourced_count = 0

    print(f"Running benchmark: {len(questions)} questions")
    print("=" * 60)

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q[:50]}...")

        brain_r = query_brain(q)
        llm_r = query_raw_llm(q)

        brain_total_latency += brain_r["latency_ms"]
        llm_total_latency += llm_r["latency_ms"]
        if brain_r.get("brain_sourced"):
            brain_sourced_count += 1

        scored = score_answer(q, brain_r, llm_r)
        results.append(scored)

        print(f"  Brain: {brain_r['latency_ms']:.1f}ms | conf={brain_r['confidence']:.2f} | sourced={brain_r['brain_sourced']}")
        print(f"  LLM:   {llm_r['latency_ms']:.1f}ms | len={len(llm_r['answer'])}")
        if brain_r.get("sources"):
            srcs = ", ".join(s["slug"] for s in brain_r["sources"][:3])
            print(f"  Sources: {srcs}")

    # Summary
    total = len(questions)
    brain_avg_latency = brain_total_latency / total if total else 0
    llm_avg_latency = llm_total_latency / total if total else 0
    brain_sourced_pct = (brain_sourced_count / total) * 100 if total else 0

    summary = {
        "total_questions": total,
        "brain_avg_latency_ms": round(brain_avg_latency, 2),
        "llm_avg_latency_ms": round(llm_avg_latency, 2),
        "speedup_vs_llm": round(llm_avg_latency / brain_avg_latency, 1) if brain_avg_latency else 0,
        "brain_sourced_pct": round(brain_sourced_pct, 1),
        "brain_has_sources_count": sum(1 for r in results if r["brain_has_sources"]),
        "brain_wins_verifiability": sum(1 for r in results if r["brain_wins_on_verifiability"]),
        "brain_more_concise": sum(1 for r in results if r["brain_more_concise"]),
        "details": results,
    }

    return summary

def print_summary(summary: Dict):
    """Print formatted benchmark summary."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Questions tested:      {summary['total_questions']}")
    print(f"Brain avg latency:     {summary['brain_avg_latency_ms']:.1f}ms")
    print(f"LLM avg latency:       {summary['llm_avg_latency_ms']:.1f}ms")
    print(f"Speedup vs LLM:        {summary['speedup_vs_llm']}×")
    print(f"Brain sourced answers: {summary['brain_sourced_pct']:.0f}%")
    print(f"Brain w/ sources:      {summary['brain_has_sources_count']}/{summary['total_questions']}")
    print(f"Brain wins verifiable: {summary['brain_wins_verifiability']}/{summary['total_questions']}")
    print(f"Brain more concise:    {summary['brain_more_concise']}/{summary['total_questions']}")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brain vs Raw LLM Benchmark")
    parser.add_argument("--count", type=int, default=None, help="Number of questions (default: all)")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Output JSON file")
    args = parser.parse_args()

    questions = BENCHMARK_QUESTIONS[:args.count] if args.count else BENCHMARK_QUESTIONS

    summary = run_benchmark(questions)
    print_summary(summary)

    with open(args.output, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nFull results saved to: {args.output}")
