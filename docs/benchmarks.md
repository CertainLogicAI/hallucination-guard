# Benchmarks

Results from our 200-case benchmark suite (April 2026).

> **Conflict of interest:** This suite was designed and run by the tool's own developers. The 200 test cases, benchmark script (`benchmarks/benchmark_suite.py`), and raw results (`benchmarks/results.json`) are published in this repo so anyone can re-run and verify. Treat these as vendor-reported numbers until independently replicated.

## Summary

| Metric | Score |
|--------|-------|
| **Overall accuracy** | 86.5% |
| **F1 score** | 83.6% |
| **Latency** | 0.85ms per case |
| **Pricing query recall** | 100% |
| **Definitional accuracy** | 100% |
| **Speculative query accuracy** | 100% |

## Category Breakdown

| Category | Accuracy | Notes |
|----------|----------|-------|
| Pricing queries | 100% | Every fabricated price caught |
| Definitional | 100% | "What is X?" correctly handled |
| Speculative | 100% | Theoretical/hypothetical queries pass through |
| Known facts (correct) | 69% | Some phrasing mismatches reduce score |
| Known facts (wrong) | 88% | Contradictions reliably caught |
| Unknown facts | 78% | Unverifiable claims flagged |
| Edge cases | 72% | Ambiguous queries, partial matches |
| Numeric with units | 85% | Unit-aware matching |

## Comparison: Cost Per Validation

| Approach | Cost per 1000 validations |
|----------|--------------------------|
| CertainLogic Verifier | **$0.00** |
| GPT-4o as judge | $5.00–$15.00 |
| Claude as judge | $3.00–$10.00 |
| Guardrails AI (SaaS) | $2.00–$8.00 |

## Methodology

- 200 test cases across 8 categories
- Each case includes query, response, expected validity, and ground-truth reasoning
- Benchmark script: `benchmarks/benchmark_suite.py`
- Results: `benchmarks/results.json`
- Full report: `benchmarks/REPORT.md`

## Running Benchmarks

```bash
cd benchmarks
python benchmark_suite.py
# Results written to results.json
```
