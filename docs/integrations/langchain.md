# LangChain Integration

CertainLogic Verifier provides two built-in LangChain integration patterns.

## Installation

```bash
pip install "hallucination-guard[langchain]"
```

## Pattern 1: Callback Handler (Drop-in)

Validates every LLM response automatically:

```python
from langchain_openai import ChatOpenAI
from hallucination_guard.integrations.langchain import HallucinationGuardCallback

callback = HallucinationGuardCallback(
    facts_db_path="./company_facts.json",
    raise_on_hallucination=True,  # block hallucinated responses
)

llm = ChatOpenAI(callbacks=[callback])
result = llm.invoke("What is our enterprise pricing?")
# Automatically validated against your facts DB
```

When `raise_on_hallucination=True`, a `HallucinationDetectedError` is raised if the response contradicts your facts.

## Pattern 2: LCEL Runnable (Pipeline)

Compose into LangChain Expression Language pipelines:

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from hallucination_guard.integrations.langchain import HallucinationGuardChain

guard = HallucinationGuardChain(facts_db_path="./facts.json")

chain = ChatOpenAI() | StrOutputParser() | guard.as_runnable()
result = chain.invoke("What is 2+2?")
```

The guard runnable returns the original response if valid, or raises/modifies if a hallucination is detected.

## Full Example

See [`examples/langchain_integration.py`](https://github.com/CertainLogicAI/hallucination-guard/blob/main/examples/langchain_integration.py) for a complete working demo.
