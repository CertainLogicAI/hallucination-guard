"""Integrations with popular LLM frameworks."""

from .langchain import HallucinationGuardCallback, HallucinationGuardChain

__all__ = ["HallucinationGuardChain", "HallucinationGuardCallback"]
