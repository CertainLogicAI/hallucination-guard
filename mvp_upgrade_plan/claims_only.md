# Claims (Claims 1-26)

## Independent Claims

1. **A deterministic AI response‑generation system** comprising:
   a. a local knowledge base indexed by deterministic retrieval methods (e.g., TF‑IDF, vector embeddings);
   b.a multi‑layer validation module that performs factual consistency checking, uncertainty detection, and speculative language filtering;
   c.a token‑budget enforcement mechanism limiting input tokens to 200 and output tokens to 500;
   d.a hybrid fallback module that routes queries to an external large‑language model only when the validation module determines the local response insufficient;
   e.wherein the system logs each query, validation result, and fallback decision in an immutable, append‑only store.

6. **A method** for operating the deterministic AI system of claim 1, comprising:
   a.receiving a user query;
   b.retrieving candidate responses from the local knowledge base;
   c.validating each candidate via the multi‑layer validation module;
   d.if validation succeeds, returning the deterministic response; else invoking the fallback module and returning the external LLM response.

10. **A computer‑readable medium** containing instructions executable by a processor to perform the method of claim 6.

---

## Dependent Claims

2. **The system of claim 1**, in which the validation module includes a deterministic hash‑based comparison of the generated response against a pre‑computed hash stored in the knowledge base, ensuring repeatable output for identical inputs.

3. **The system of claim 1**, wherein the token‑budget enforcement further comprises a dynamic token allocator that dynamically tightens the token ceiling in real‑time based on current system load, preserving deterministic latency.

4. **The system of claim 1**, wherein the fallback module incorporates a configurable safety threshold that triggers external LLM calls only when the confidence score from the validation module falls below a predetermined value (e.g., 0.7).

5. **The system of claim 1**, wherein the immutable log comprises a SHA‑256 hash of the request and response, timestamps, and a status flag (SUCCESS, FAILED, ERROR) stored in a SQLite database.

7. **The method of claim 6**, further comprising: monitoring and reporting token usage metrics to an operational dashboard for real‑time transparency.

8. **The system of claim 1**, wherein the architecture is designed to operate entirely on‑premise, without transmitting raw user data to external services, thereby satisfying data‑privacy regulations (e.g., GDPR, CCPA).

9. **The system of claim 1**, wherein the knowledge base is continuously updated via a cache‑warming routine that pre‑loads high‑frequency query patterns, reducing the learning curve for new deployments.

11. **The system of claim 1**, wherein the local knowledge base is stored in an encrypted, column‑archetype database and accessed via a lightweight, in‑memory cache that respects the token‑budget constraints of claim 3.

12. **The system of claim 1**, wherein the multi‑layer validation module employs a deterministic rule‑based engine that assigns a numerical confidence score to each candidate answer and requires a threshold of 0.85 for the answer to pass.

13. **The system of claim 1**, wherein the token‑budget enforcement mechanism also limits the cumulative token consumption per client IP within a rolling‑window of 24 hours.

14. **The system of claim 1**, wherein the hybrid fallback module includes a "whitelisting" filter that restricts external LLM calls to pre‑approved model endpoints (e.g., OpenAI GPT‑4, Anthropic Claude‑3) and records each call in the audit log.

15. **The system of claim 1**, wherein the immutable audit log is replicated in real‑time to a tamper‑evident, write‑once immutable storage tier (e.g., blockchain, append‑only log server) for compliance auditing.

16. **The system of claim 1**, wherein the Deterministic Engine is implemented as a stateless, containerized micro‑service that can be scaled horizontally behind a load‑balancing gateway.

17. **The system of claim 1**, wherein the fallback module incorporates a "confidence fallback queue" that segments external LLM requests into priority levels, allowing the system to preferentially service high‑confidence queries while deferring low‑confidence ones.

18. **The system of claim 1**, wherein the validation module's uncertainty detection layer uses a pre‑trained, calibrated language model that scores phrases on a 0‑1 scale for hedging probability and requires the score to be < 0.3 before a response may pass.

19. **The system of claim 1**, wherein the deterministic engine performs a "token–budget inflation guard" that caps output token length by trimming or summarizing content while preserving the top‑k factual entities.

20. **The system of claim 1**, wherein the audit log includes not only the SHA‑256 hash of each query and response but also a cryptographic nonce that allows clients to independently verify that the stored log was not altered after the fact.

21. **The method of claim 6**, wherein the system extracts a "confidence token" from the validation module, uses it to gate the fallback call, and logs the call latency in the audit log.

22. **The method of claim 6**, wherein the system's token‑budget manager employs a token‑bucket algorithm with a refill rate calibrated to the average output per query (≈ 210 tokens per 200 input tokens).

23. **The method of claim 6**, wherein the system's audit log is streamed in real‑time to an external analytics platform (e.g., Grafana agent) that visualizes a live heat map of query frequency per end‑user.

24. **The method of claim 6**, wherein the system's deterministic engine is optionally exposed as a FaaS (e.g., AWS Lambda) endpoint that auto‑scales based on request load but continues to obey the determinism guarantees of claims 1‑4.

25. **The method of claim 6**, wherein the system updates the local knowledge base via an incremental, immutable "commit‑set" that records every fact insertion in the audit log along with a timestamp and version number.

26. **The method of claim 6**, wherein the fallback module's external LLM calls are rate‑limited to a maximum of one request per second per client to preserve deterministic latency bounds.