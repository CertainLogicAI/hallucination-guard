# Non‑Provisional Patent Claims Draft

## Background
This draft expands on the provisional application (saved at `validated_patent_application.md`) and incorporates the recent Anthropic incident, emphasizing the need for deterministic, controllable AI systems.

## Claim Set

1. **A deterministic AI response generation system** comprising:
   - a local knowledge base indexed by deterministic retrieval methods (e.g., TF‑IDF, vector embeddings);
   - a multi‑layer validation module that performs factual consistency checking, uncertainty detection, and speculative language filtering;
   - a token‑budget enforcement mechanism limiting input tokens to 200 and output tokens to 500;
   - a hybrid fallback module that routes queries to an external large language model only when the validation module determines the local response insufficient.
   - wherein the system logs each query, validation result, and fallback decision in an immutable append‑only store.

2. **The system of claim 1**, wherein the validation module includes a deterministic hash‑based comparison of the generated response against a pre‑computed hash stored in the knowledge base, ensuring repeatable output for identical inputs.

3. **The system of claim 1**, wherein the token‑budget enforcement further includes a dynamic token allocator that adjusts the token ceiling based on real‑time load, preserving deterministic latency.

4. **The system of claim 1**, wherein the fallback module incorporates a configurable safety threshold that triggers external LLM calls only when the confidence score from the validation module falls below a predetermined value (e.g., 0.7).

5. **The system of claim 1**, wherein the immutable log comprises a SHA‑256 hash of the request and response, timestamps, and a status flag (SUCCESS, FAILED, ERROR) stored in a SQLite database.

6. **A method** for operating the deterministic AI system of claim 1, comprising:
   - receiving a user query;
   - retrieving candidate responses from the local knowledge base;
   - validating each candidate via the multi‑layer validation module;
   - if validation succeeds, returning the deterministic response; otherwise invoking the fallback module and returning the external LLM response.

7. **The method of claim 6**, further comprising: monitoring and reporting token usage metrics to a dashboard for operational transparency.

8. **The system of claim 1**, wherein the architecture is designed to operate entirely on‑premise, without transmitting raw user data to external services, thereby satisfying data‑privacy regulations (e.g., GDPR, CCPA).

9. **The system of claim 1**, wherein the knowledge base is continuously updated via a cache‑warming routine that pre‑loads high‑frequency query patterns, reducing the learning curve for new deployments.

10. **A computer‑readable medium** containing instructions executable by a processor to perform the method of claim 6.

## Additional Dependent Claims (Optional)
- Claims covering specific implementations of the validation heuristics (e.g., regex patterns for uncertainty detection).
- Claims covering integration with specific external LLM providers (e.g., OpenAI GPT‑4, Anthropic Claude‑3) under a token‑budget contract.
- Claims covering a service‑level agreement (SLA) guaranteeing 99.9% uptime and deterministic response latency under defined load conditions.

---

**Note:** This draft is intended for review with counsel to ensure claim language meets USP‑TO standards and to incorporate any further inventive aspects discovered during ongoing development.

*Prepared on 2026‑04‑08*