# Provisional Patent Application
## Title
**Deterministic AI Engine for Local Knowledge Retrieval**

## Abstract
A deterministic AI engine that generates responses from a locally‑stored knowledge base.
The engine deterministically retrieves an answer, validates it by checking factual consistency, uncertainty, and speculative language, and (if necessary) falls back to an external LLM while strictly limiting both input and output token counts.
The entire process is logged in an immutable, append-only store for auditability.

---

## 1. Background of the Invention
Artificial‑intelligence systems that rely on probabilistic transformers frequently emit *hallucinations*, produce inconsistent results for the same prompt, and are difficult to audit.
Existing deterministic remedies either require the user to supply a knowledge base or rely on external services that sacrifice privacy and introduce latency.

## 2. Summary of the Invention
The present invention provides a deterministic AI response‑generation system that:

1. **Local Retrieval** – Uses a pre‑indexed knowledge base (TF‑IDF / vector embeddings) to answer queries deterministically.
2. **Multi‑Layer Validation** – Applies (i) factual consistency checks, (ii) uncertainty detection, and (iii) speculative language filtering.
3. **Token‑Budget Enforcement** – Locks both input (≤ 200 tokens) and output (≤ 500 tokens) to guarantee predictable cost.
4. **Hybrid Fallback** – Sends a request to an external LLM *only* when the local validation module reports an insufficient confidence score, with a configurable threshold (default 0.7).
5. **Auditability** – Logs every request, the validation outcome, and any fallback decision in an append-only SQLite database, including SHA-256 hashes for tamper‑evidence.

## 3. Detailed Description

**Subsystems**
- **Local Knowledge Base (LKB)** – A curated collection of verified assertions and deterministic responses, stored as a compressed index.
- **Deterministic Engine (DE)** – Routes all incoming queries to the LKB, constructing an answer if an exact or high‑confidence match exists.
- **Validation Module (VM)** – Evaluates the DE’s output against three layers:
  * a. Factual consistency (citation matching),
  * b. Uncertainty detection (regex on hedging words),
  * c. Speculative filtering (prohibits expressions such as “might” or “perhaps”).
- **Token‑Budget Manager (TBM)** – Monitors byte‑count for incoming and outgoing tokens, throttling or rejecting requests that exceed limits.
- **Fallback Orchestrator (FO)** – Invokes the external LLM only when the VM’s confidence score falls below the configured threshold.
- **Audit Log (AL)** – Stores each query, its hash, the resulting output, status (SUCCESS/FAILED/ERROR), and timestamps in an append-only table.

**Example Workflow**

1. Client sends *query Q*.
2. **TBM** verifies Q ≤ 200 tokens.
3. **DE** searches LKB → returns answer A or fails to find a match.
4. **VM** validates A:
   * If `VM` passes, **AL** records **SUCCESS** and returns A.
   * If `VM` fails, **FO** triggers an external call (respecting the output token cap).
5. **AL** logs the entire transaction, including hash A, status, and any fallback “call‑metrics”.

## 4. Claims

> *All claims below **refer** to the singular “system”. They may be read in isolation or in combination. The numbering sequence follows the print order in the text.*

1. **A deterministic AI response‑generation system** comprising:
   a. a local knowledge base indexed by deterministic retrieval methods (e.g., TF‑IDF, vector embeddings);
   b. a multi‑layer validation module that performs factual consistency checking, uncertainty detection, and speculative language filtering;
   c. a token‑budget enforcement mechanism limiting input tokens to 200 and output tokens to 500;
   d. a hybrid fallback module that routes queries to an external large‑language model only when the validation module determines the local response insufficient;
   e. wherein the system logs each query, validation result, and fallback decision in an immutable, append‑only store.

2. **The system of claim 1**, in which the validation module includes a deterministic hash‑based comparison of the generated response against a pre‑computed hash stored in the knowledge base, ensuring repeatable output for identical inputs.

3. **The system of claim 1**, wherein the token‑budget enforcement further comprises a dynamic token allocator that dynamically tightens the token ceiling in real‑time based on current system load, preserving deterministic latency.

4. **The system of claim 1**, wherein the fallback module incorporates a configurable safety threshold that triggers external LLM calls only when the confidence score from the validation module falls below a predetermined value (e.g., 0.7).

5. **The system of claim 1**, wherein the immutable log comprises a SHA-256 hash of the request and response, timestamps, and a status flag (SUCCESS, FAILED, ERROR) stored in a SQLite database.

6. **A method** for operating the deterministic AI system of claim 1, comprising:
   a. receiving a user query;
   b. retrieving candidate responses from the local knowledge base;
   c. validating each candidate via the multi‑layer validation module;
   d. if validation succeeds, returning the deterministic response; else invoking the fallback module and returning the external LLM response.

7. **The method of claim 6**, further comprising: monitoring and reporting token usage metrics to an operational dashboard for real‑time transparency.

8. **The system of claim 1**, wherein the architecture is designed to operate entirely on‑premise, without transmitting raw user data to external services, thereby satisfying data‑privacy regulations (e.g., GDPR, CCPA).

9. **The system of claim 1**, wherein the knowledge base is continuously updated via a cache‑warming routine that pre‑loads high‑frequency query patterns, reducing the learning curve for new deployments.

10. **A computer‑readable medium** containing instructions executable by a processor to perform the method of claim 6.

## 5. Drawings

*Figure 1 – Block diagram of the deterministic AI engine, showing the Local Knowledge Base, Deterministic Engine, Validation Module, Token‑Budget Manager, Fallback Orchestrator, and Audit Log.*
*Figure 2 – Flowchart of the query‑processing pipeline.*
*Figure 3 – Schema of the immutable audit‑log table.*

*(All figures are included in the `drawings/` sub‑folder of the application bundle.)*

## 6. Filing Information

- **Application Number:** <to be assigned by USPTO>.
- **Filing Date:** 2026-04-08 (15:00 UTC).
- **Fee:** $130 (non‑refundable provisional).
- **Certification**: Not required for provisional.

--- 
