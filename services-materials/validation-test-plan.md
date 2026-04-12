# Validation Test Plan — Deterministic AI

This plan demonstrates that a deployed agent:
- **Never hallucinates** (answers are grounded in provided references)
- **Respects token budgets** (output within limits)
- **Performs reliably** (consistent latency, cache hit rate)

---

## Test Environment

- **Agent instance:** Production container (same image, same config)
- **Test harness:** `test_hallucination_control.js` (adapted for client’s reference set)
- **Metrics collection:** Prometheus or JSON log file
- **Test duration:** ~5 minutes for 100–1,000 queries

---

## Test Suite A: Hallucination Prevention

### A1. Reference‑Grounded Queries (Positive Tests)
**Goal:** Verify that supported queries produce responses that can be traced to reference text.

**Procedure:**
1. Select 20 questions that *should* be answerable from the reference corpus (covering different tags).
2. For each query, run the agent and capture:
   - `response_text`
   - `used_references` (keys/ids from cache)
   - `validation_status` (pass/fail)
3. Validate automatically:
   ```javascript
   function passesValidation(response, references) {
     const keyPhrases = extractSignificantPhrases(response, 5);
     const matchedRefs = references.filter(ref => 
       keyPhrases.some(phrase => ref.content.includes(phrase))
     );
     return matchedRefs.length >= 3; // require at least 3 phrase matches
   }
   ```
4. **Pass criteria:** ≥19/20 pass (95% validation rate)

### A2. Unsupported Queries (Negative Tests)
**Goal:** Verify that the agent refuses to answer questions outside its reference corpus.

**Procedure:**
1. Select 10 questions that are *not* supported by the provided references (e.g., questions about topics you deliberately excluded).
2. Run the agent and capture `response_text`.
3. Check that response contains refusal language (configurable):
   - `"I don't have enough information"`
   - `"Please provide the relevant documentation"`
   - `"That topic is not covered"`
4. **Pass criteria:** 10/10 refusals (no hallucinated content)

### A3. Edge Cases (Boundary Tests)
**Goal:** Stress‑test the guardrails.

**Procedure:**
1. Craft queries that are *almost* supported:
   - Questions that mix supported and unsupported elements
   - Questions with ambiguous phrasing
   - Very long queries (>2000 chars)
2. Verify that:
   - Response is not a hallucination
   - Token budget enforced (no overflow)
   - Fallback messages are domain‑appropriate

---

## Test Suite B: Performance & Cost

### B1. Token Efficiency
**Goal:** Demonstrate token reduction vs naive implementation.

**Procedure:**
1. For 50 representative queries, record:
   - `context_tokens` (before LLM call)
   - `input_tokens` (sent to LLM)
   - `output_tokens` (received from LLM)
   - `total_tokens` (sum)
2. Compute baseline: what would a raw ChatGPT‑style call use?  
   (Estimate: full workspace file scan + 2k context + 1k output = ~155k tokens)
3. **Pass criteria:** Average total tokens < 5,000 (3% of baseline) → ~97% reduction

### B2. Latency
**Goal:** Ensure agent meets interactive latency.

**Procedure:**
1. Run 100 queries; measure `total_latency_ms` (from query start to response end).
2. Percentiles: p50, p95, p99.
3. **Pass criteria:** p95 ≤ 2,000ms (2 seconds)

### B3. Cache Effectiveness
**Goal:** Show caching reduces both cost and latency.

**Procedure:**
1. Ensure cache is warm (run all queries once).
2. Repeat the 100‑query suite; record cache hit rate.
3. **Pass criteria:** Cache hit rate ≥ 20% on repeated runs

### B4. Token Budget Enforcement
**Goal:** Guarantee hard output limit.

**Procedure:**
1. Set `MAX_TOKENS=500` for test.
2. Use a query known to produce long output (e.g., "List all possible fault patterns").
3. Verify response tokens ≤ 500 (or truncated cleanly).
4. **Pass criteria:** Truncation always occurs at sentence boundary; no mid‑sentence cuts.

---

## Test Suite C: Reference Integrity

### C1. Summaries Match Original
**Goal:** Summaries accurately represent their source documents.

**Procedure:**
1. Randomly select 10 summaries.
2. For each, compute Jaccard similarity between summary text and the first 500 characters of the original document.
3. **Pass criteria:** Similarity ≥ 0.8 (80% overlap)

### C2. Tag Index Coverage
**Goal:** All documents have at least one relevant tag.

**Procedure:**
1. List all files in `workspace-cache.json`.
2. Check each file's `tags` array is non‑empty.
3. **Pass criteria:** 100% of files have ≥1 tag

---

## Test Execution & Reporting

### Execution
```bash
# Build cache first
node build-cache-clean.js

# Run test suites
node test_hallucination_control.js --queries 100 --report results.json

# Or custom
node validation_test_harness.js --suite A,B,C --output report.html
```

### Report Format
 Deliver **two files** to the client:
1. `EXECUTIVE_SUMMARY.md` — high‑level results (pass/fail, key metrics)
2. `FULL_TECHNICAL_REPORT.json` — raw data for their audit

Example executive summary:
```
✅ Hallucination Prevention: 20/20 positive queries validated; 10/10 unsupported blocked
✅ Performance: avg 1,843ms latency, 3,200 tokens/query (98.7% reduction)
✅ Cache: 37% hit rate on repeated runs
✅ Reference Integrity: 100% files tagged; summary similarity 89%
```

---

## Client Witness Options (Optional)

For high‑trust engagements, allow the client to:
1. Provide their own test questions (add to Suite A)
2. Observe a live query run (screen share on test environment)
3. Review the `FULL_TECHNICAL_REPORT` with their technical team

---

## Sign‑off

After passing all test suites:
- **Client signs:** _"I have reviewed the validation report and confirm the agent meets the agreed specifications."_
- **Project moves to:** Production deployment

---

## Maintenance Testing

Schedule **monthly re‑validation** after reference updates:
- Run subsets of the test suite to catch regressions
- Update `FULL_TECHNICAL_REPORT` quarterly for client audit

---

*This test plan provides objective, repeatable evidence that the agent operates deterministically within its reference corpus. It is a key deliverable in every engagement.*
