#!/usr/bin/env python3
"""
CertainLogic Verifier - Pydantic schemas for facts and validation.
v0.2.0 — typed data models for audit-ready compliance.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class Fact(BaseModel):
    """A single verified fact entry."""

    id: str = Field(..., description="Unique fact identifier")
    type: str = Field(default="string", description="Fact type: string, numeric, bool, enum")
    value: str = Field(..., description="Verified value")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence 0.0–1.0")
    source: str = Field(default="unknown", description="Source URL or reference")
    last_updated: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 timestamp of last verification",
    )
    exact_match_required: bool = Field(default=False, description="Require exact word match for string facts")

    @classmethod
    def from_legacy(cls, key: str, data: dict[str, Any]) -> "Fact":
        """Upgrade a legacy flat dict into a typed Fact."""
        if isinstance(data, str):
            return cls(id=key, value=data)
        return cls(
            id=key,
            type=data.get("type", "string"),
            value=data.get("value", data.get("answer", str(data))),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "unknown"),
            last_updated=data.get("last_updated", datetime.now(timezone.utc).isoformat()),
            tags=data.get("tags", []),
            exact_match_required=data.get("exact_match_required", False),
        )

    def to_legacy(self) -> dict[str, Any]:
        """Downgrade to legacy dict for backward-compatible consumers."""
        legacy: dict[str, Any] = {
            "type": self.type,
            "value": self.value,
        }
        if self.confidence != 1.0:
            legacy["confidence"] = self.confidence
        if self.source != "unknown":
            legacy["source"] = self.source
        if self.last_updated:
            legacy["last_updated"] = self.last_updated
        if self.tags:
            legacy["tags"] = self.tags
        if self.exact_match_required:
            legacy["exact_match_required"] = self.exact_match_required
        return legacy


class FactsDB(BaseModel):
    """Top-level facts database container."""

    version: str = Field(default="1.0", description="Schema version")
    facts: dict[str, Fact] = Field(default_factory=dict, description="Fact ID → Fact mapping")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extra metadata (pack name, tier, etc.)"
    )
    sample_queries: list[dict[str, str]] = Field(
        default_factory=list, description="Optional sample queries"
    )

    @classmethod
    def model_validate_json(cls, data: str | bytes, **kwargs: Any) -> "FactsDB":
        """Parse JSON string into a FactsDB, handling legacy flat formats."""
        import json

        raw = json.loads(data)
        return cls.from_raw(raw)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "FactsDB":
        """Build FactsDB from a raw dict, upgrading legacy formats on the fly."""
        version = raw.get("version", "1.0")
        metadata = raw.get("metadata", {})
        sample_queries = raw.get("sample_queries", [])

        facts_raw = raw.get("facts", raw)  # support both {facts: {...}} and flat dict
        facts: dict[str, Fact] = {}
        for key, val in facts_raw.items():
            if key in ("version", "metadata", "sample_queries"):
                continue
            if isinstance(val, dict) and "id" in val and "value" in val:
                # Already v0.2.0 schema
                facts[key] = Fact.model_validate(val)
            else:
                # Legacy schema upgrade
                facts[key] = Fact.from_legacy(key, val)

        return cls(
            version=version,
            facts=facts,
            metadata=metadata,
            sample_queries=sample_queries,
        )

    def to_legacy_json(self) -> str:
        """Export as JSON in legacy flat format for backward compatibility."""
        import json

        payload: dict[str, Any] = {
            "version": self.version,
            "facts": {k: v.to_legacy() for k, v in self.facts.items()},
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        if self.sample_queries:
            payload["sample_queries"] = self.sample_queries
        return json.dumps(payload, indent=2)
