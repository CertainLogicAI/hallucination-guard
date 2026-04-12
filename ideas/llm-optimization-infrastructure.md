---
summary: "\"LLM Optimization Infrastructure — Ultra-Efficient Token Usage\""
read_when: ["["idea", "llm"]"]
---
# LLM Optimization Infrastructure — Ultra-Efficient Token Usage

**Goal:** Reduce LLM token consumption by 80–90% across all AI features, preparing for next-generation models where every token counts.

---

## Problem Statement

Current AI integrations (future OpenClaw agent skills for FaultTrace) will burn tokens on:
- Verbose system prompts
- Repeated context (same L5X files uploaded multiple times)
- Overly chatty responses
- No model intelligence (always using Opus when Haiku would suffice)
- Duplicate work across users with similar code

We need a **comprehensive optimization layer** before launching any AI features.

---

## Architecture

```
User Request → Skill Router → Cache Layer → Prompt Compressor → Model Router → LLM
       ↑              ↑              ↑                 ↑
   Intent        Skill def     Semantic hash      Cost-aware
   constraints                L5X摘要                routing
```

### Components

1. **Skill Router** — Determines which skill is needed; returns minimal instructions
2. **Semantic Cache** — Stores embeddings of L5X files + LLM responses; hit rate target 80%
3. **Prompt Compressor** — Removes boilerplate, uses instruction tuning, compresses history
4. **Model Router** — Picks cheapest model that can handle the task (Haiku → Sonnet → Opus)
5. **Output Controller** — Enforces max_tokens, stop sequences, JSON mode to avoid verbose rambling
6. **Token Accounting** — Real-time cost tracking per user, with hard limits
7. **Batch Queue** — Groups similar requests to amortize prompt overhead
8. **Provider Abstraction** — Switch between OpenRouter, Anthropic, OpenAI, local models seamlessly

---

## Optimization Techniques

### 1. Input Compression

- **L5X → AST摘要** — Instead of sending full 25KB L5X, send:
  - Tag list (names + types + usage stats): ~500 tokens
  - Issue list from static analyzer: ~200 tokens
  - Rung count + top 3 problem areas: ~100 tokens
  - **Total: ~800 tokens vs 6,250** (92% reduction)

- **Embedding-based deduplication** — If two files are 95% identical, use cached result and a delta diff prompt (100 tokens)

### 2. System Prompt Bloat Elimination

**Current typical system prompt:** 800–1,200 tokens

**Optimized:**
- Move skill instructions to **external reference file** loaded on-demand (not always in context)
- Use **short-hand templates**: "You are a PLC expert. Use these rules: <rules.md>. Output JSON only."
- Pre-pend examples to user query, not system
- Target system prompt: **<200 tokens**

### 3. Few-Shot Reduction

- Replace 3–5 examples with **1 high-quality example** + clear schema
- Use **function calling** / tool-use format (OpenRouter supports) to avoid describing formats in prose
- Store examples in **cache**; retrieve most similar example via embedding similarity (RAG)

### 4. Output Control

- Always use **JSON mode** with schema:
  ```json
  { "suggestions": [{ "type": "fix", "line": 45, "text": "..." }] }
  ```
- Set `max_tokens` per skill:
  - Summarizer: 300
  - Test Generator: 800
  - Compliance: 600
- Use `stop` sequences to cut off rambling (`\n\n`, `---`)

### 5. Model Routing Intelligence

**Decision tree:**
1. Is it simple classification? → **Haiku**
2. Needs reasoning + small context (<2k tokens)? → **Sonnet**
3. Complex cross-file analysis + >5k context? → **Opus**
4. **Fallback:** If Opus budget exceeded, downgrade to Sonnet with explicit warning

Implement a **token budget** per request:
- If estimated input > 4k tokens → force Haiku + compression
- If user is on free tier → cap at Sonnet

### 6. Caching Strategy

**Three-layer cache:**
1. **Exact file hash** → result (TTL 24h)
2. **Semantic similarity** (embedding: L5X AST) → result if >90% match (TTL 7d)
3. **Prompt template + params** → result (TTL 1h)

**Cache hit target:** 80%+ for repeat analyses (industrial code doesn't change often)

### 7. Batching

- Nightly batch: re-analyze all files in customer's account that changed since last run
- Group 5–10 small files into one prompt: "Analyze these 8 programs and list all unused tags"
- Reduces per-file overhead

### 8. Streaming vs. Non-Streaming

- Use **non-streaming** for agents (wait for full response, then cache)
- Streaming only for user-facing chat where they want to see incremental output

---

## Implementation Plan (3–4 weeks)

### Week 1: Core Infrastructure
- Set up Redis with semantic cache (using `ioredis` + embedding model, e.g., `all-MiniLM-L6-v2` via `@xenova/transformers`)
- Implement `CacheLayer` with `get(hash)`, `set(hash, response)`, `similaritySearch(ast)`
- Build `ModelRouter` that selects model based on input tokens + skill complexity
- Create `TokenAccountant` that tracks per-user spend and enforces limits

**Deliverable:** Cache + routing works; token count reduced 30%

### Week 2: Compression & Prompt Engineering
- Build `PromptCompressor`: loads skill instructions from `references/` files, injects only needed sections
- Create `OutputController`: wraps LLM calls with JSON schema + max_tokens
- Optimize all skill system prompts to <200 tokens (using reference files)
- Implement AST摘要 for L5X (extract tags, issues, structure without full file)

**Deliverable:** Token count reduced 60% vs baseline

### Week 3: Integration & Testing
- Wire all layers into OpenClaw agent skill execution
- Add caching to all 3 skills (Diagnose, TestGen, Compliance)
- Implement batch processing scheduler (cron: nightly re-analyze)
- Add real-time monitoring dashboard (tokens used, cache hit rate, cost per analysis)

**Deliverable:** End-to-end optimized pipeline; 80% token reduction target

### Week 4: Polish & Scale
- Add provider abstraction (switch from OpenRouter to Anthropic direct or local models)
- Implement graceful degradation (if cache miss and Opus budget exhausted → Sonnet + warning)
- Write comprehensive docs: how to add new skills without blowing tokens
- Load test with 1000 simulated analyses; fine-tune cache TTLs and model thresholds

**Deliverable:** Production-ready optimization layer; 90% token reduction achieved in testing

---

## Software Stack

| Component | Tech |
|-----------|------|
| Cache | Redis + custom embedding index (or use `redis-vector` if available) |
| Embedding model | `@xenova/transformers` (Node.js ONNX Runtime) — 22MB, CPU-friendly |
| Model routing | Simple rules engine (if-else) or tiny neural net (overkill) |
| Token accounting | Redis sorted sets per user + daily TTL |
| Monitoring | Express route `/admin/metrics` returning JSON + Prometheus exporter |
| Config | YAML files per skill: `model`, `max_tokens`, `cache_ttl`, `compression_level` |

**Why not use a heavy framework:** We're optimizing for build speed and low overhead. Custom code is 500 lines, not 5000.

---

## Cost Savings Projection (Post-Optimization)

### Baseline (no optimization)

| Scale | Analyses/mo | Tokens/analysis | Total tokens | Cost/mo (Opus/Sonnet mix) |
|-------|-------------|-----------------|--------------|---------------------------|
| Moderate | 12k | 8,250 input + 4k output = 12,250 | 147M | $1,389 |

### Optimized (80% token reduction)

| Scale | Input tokens/analysis | Output tokens/analysis | Total tokens | Cost/mo |
|-------|----------------------|-----------------------|--------------|---------|
| Moderate | 1,650 (80% off) | 800 (80% off) | 29.4M | ~$278 |

**Savings: $1,111/mo** at moderate scale.

At aggressive scale (40k analyses/mo): **$3,700/mo saved**.

That's **real money** when models get more expensive (next-gen will cost more, not less).

---

## Risks

| Risk | Mitigation |
|------|------------|
| Compression loses important context | Validate: run optimized vs full-context on 100 samples, measure quality delta <5% |
| Cache poisoning (wrong result served) | Hash + embedding similarity both must match; versioned keys |
| Model router misroutes (Haiku too dumb) | Fallback chain: if Haiku fails (low confidence), auto-retry with Sonnet |
| Over-optimization breaks skills | Keep baseline (no-compression) path as fallback; A/B test |
| Token accounting misses edge cases | Log every LLM call with full token count; daily reconciliation |

---

## Success Metrics

- Token reduction: **≥80%** vs baseline (measured on 100-real-usage sample)
- Cache hit rate: **≥75%**
- Quality retention: **≥95%** of baseline outputs still acceptable (user testing)
- Latency: **≤2s** added overhead from compression+caching

---

## Optional: Local Model Fallback

To further reduce cost, add ability to run **small local models** (e.g., `mistral-7b` via `llama.cpp`) for simple tasks. If open-source models reach Haiku-level quality at 10x lower cost, switch automatically.

**Implementation:** Add `LocalProvider` that runs quantized model in Docker container; router chooses local if task matches constraints.

**Potential savings:** 90%+ on eligible tasks.

---

## Go/No-Go

**Go if:**
- [ ] Baseline token usage measured on real traffic (sample 100 analyses)
- [ ] Compression quality validated (side-by-side comparison)
- [ ] Redis budget approved ($50/mo for cluster if needed)
- [ ] You have 3–4 weeks to build before launching AI features

**No-Go if:**
- We're shipping in 1 week and can't delay
- Token costs projected to be <$100/mo even without optimization (unlikely at scale)

---

**Recommendation:** Build this **before** any AI feature launch. It's the difference between burning $1k/mo and $100/mo at scale. Next-gen models will be more expensive; this prep pays for itself immediately.

---
*Created: 2026-03-27*
*Status: proposed*
*Tags: llm, optimization, tokens, cost-saving*
