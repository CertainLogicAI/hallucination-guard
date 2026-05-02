# CertainLogic Hallucination Guard

**Company brain primitives: truth layer, audit layer, cost controls.** ⚡

Built for teams that need AI-generated answers to be verifiable, auditable, and cost-predictable.

---

## What This Actually Is

A FastAPI service that gives you three building blocks for a company knowledge system:

| Layer | What It Does | How |
|-------|-------------|-----|
| **Truth** | Catches uncertain or unverified claims before they reach users | Linguistic pattern detection + optional fact database validation |
| **Audit** | Immutable, cryptographically chained log of every validation decision | SHA-256 chained JSONL, append-only |
| **Cost** | Cuts LLM spend by caching verified answers and routing queries efficiently | Semantic cache + model tier routing |

**Not just a regex guard.** The linguistic detector catches hedging words ("I think," "maybe," "probably") that signal low-confidence responses. The fact validator checks claims against a curated database of verified company knowledge. Together they form a decision boundary: responses that pass both checks get served with confidence; responses that fail get flagged for human review.

---

## Architecture

```
Query → [Truth Layer]
            ├── Linguistic Guard → flags hedge words, uncertainty signals
            └── Fact Validator → checks against verified facts database
                    ↓
        [Pass] → Serve to user + log to audit trail
        [Flag] → Human review queue + log to audit trail
                    ↓
        [Cost Layer]
            ├── Cache hit → return verified answer, $0 LLM cost
            └── Cache miss → route to appropriate model tier
                    ↓
        [Audit Layer]
            └── SHA-256 chained JSONL → every decision immutable
```

---

## The Three Layers in Detail

### 1. Truth Layer — "Don't serve what you can't verify"

**Linguistic Guard** detects low-confidence language:
- Hedge words: "I think," "probably," "maybe," "I'm not sure"
- Self-contradiction markers: "on the other hand," "alternatively"
- Vague quantifiers: "some," "many," "often" (when specificity expected)

**Fact Validator** checks against your ground-truth database:
- Exact match: "Speed of light = 299,792,458 m/s" → verified
- Within tolerance: "Price = $49.99 ± 5%" → verified
- No match found: "GPT-5 costs $200/month" → flagged (not in facts DB)

**How they work together:**
- A response like "I think Python was released in 1991" hits the linguistic guard ("I think") AND matches the fact DB ("1991" = correct) → passes with warning logged
- A response like "Python was released in 1994" matches no hedge words BUT contradicts the fact DB → flagged
- A response like "I believe our enterprise plan is $99/month" hits the guard AND has no matching fact → blocked for review

### 2. Audit Layer — "Every decision is on the record"

Every validation produces an append-only log entry:

```json
{
  "timestamp": "2026-05-02T14:22:11Z",
  "query": "What is our enterprise pricing?",
  "response": "$49/month per seat",
  "truth_layer": {
    "linguistic_passed": true,
    "fact_validated": true,
    "fact_matched": "enterprise_pricing_2026"
  },
  "decision": "PASS",
  "previous_hash": "a3f91c44...",
  "entry_hash": "8d2e4b7a..."
}
```

- **Immutable:** Each entry hashes the previous entry's hash. Tamper with one entry, every subsequent hash breaks.
- **Auditable:** External auditor can verify chain integrity in minutes.
- **Searchable:** Filter by decision, date range, fact category, confidence level.

**Why this matters for a company brain:** Without audit trails, you can't debug why your AI gave a wrong answer last Tuesday. With them, you trace the exact validation decision, the facts DB version at that moment, and whether the linguistic guard fired.

### 3. Cost Layer — "Smart caching, smarter routing"

**Semantic Cache:**
- "What is Python?" and "Explain Python programming" hit the same cached answer
- Cache is keyed by sentence-transformer embeddings, not exact strings
- Hit rate varies by workload (typically 20-40% on repetitive business queries)

**Model Tier Routing:**
- Simple factual lookups → cheapest model (or cache bypass)
- Complex reasoning → appropriate model for the task
- No more using GPT-4 to answer "What year was Python released?"

**What this saves:**
- Cache hits cost $0 (no LLM API call)
- Routing cuts average per-query cost by routing to the cheapest adequate model
- Actual savings depend on query mix — repetitive workflows see the most benefit

---

## Quick Start

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export FACTS_DB_PATH=./facts_db.json
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Test the truth layer:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?", "response": "I think it is 5."}'
# → flagged: hedge words detected + fact mismatch
```

**Test the cost layer:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain Python in simple terms"}'
# → cache miss first time, cache hit second time
```

---

## API Endpoints

| `POST /query` | Cost | Process query through cache + routing |
| `POST /validate` | Truth | Run linguistic guard + fact validator on response |
| `GET /facts/search` | Truth | Search facts database directly |
| `GET /health` | — | Service status |
| `GET /metrics` | All | Cache hit rates, validation counts, cost tracking |

---

## Honest Limitations

**This is not a universal truth machine.**

- The linguistic guard catches *signals of uncertainty*, not *falsehoods*. A confident lie ("Python was released in 1984") passes the linguistic detector and only gets caught if the fact DB has the correct date.
- The fact validator is only as good as your facts database. It knows nothing outside what you load.
- Semantic cache saves money only on *repeated* queries. Novel creative tasks see near-zero cache benefit.
- Audit trails verify *what the system decided*, not *whether the decision was correct*. A misconfigured fact DB produces consistently wrong but auditable validations.

**What this means in practice:**
- Use the guard on customer-facing AI where wrong answers cost reputation
- Use the audit layer in regulated environments where you need decision traceability
- Use the cost layer when your workload has repetitive queries (support tickets, documentation lookups)
- Do not use this if you need real-time fact-checking against live web data (use RAG + search APIs instead)

---

## Configuration

### Facts Database

JSON file with verified facts:

```json
{
  "python_release_year": {
    "type": "numeric",
    "value": "1991"
  },
  "enterprise_pricing": {
    "type": "numeric",
    "value": "49.99",
    "unit": "usd",
    "tolerance": 0.01
  }
}
```

Load via `FACTS_DB_PATH` environment variable or pass to `HallucinationDetector(facts_db_path=...)`.

### Audit Log

Append-only JSONL with SHA-256 chaining. Log path configurable via `AUDIT_LOG_PATH` (default: `./audit.log.jsonl`).

Chain integrity verification:
```bash
python3 scripts/verify_chain.py audit.log.jsonl
# → "Chain valid: 1,247 entries, 0 tamper events"
```

---

## License