"""
LangChain integration for Hallucination Guard.

Provides two integration patterns:

1. **HallucinationGuardCallback** — a LangChain callback handler that validates
   every LLM response automatically. Drop it into any chain.

2. **HallucinationGuardChain** — a standalone Runnable that wraps validation
   logic. Compose it into LCEL pipelines.

Install dependencies::

    pip install hallucination-guard langchain-core

Example::

    from langchain_openai import ChatOpenAI
    from hallucination_guard.integrations.langchain import HallucinationGuardCallback

    llm = ChatOpenAI(callbacks=[HallucinationGuardCallback()])
    llm.invoke("What is 2+2?")  # validated automatically
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.runnables import RunnableLambda

    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False


def _require_langchain() -> None:
    if not _HAS_LANGCHAIN:
        raise ImportError(
            "LangChain integration requires langchain-core. "
            "Install with: pip install langchain-core"
        )


class HallucinationGuardCallback:
    """LangChain callback handler that validates LLM outputs.

    Attach to any LangChain LLM or chain to automatically validate responses
    against your facts database. Flagged responses are logged and optionally
    raise an exception.

    Args:
        facts_db_path: Path to facts database JSON file.
        confidence_threshold: Minimum confidence to pass (0.0–1.0).
        raise_on_hallucination: If True, raise ValueError on flagged responses.
        on_flag: Optional callback ``fn(query, response, result)`` for custom handling.

    Example::

        from langchain_openai import ChatOpenAI
        from hallucination_guard.integrations.langchain import HallucinationGuardCallback

        callback = HallucinationGuardCallback(
            facts_db_path="./my_facts.json",
            raise_on_hallucination=True,
        )
        llm = ChatOpenAI(callbacks=[callback])
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        _require_langchain()
        # Dynamically create the real class inheriting from BaseCallbackHandler
        real_cls = type(
            "HallucinationGuardCallback",
            (BaseCallbackHandler,),
            {
                "__init__": cls._real_init,
                "on_llm_end": cls._on_llm_end,
                "on_chain_end": cls._on_chain_end,
                "_validate": cls._validate,
            },
        )
        instance = object.__new__(real_cls)
        instance.__init__(*args, **kwargs)
        return instance

    @staticmethod
    def _real_init(
        self: Any,
        facts_db_path: Optional[str] = None,
        confidence_threshold: float = 0.7,
        raise_on_hallucination: bool = False,
        on_flag: Optional[Any] = None,
    ) -> None:
        from hallucination_guard import HallucinationDetector

        kwargs: dict[str, Any] = {"confidence_threshold": confidence_threshold}
        if facts_db_path:
            kwargs["facts_db_path"] = facts_db_path
        self.detector = HallucinationDetector(**kwargs)
        self.raise_on_hallucination = raise_on_hallucination
        self.on_flag = on_flag
        self._last_query: str = ""

    @staticmethod
    def _validate(self: Any, query: str, response_text: str) -> dict:
        result = self.detector.validate(query, response_text)
        if result["valid"] is not True:
            logger.warning(
                "Hallucination flagged: query=%r confidence=%.2f flags=%s",
                query[:80],
                result["confidence"],
                result["flags"],
            )
            if self.on_flag:
                self.on_flag(query, response_text, result)
            if self.raise_on_hallucination:
                raise ValueError(
                    f"Hallucination detected (confidence={result['confidence']:.2f}): "
                    f"{result['flags']}"
                )
        return result

    @staticmethod
    def _on_llm_end(self: Any, response: Any, **kwargs: Any) -> None:
        """Called after LLM generates a response."""
        if not response or not response.generations:
            return
        for gen_list in response.generations:
            for gen in gen_list:
                text = gen.text if hasattr(gen, "text") else str(gen)
                if text:
                    self._validate(self, self._last_query or "unknown", text)

    @staticmethod
    def _on_chain_end(self: Any, outputs: Any, **kwargs: Any) -> None:
        """Called after a chain completes."""
        pass  # LLM-level validation covers most cases


class HallucinationGuardChain:
    """A LangChain-compatible Runnable for hallucination validation.

    Use in LCEL pipelines to validate LLM outputs before they reach the user.

    Args:
        facts_db_path: Path to facts database JSON file.
        confidence_threshold: Minimum confidence to pass (0.0–1.0).

    Example::

        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser
        from hallucination_guard.integrations.langchain import HallucinationGuardChain

        guard = HallucinationGuardChain(facts_db_path="./facts.json")
        chain = ChatOpenAI() | StrOutputParser() | guard.as_runnable()
        result = chain.invoke("What is 2+2?")
    """

    def __init__(
        self,
        facts_db_path: Optional[str] = None,
        confidence_threshold: float = 0.7,
    ) -> None:
        _require_langchain()
        from hallucination_guard import HallucinationDetector

        kwargs: dict[str, Any] = {"confidence_threshold": confidence_threshold}
        if facts_db_path:
            kwargs["facts_db_path"] = facts_db_path
        self.detector = HallucinationDetector(**kwargs)

    def validate(self, text: str, query: str = "unknown") -> dict:
        """Validate a text response.

        Args:
            text: The AI-generated text to validate.
            query: The original query (for context).

        Returns:
            Validation result dict with ``valid``, ``confidence``, ``flags``.
        """
        return self.detector.validate(query, text)

    def as_runnable(self) -> Any:
        """Return a LangChain Runnable that validates string inputs.

        The Runnable passes through valid responses and raises ValueError
        for flagged hallucinations.
        """

        def _validate_runnable(text: str) -> str:
            result = self.detector.validate("user_query", text)
            if result["valid"] is not True:
                raise ValueError(
                    f"Hallucination detected: {result['flags']} "
                    f"(confidence={result['confidence']:.2f})"
                )
            return text

        return RunnableLambda(_validate_runnable)
