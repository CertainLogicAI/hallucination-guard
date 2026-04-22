# Usage Examples

## Example 1: Single Fact Verification

**Scenario:** Claude Code is asked a coding question.

### Without CertainLogic MCP

```
User: "What's the default timeout for Python's requests library?"
Claude: "The default timeout is 30 seconds."

# Problem: This is wrong. The default is None (no timeout).
# Claude may hallucinate or rely on stale training data.
```

### With CertainLogic MCP

```
User: "What's the default timeout for Python's requests library?"
Claude: → brain_api_query("What is the default timeout for Python requests library?")
       → { "answer": "None. The requests library has NO default timeout.",
            "confident": true, "method": "facts" }
       → Fact validated

Claude: "The default timeout for Python's requests library is `None`
         — meaning requests will hang indefinitely unless you specify
         a timeout. Always set `timeout=` in production code.
         [Source: CertainLogic validated]"
```

---

## Example 2: Batch Import Validation

**Scenario:** Importing 50 blog posts and want to verify all factual claims.

```python
# In your agent workflow
from certainlogic_mcp.server import batch_query

async def validate_article(article_text: str):
    # Extract claims from article (using your LLM or NLP pipeline)
    claims = [
        "Python 3.12 was released in October 2023",
        "PEP 693 introduced a new parser",
        "Guido van Rossum is still Python BDFL",
    ]

    result = await batch_query(queries=claims, api_key="your-key")

    for item in result.results:
        if item.confident:
            write_to_knowledge_base(item.query, item.answer)
        else:
            flag_for_review(item.query)

    print(f"Validated: {result.confident}/{result.total}")
    print(f"Uncertain: {result.uncertain}/{result.total}")
    print(f"Errors: {result.errors}/{result.total}")
```

**Sample Output:**

```
Validated: 2/3
Uncertain: 0/3
Errors: 0/3

Results:
✅ Python 3.12 was released in October 2023 → True
✅ PEP 693 introduced a new parser → True
⚠️ Guido van Rossum is still Python BDFL → False (he stepped down in 2018)
```

---

## Example 3: Hallucination Detection with Guard

**Scenario:** An AI summarizer claims a paper said something it didn't.

```python
# Source: arxiv.org/abs/2304.15004 — "Attention Is All You Need"
source_text = """
The Transformer, a model architecture eschewing recurrence and instead
relying entirely on an attention mechanism to draw global dependencies
between input and output. The Transformer allows for significantly more
parallelization and can reach a new state of the art in translation quality.
"""

claim = "The Transformer paper introduced the BERT model."

result = await verify_fact_guard(
    claim=claim,
    source_text=source_text,
    strictness=0.9,  # enterprise-grade strictness
)

# Result:
# valid: false
# confidence: 0.97
# reason: "Source text describes the Transformer architecture, not BERT.
#          BERT was introduced in a different paper (Devlin et al., 2018)."
```

---

## Example 4: Health Monitoring

**Scenario:** Build a dashboard showing Brain API availability.

```python
from certainlogic_mcp.server import health_check

async def monitor_brain_api():
    health = await health_check()

    if health.status == "ok":
        print(f"✅ Brain API healthy (latency: {health.latency_ms}ms)")
    elif health.status == "degraded":
        print(f"⚠️  Brain API degraded: {health.components}")
        alert_ops_team()
    else:
        print(f"❌ Brain API down: {health.components}")
        failover_to_llm_mode()
```

---

## Example 5: Retry Resilience

**Scenario:** Network hiccup during a critical fact check.

The MCP server automatically retries on:
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout
- `httpx.ConnectError`
- `httpx.ReadError`

```
Attempt 1: POST → 503 (server overloaded)
→ Wait 1.0s + jitter

Attempt 2: POST → 503 still
→ Wait 2.0s + jitter

Attempt 3: POST → 200 ✅
→ Return result to client
```

No code changes needed — retry is automatic with exponential backoff.

---

## Example 6: Integration with LangChain

```python
from langchain.tools import StructuredTool
from certainlogic_mcp.server import brain_api_query

# Wrap as a LangChain tool
brain_tool = StructuredTool.from_function(
    func=brain_api_query,
    name="brain_api_query",
    description="Query verified factual knowledge base. Use for API specs, language behavior, regulatory facts.",
)

# Use in an agent
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools=[brain_tool, ...],
    llm=your_llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

agent.run("What's the maximum file size for S3 multipart uploads?")
# → brain_api_query → "5TB" (verified fact)
```

---

## Example 7: Integration with CrewAI

```python
from crewai import Agent, Task, Crew
from certainlogic_mcp.server import brain_api_query

# Create a fact-checker agent
fact_checker = Agent(
    role="Fact Checker",
    goal="Verify all claims before publishing",
    backstory="You meticulously check every fact using verified sources.",
    tools=[brain_api_query],
    verbose=True,
)

verify_task = Task(
    description="Verify these claims about Python 3.13",
    agent=fact_checker,
)

crew = Crew(agents=[fact_checker], tasks=[verify_task])
crew.kickoff()
```

---

## Example 8: CI/CD Pipeline Gate

```yaml
# .github/workflows/fact-check.yml
name: Fact Check Documentation

on: [pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install CertainLogic MCP
        run: pip install certainlogic-mcp

      - name: Check Docs for Factual Accuracy
        env:
          BRAIN_API_KEY: ${{ secrets.BRAIN_API_KEY }}
        run: |
          python scripts/extract_claims.py docs/ | \
          python -m certainlogic_mcp.batch_check --strict
```

---

## Workflow Summary

| User Action | MCP Tool | Result |
|---|---|---|
| Ask coding question | `brain_api_query` | Verified answer or honest `uncertain` |
| Import article batch | `batch_query` | Stats: validated/uncertain/rejected |
| Validate summary | `verify_fact_guard` | `valid` / `invalid` / `unclear` |
| Monitor API health | `health_check` | `ok` / `degraded` / `down` |
| Network failure | Auto-retry | Exponential backoff, transparent to user |

---

## Anti-Patterns to Avoid

1. **Don't validate everything** — Personal opinions, subjective judgments, and "best practices" don't need fact-checking. Use it for objective, verifiable claims.

2. **Don't block on uncertain** — If a fact can't be validated, flag it. Don't stop the workflow. The honest `uncertain` response is a feature, not a bug.

3. **Don't trust LLM answers blindly** — `method: "llm"` means the Brain API called an LLM to answer. Prefer `facts` or `cache` over `llm` for critical decisions.

4. **Don't log query text** — The MCP server never logs raw queries (only hashes). Don't override this behavior — query privacy is a core guarantee.
