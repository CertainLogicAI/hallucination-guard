# CertainLogic Verifier

**Kill AI hallucinations deterministically • 85–98% token savings • Self-hosted & audit-ready**

[![CI](https://github.com/CertainLogicAI/hallucination-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/CertainLogicAI/hallucination-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hallucination-guard?color=blue)](https://pypi.org/project/hallucination-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/CertainLogicAI/hallucination-guard/blob/main/LICENSE)

---

## What Is It?

CertainLogic Verifier is **deterministic AI verification middleware** that:

- **Catches hallucinations** using rule-based fact-checking against your versioned facts database — no extra LLM calls
- **Saves 85–98% on tokens** via semantic caching and similarity lookup
- **Runs entirely self-hosted** — your VPC, your air-gapped network, your control
- **Produces audit trails** with SHA-256 hash-chained JSONL logs for HIPAA/GDPR/SOC2 compliance

## Why Not LLM-as-a-Judge?

Most guardrail tools use another LLM to check the first LLM. That's:

- **Expensive** — $0.05–$0.50 per validation call
- **Non-deterministic** — different answer each time
- **Unauditable** — you can't prove what the judge saw or decided
- **Still hallucination-prone** — LLM judges hallucinate too (5–15% rate)

CertainLogic Verifier uses **deterministic rules + your facts**. Same query → same answer, every time, with cryptographic proof.

## Quick Start

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then validate a response:

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is GPT-5 pricing?", "response": "$200/month"}'
```

→ Hallucination caught and flagged. [Full quickstart guide →](getting-started/quickstart.md)

## Key Numbers

| Metric | Value |
|--------|-------|
| Hallucination detection accuracy | 83.9% |
| Pricing query recall | 100% |
| Token reduction | 85–98% |
| Inference latency | <100ms |
| Extra LLM cost | **$0.00** |

## Next Steps

- [Installation & setup](getting-started/installation.md)
- [API reference](api/endpoints.md)
- [LangChain integration](integrations/langchain.md)
- [Deploy with Docker](deployment/docker.md)
- [Compliance guide](compliance.md)
