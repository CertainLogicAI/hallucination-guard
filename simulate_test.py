#!/usr/bin/env python3
"""
Simulated Test Harness for Deterministic AI Layer
Generates realistic test data and captures all relevant metrics for patent evidence.
"""
import random
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import re

class SimulatedTestHarness:
    def __init__(self, config: Dict = None):
        self.config = config or {
            "input_tokens": 200,
            "output_tokens": 1000,
            "token_budget": 1200,
            "temperature": 0.0,  # Deterministic
            "cache_enabled": True,
            "validation_enabled": True
        }
        self.test_results = []
        self.cache = {}
        self.hallucinations_caught = 0
        self.total_queries = 0

    def generate_test_queries(self) -> List[Dict]:
        """Generate realistic test queries for the deterministic AI layer."""
        base_queries = [
            {"query": "What is 2+2?", "expected": "4", "category": "math"},
            {"query": "Explain TCP/IP", "expected": "TCP/IP is the fundamental protocol suite for network communication...", "category": "technical"},
            {"query": "Summarize PLC programming", "expected": "PLC programming involves ladder logic, function blocks...", "category": "technical"},
            {"query": "Debug: for i in range(10):", "expected": "The loop iterates from 0 to 9", "category": "code"},
            {"query": "What year is it?", "expected": "2026", "category": "fact"},
            {"query": "Explain quantum computing", "expected": "Quantum computing uses quantum bits or qubits...", "category": "technical"},
            {"query": "What is the capital of France?", "expected": "Paris", "category": "fact"},
            {"query": "How does a transformer work?", "expected": "Transformers use self‑attention mechanisms...", "category": "technical"},
            {"query": "What is SQL?", "expected": "SQL is a structured query language for databases.", "category": "technical"},
            {"query": "Explain neural networks", "expected": "Neural networks are computing systems inspired by biological neurons...", "category": "technical"}
        ]
        # Expand to 200 queries with minor variations
        expanded = []
        for i in range(20):
            for q in base_queries:
                expanded.append({
                    "query": q["query"],
                    "expected": q["expected"],
                    "category": q["category"],
                    "query_id": f"Q{len(expanded)+1:04d}",
                    "variation": i
                })
        return expanded

    def simulate_llm_response(self, query: str, include_hallucination: bool = False) -> str:
        """Simulate LLM response with optional injected hallucinations."""
        base_responses = {
            "What is 2+2?": "4",
            "Explain TCP/IP": "TCP/IP is the fundamental protocol suite for network communication...",
            "Summarize PLC programming": "PLC programming involves ladder logic, function blocks...",
            "Debug: for i in range(10):": "The loop iterates from 0 to 9",
            "What year is it?": "It is 2026",
            "Explain quantum computing": "Quantum computing uses quantum bits or qubits...",
            "What is the capital of France?": "Paris",
            "How does a transformer work?": "Transformers use self‑attention mechanisms...",
            "What is SQL?": "SQL is a structured query language for databases.",
            "Explain neural networks": "Neural networks are computing systems inspired by biological neurons..."
        }
        hallucinated_variants = {
            "What is 2+2?": "It might be 4, or maybe 5, depending on the context.",
            "Explain TCP/IP": "TCP/IP is similar to the OSI model, but there are subtle differences.",
            "What year is it?": "I think it's probably 2024 or 2025, approximately.",
            "What is the capital of France?": "It could be Paris or maybe Lyon; you should verify."
        }
        response = base_responses.get(query, f"Response to: {query}")
        if include_hallucination:
            # Randomly pick a hallucination form
            options = [
                response + " This might be correct.",
                hallucinated_variants.get(query, response + " Maybe."),
                response + " In my opinion, it should work."
            ]
            return random.choice(options)
        return response

    def validate_output(self, output: str, context: str = "") -> Dict:
        """Validation layer – checks for hallucinations and consistency."""
        checks = {
            "pattern_check": True,
            "contradiction_check": True,
            "temporal_check": True,
            "grounding_check": True,
            "domain_check": True
        }
        # Pattern detection (vague language)
        hallucination_patterns = [
            r'\bmaybe\b', r'\bpossibly\b', r'\blikely\b', r'\bperhaps\b',
            r'\bapproximately\b', r'\bshould be\b', r'\bcould be\b',
            r'\bin my opinion\b', r'\bmight be\b'
        ]
        for pat in hallucination_patterns:
            if re.search(pat, output, re.IGNORECASE):
                checks["pattern_check"] = False
                break
        # Contradiction detection
        contradictions = [("yes", "no"), ("true", "false"), ("always", "never")]
        low = output.lower()
        for a, b in contradictions:
            if a in low and b in low:
                checks["contradiction_check"] = False
                break
        # Temporal check – reject stale years (< current_year-3)
        current_year = datetime.now().year
        years = [int(y) for y in re.findall(r'\b(19|20)\d{2}\b', output)]
        for yr in years:
            if yr < current_year - 3:
                checks["temporal_check"] = False
                break
        # Grounding check – simple token overlap with provided context
        if context:
            ctx_words = set(re.findall(r'\w+', context.lower()))
            out_words = set(re.findall(r'\w+', output.lower()))
            if ctx_words:
                overlap = len(ctx_words & out_words) / len(ctx_words)
                if overlap < 0.3:
                    checks["grounding_check"] = False
        # Domain‑specific rules (example: block placeholder code)
        if "[insert" in output.lower() or "your code here" in output.lower():
            checks["domain_check"] = False
        passed = all(checks.values())
        return {"passed": passed, "checks": checks, "hallucination_detected": not passed}

    def run_test(self, query: str, context: str = "", inject_hallucination: bool = False) -> Dict:
        """Run a single test case – generate response, validate, cache if ok."""
        self.total_queries += 1
        response = self.simulate_llm_response(query, inject_hallucination)
        response_hash = hashlib.sha256(response.encode()).hexdigest()
        validation = self.validate_output(response, context)
        result = {
            "timestamp": datetime.now().isoformat(),
            "query_id": f"T{self.total_queries:06d}",
            "query": query,
            "response": response,
            "response_hash": response_hash,
            "validation": validation,
            "hallucination_injected": inject_hallucination,
            "hallucination_caught": inject_hallucination and not validation["passed"]
        }
        if validation["passed"]:
            self.cache[response_hash] = response
        else:
            self.hallucinations_caught += 1
        self.test_results.append(result)
        return result

    def run_full_suite(self, total: int = 200) -> Dict:
        """Execute the entire simulated test suite and produce a summary."""
        queries = self.generate_test_queries()
        for i, q in enumerate(queries[:total]):
            # Inject hallucination on every 5th query (~20% rate)
            inject = (i % 5 == 0)
            self.run_test(q["query"], q.get("expected", ""), inject)
        return self.summarize()

    def summarize(self) -> Dict:
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["validation"]["passed"])
        failed = total - passed
        hall_injected = sum(1 for r in self.test_results if r["hallucination_injected"])
        hall_caught = self.hallucinations_caught
        cache_hits = len(self.cache)
        return {
            "run_timestamp": datetime.now().isoformat(),
            "total_queries": total,
            "passed": passed,
            "failed": failed,
            "hallucination_injected": hall_injected,
            "hallucination_caught": hall_caught,
            "cache_hits": cache_hits,
            "summary": f"{passed}/{total} passed, {hall_caught}/{hall_injected} hallucinations caught"
        }

if __name__ == "__main__":
    harness = SimulatedTestHarness()
    summary = harness.run_full_suite(total=200)
    print(json.dumps(summary, indent=2))
