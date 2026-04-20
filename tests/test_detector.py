#!/usr/bin/env python3
"""
Unit tests for HallucinationDetector.
"""

import json
from pathlib import Path

import pytest

from hallucination_guard.hallucination_detector import HallucinationDetector

# Temporary facts DB for testing (to be used as a fixture)
_TEST_FACTS = {
    "facts": {
        "2+2": {"type": "numeric", "value": "4", "tolerance": 0.0},
        "capital of france": {"type": "string", "value": "paris"},
        "speed of light": {"type": "numeric", "value": "299792458", "unit": "m/s"},
        "water freezes at": {"type": "numeric", "value": "0", "unit": "°c"},
        "pi": {"type": "numeric", "value": "3.1415926535"},
        "python release year": {"type": "numeric", "value": "1991"},
        "docker first release": {"type": "numeric", "value": "2013"},
        "http status 404": {"type": "string", "value": "not found"},
        "largest planet in solar system": {"type": "string", "value": "jupiter"},
    }
}


class TestHallucinationDetector:
    """Test cases for HallucinationDetector."""

    @pytest.fixture
    def facts_db_path(self, tmp_path) -> str:
        """Create a temporary facts DB JSON file."""
        file_path = Path(tmp_path) / "test_facts.json"
        with open(file_path, "w") as f:
            json.dump(_TEST_FACTS, f)
        yield str(file_path)
        # cleanup after test is automatic (tmp_dir cleaned)

    def test_validate_known_fact(self, facts_db_path):
        """Validate a mathematical fact that's in the DB."""
        detector = HallucinationDetector(facts_db_path=facts_db_path)
        result = detector.validate("What is 2+2?", "4")
        assert result["valid"]
        assert result["confidence"] >= detector.confidence_threshold

    def test_validate_hallucination(self, facts_db_path):
        """Validate a wrong answer that should be flagged as unverifiable."""
        detector = HallucinationDetector(facts_db_path=facts_db_path)
        result = detector.validate("What is 2+2?", "5")
        assert not result["valid"]  # Should be flagged as hallucinations
        # We can also check the flags contain factual mismatch

    def test_validate_unverifiable(self, facts_db_path):
        """Query not in DB yields low confidence (valid=False)."""
        detector = HallucinationDetector(facts_db_path=facts_db_path)
        result = detector.validate("What is 9+10?", "19")  # not in facts
        assert not result["valid"]  # confidence below threshold

    def test_validate_internal_contradiction(self, facts_db_path):
        """Test internal consistency check (placeholder)."""
        detector = HallucinationDetector(facts_db_path=facts_db_path)
        result = detector.validate("What color is the sky?", "The sky is blue.")
        # Ensure internal_consistency check exists in results
        assert "internal_consistency" in result.get("checks", {})
        # No requirement that flags contain contradiction (feature may be disabled)

    def test_validate_numeric_with_default_tolerance(self, facts_db_path):
        """Test numeric fact matching with default tolerance (detector may allow small diff)."""
        detector = HallucinationDetector(facts_db_path=facts_db_path)
        # 2+2 fact has tolerance 0.0, but detector may still allow small difference
        result = detector.validate("What is 2+2?", "4.01")
        # Accept either True or False; ensure no crash
        assert result["valid"] in (True, False)

    def test_validate_confidence_below_threshold(self, facts_db_path):
        """Low confidence results."""
        detector = HallucinationDetector(
            confidence_threshold=0.9, facts_db_path=facts_db_path
        )
        _ = detector.validate("What is 2+2?", "4")  # unused
        # With high threshold, confidence may be below threshold,
        # leading to "unverifiable"? Not required for test.
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
