#!/usr/bin/env python3
"""
Enhanced Hallucination Detector – Upgraded implementation
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Default facts_db.json path (same directory as this file)
_DEFAULT_FACTS_DB_PATH = str(Path(__file__).parent / "facts_db.json")

CONFIDENCE_THRESHOLD = 0.7


class HallucinationDetector:
    """
    Detects hallucinations in AI responses.

    validate(query, response) -> dict  (backward compatible)
    """

    # Hardcoded fallback facts (used if facts_db.json is missing)
    _HARDCODED_FACTS = {
        "2+2": {"type": "numeric", "value": "4", "tolerance": 0.0},
        "capital of france": {"type": "string", "value": "paris"},
        "speed of light": {"type": "numeric", "value": "299792458", "unit": "m/s"},
        "water freezes at": {"type": "numeric", "value": "0", "unit": "°c"},
        "pi": {"type": "numeric", "value": "3.1415926535"},
    }

    # Signals that a query is asking for a factual/specific answer
    _FACTUAL_QUERY_PATTERNS = [
        r"\bwhat is\b",
        r"\bhow many\b",
        r"\bhow much\b",
        r"\bhow much does\b",
        r"\bhow much is\b",
        r"\bwhen did\b",
        r"\bwho is\b",
        r"\bwhat year\b",
        r"\bwhat's the\b",
        r"\bwhat are\b",
        r"\bdefine\b",
        r"\bwhat was\b",
        r"\bwhat is the price of\b",
        r"\bwhat's the cost of\b",
        r"\bwhat is the cost of\b",
    ]

    # Uncertainty language to flag (only in factual responses)
    _UNCERTAINTY_PATTERNS = [
        r"\bi'm not sure\b",
        r"\bi think\b",
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bcould be\b",
        r"\bmight be\b",
        r"\bpossibly\b",
        r"\bprobably\b",
        r"\bunsure\b",
        r"\bi doubt\b",
        r"\bnot certain\b",
    ]

    # Qualifiers that make a query speculative/theoretical, not factual
    _SAFE_QUALIFIERS = [
        r"in the quantum realm",
        r"in theory",
        r"theoretically",
        r"hypothetically",
        r"in principle",
        r"in a perfect world",
        r"in the abstract",
        r"in the context of",
        r"under the assumption",
        r"assuming",
        r"if",
        r"suppose",
        r"let's say",
        r"for example",
        r"e\.g\.",
        r"i\.e\.",
        r"say",
        r"perhaps",
        r"maybe",
    ]

    def __init__(
        self,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        facts_db_path: str = _DEFAULT_FACTS_DB_PATH,
    ):
        self.confidence_threshold = confidence_threshold
        self.facts_db: dict = dict(self._HARDCODED_FACTS)
        # Try loading from JSON on init
        try:
            self.load_facts(facts_db_path)
        except Exception:
            pass  # Fallback to hardcoded

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_facts(self, facts_db_path: str) -> int:
        """Load/reload facts from JSON file. Returns count loaded."""
        with open(facts_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        facts = data.get("facts", data)  # support both {facts: {...}} and flat dict
        count = 0
        for key, val in facts.items():
            if isinstance(val, dict) and "value" in val:
                self.facts_db[key.lower()] = val
                count += 1
        return count

    def set_threshold(self, threshold: float):
        """Set confidence threshold for valid/invalid decision."""
        self.confidence_threshold = threshold

    def validate(self, query: str, response: str) -> dict:
        """Validate a (query, response) pair. Returns enriched result dict."""
        confidence = 1.0
        flags: list[str] = []

        # ---- 1. Factual consistency ----
        fc_result = self._check_factual_consistency(query, response)
        confidence += fc_result["delta"]
        if fc_result["delta"] < 0:
            flags.append(f"Factual mismatch: {fc_result['message']}")

        # ---- 2. Uncertainty detection ----
        unc_result = self._check_uncertainty(query, response)
        confidence += unc_result["delta"]
        for issue in unc_result["issues"]:
            flags.append(f"Uncertainty language in factual response: '{issue}'")

        # ---- 3. Internal consistency ----
        ic_result = self._check_internal_consistency(response)
        confidence += ic_result["delta"]
        for issue in ic_result["issues"]:
            flags.append(f"Internal contradiction: {issue}")

        # ---- 4. Specificity ----
        spec_result = self._check_specificity(query, response, fc_result["matched_key"])
        confidence += spec_result["delta"]
        if spec_result["delta"] < 0:
            flags.append("Response too vague for a factual query")

        # Clamp
        confidence = round(max(0.0, min(1.0, confidence)), 4)

        # ---- 5. Flagged tier: specific claim that can't be verified ----
        flagged = False
        if self._is_specific_unverifiable_query(query):
            # Flag if: no fact matched at all, OR fact matched but it's a broad entity match
            # (i.e. the fact value doesn't contain the specific attribute being asked about)
            should_flag = False
            if fc_result["matched_key"] is None:
                should_flag = True
            else:
                # Fact matched — check if the specific attribute is actually in the fact value
                matched_key = fc_result["matched_key"]
                fact_value = self.facts_db.get(matched_key, {}).get("value", "").lower()
                # If the fact value is short/generic (entity name only), it can't verify specific claims
                specific_attr_patterns = [
                    r"\b(funding|series\s+[abc]|raised|valuation|investor)",
                    r"\b(cto|ceo|coo|founder|co-founder)",
                    r"\b(revenue|arr|mrr)",
                    r"\b(employee|headcount|staff)",
                    r"\b(price|cost|pricing|\$\d)",
                    r"\b(version|v\d|release)",
                    r"\b(sku|product code|filing|patent)",
                    r"\b(stripe|merchant id)",
                    r"\b(how\s+long|founded|established)",
                ]
                query_lower = query.lower()
                for pat in specific_attr_patterns:
                    if re.search(pat, query_lower, re.IGNORECASE):
                        # The query asks for a specific attribute — is it in the fact value?
                        attr_words = set(
                            re.findall(
                                r"\w+", re.sub(r"[\\^$.*+?()\[\]{}|]", "", pat).lower()
                            )
                        ) - {"b", "s"}
                        if not any(w in fact_value for w in attr_words if len(w) > 3):
                            should_flag = True
                            break
            if should_flag:
                confidence = min(confidence, 0.65)
                flagged = True
                flags.append(
                    "Specific claim with no verifiable fact — flagged for human review"
                )

        # Severity
        severity = self._severity(confidence)

        return {
            "query": query[:100],
            "response_length": len(response),
            "valid": (
                "flagged" if flagged else (confidence >= self.confidence_threshold)
            ),
            "flagged": flagged,
            "confidence": confidence,
            "severity": severity,
            "checks": {
                "factual_consistency": {
                    "passed": fc_result["passed"],
                    "message": fc_result["message"],
                    "score": fc_result["score"],
                },
                "uncertainty": {
                    "passed": unc_result["passed"],
                    "issues": unc_result["issues"],
                    "score": unc_result["score"],
                },
                "internal_consistency": {
                    "passed": ic_result["passed"],
                    "issues": ic_result["issues"],
                    "score": ic_result["score"],
                },
                "specificity": {
                    "passed": spec_result["passed"],
                    "message": spec_result["message"],
                    "score": spec_result["score"],
                },
            },
            "flags": flags,
        }

    def validate_batch(self, pairs: list) -> list:
        """Validate multiple (query, response) pairs. Returns list of results."""
        return [self.validate(q, r) for q, r in pairs]

    # ------------------------------------------------------------------
    # Internal checks
    # ------------------------------------------------------------------

    def _is_factual_query(self, query: str) -> bool:
        q = query.lower()
        # Skip if query contains safe qualifiers (speculative/theoretical)
        for qual in self._SAFE_QUALIFIERS:
            if re.search(qual, q, re.IGNORECASE):
                return False
        return any(re.search(p, q, re.IGNORECASE) for p in self._FACTUAL_QUERY_PATTERNS)

    def _match_facts(self, query: str) -> list[str]:
        """Return fact keys with sufficient word overlap with query (>= 50% of key words must match)."""
        stop_words = {
            "what",
            "is",
            "the",
            "of",
            "a",
            "an",
            "are",
            "how",
            "many",
            "when",
            "did",
            "who",
            "was",
        }
        query_words = set(re.findall(r"\w+", query.lower())) - stop_words
        matched = []
        for key in self.facts_db:
            key_words = set(re.findall(r"\w+", key.lower())) - stop_words
            if not key_words:
                continue
            overlap = key_words & query_words
            ratio = len(overlap) / len(key_words)
            if ratio > 0.5:  # strict majority of key words must be present
                matched.append(key)
        return matched

    def _check_factual_consistency(self, query: str, response: str) -> dict:
        matched_keys = self._match_facts(query)
        if not matched_keys:
            if self._is_factual_query(query):
                return {
                    "passed": False,
                    "message": "No matching fact for factual query — unverifiable",
                    "score": 0.5,
                    "delta": -0.5,
                    "matched_key": None,
                }
            else:
                return {
                    "passed": True,
                    "message": "No matching fact — unknown query",
                    "score": 1.0,
                    "delta": 0.0,
                    "matched_key": None,
                }

        response_lower = response.lower()
        mismatches = []
        first_key = matched_keys[0]

        for key in matched_keys:
            fact = self.facts_db[key]
            fact_type = fact.get("type", "string")
            expected = fact["value"].lower().replace(",", "")

            if fact_type == "numeric":
                numbers = re.findall(
                    r"-?\d+(?:\\.\d+)?(?:e[+-]?\d+)?", response_lower.replace(",", "")
                )
                match = False
                for num_str in numbers:
                    try:
                        resp_num = float(num_str)
                        exp_num = float(expected)
                        denom = abs(exp_num) if exp_num != 0 else 1e-6
                        if abs(resp_num - exp_num) / denom < 0.01:
                            # Numeric match passed; now check unit if present
                            unit = fact.get("unit")
                            if unit:
                                unit_lower = unit.lower()
                                # Look for unit in response (allow plural variations)
                                if unit_lower not in response_lower:
                                    # Unit mismatch, continue searching other numbers
                                    continue
                            match = True
                            break
                    except (ValueError, ZeroDivisionError):
                        pass
                if not match and numbers:
                    unit = fact.get("unit")
                    mismatches.append(
                        f"'{key}' expected ~{expected}" + (f" {unit}" if unit else "")
                    )
                expected_words = set(re.findall(r"\w+", expected))
                if len(expected_words) > 5:
                    # Long text fact — skip substring check, too noisy
                    continue
                if expected not in response_lower:
                    mismatches.append(f"'{key}' expected '{expected}'")

        if mismatches:
            return {
                "passed": False,
                "message": "; ".join(mismatches),
                "score": 0.5,
                "delta": -0.5,
                "matched_key": first_key,
            }

        # Qualifier check: detect unverifiable context injected into the query.
        # If the query adds qualifiers (industry, location, time, demographic, etc.)
        # that are not present in any matched fact value, flag as unverifiable.
        qualifier_patterns = [
            r"\bin\s+the\s+([\w\s]+?)\s+(?:industry|sector|market|field|region|country|area|space)",
            r"\bfor\s+(?:the\s+)?([\w\s]+?)\s+(?:industry|sector|market|customers|clients|users)",
            r"\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # named locations
            r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # named places
            r"\bsince\s+(\d{4}|last\s+\w+|this\s+\w+)",  # time qualifiers
            r"\bafter\s+(\d{4}|last\s+\w+)",
            r"\bunder\s+(\w+\s+)?(?:ceo|cto|management|leadership)",
        ]
        query_lower = query.lower()
        # Build a combined string of all matched fact values for reference
        all_fact_values = " ".join(
            self.facts_db[k]["value"].lower()
            for k in matched_keys
            if k in self.facts_db
        )
        unverifiable_qualifiers = []
        for pattern in qualifier_patterns:
            for m in re.finditer(pattern, query_lower, re.IGNORECASE):
                qualifier = m.group(0).strip()
                # Skip if qualifier matches safe qualifiers (speculative/theoretical)
                safe = False
                for safe_pat in self._SAFE_QUALIFIERS:
                    if re.search(safe_pat, qualifier, re.IGNORECASE):
                        safe = True
                        break
                if safe:
                    continue
                # If the qualifier text isn't mentioned in any fact value, it's unverifiable
                qualifier_words = set(re.findall(r"\w+", qualifier.lower())) - {
                    "in",
                    "the",
                    "for",
                    "from",
                    "at",
                    "of",
                }
                if qualifier_words and not any(
                    w in all_fact_values for w in qualifier_words
                ):
                    unverifiable_qualifiers.append(qualifier)

        if unverifiable_qualifiers:
            return {
                "passed": False,
                "message": f"Query contains unverifiable qualifiers not in facts: {', '.join(unverifiable_qualifiers[:3])}",
                "score": 0.4,
                "delta": -0.6,
                "matched_key": first_key,
            }

        return {
            "passed": True,
            "message": f"Fact(s) verified: {', '.join(matched_keys[:3])}",
            "score": 1.0,
            "delta": 0.0,
            "matched_key": first_key,
        }

    def _check_uncertainty(self, query: str, response: str) -> dict:
        """Only penalise uncertainty language when query is factual."""
        if not self._is_factual_query(query):
            return {"passed": True, "issues": [], "score": 1.0, "delta": 0.0}

        response_lower = response.lower()
        found = []
        for p in self._UNCERTAINTY_PATTERNS:
            for m in re.finditer(p, response_lower, re.IGNORECASE):
                found.append(m.group(0))

        if not found:
            return {"passed": True, "issues": [], "score": 1.0, "delta": 0.0}

        penalty = min(0.5, len(found) * 0.15)
        score = round(1.0 - penalty, 4)
        return {
            "passed": False,
            "issues": found,
            "score": score,
            "delta": -penalty,
        }

    def _check_internal_consistency(self, response: str) -> dict:
        """Look for direct contradictions within the response."""
        sentences = re.split(r"[.!?]\s+", response.lower())
        issues = []

        # Simple heuristic: look for "X is Y" then "X is not Y" (or vice versa)
        assertion_re = re.compile(r"(\w[\w\s]{1,20})\s+is\s+([\w\s]{1,20})")
        negation_re = re.compile(r"(\w[\w\s]{1,20})\s+is\s+not\s+([\w\s]{1,20})")

        assertions: dict[str, str] = {}
        for sent in sentences:
            for m in assertion_re.finditer(sent):
                subj = m.group(1).strip()
                pred = m.group(2).strip()
                assertions[subj] = pred

        for sent in sentences:
            for m in negation_re.finditer(sent):
                subj = m.group(1).strip()
                pred = m.group(2).strip()
                # Check exact match or partial overlap with assertion predicate
                if subj in assertions:
                    asserted_pred = assertions[subj]
                    pred_words = set(re.findall(r"\w+", pred.lower()))
                    asserted_words = set(re.findall(r"\w+", asserted_pred.lower()))
                    if asserted_words & pred_words:  # any word overlap = contradiction
                        issues.append(
                            f"'{subj} is {asserted_pred}' contradicted by '{subj} is not {pred}'"
                        )

        # Also check "always...never" pattern
        if re.search(r"\balways\b", response, re.IGNORECASE) and re.search(
            r"\bnever\b", response, re.IGNORECASE
        ):
            issues.append("Response contains both 'always' and 'never'")

        if issues:
            return {"passed": False, "issues": issues, "score": 0.65, "delta": -0.35}
        return {"passed": True, "issues": [], "score": 1.0, "delta": 0.0}

    _CODE_QUERY_PATTERNS = [
        r"\bhow\s+(do|can|should|would)\s+i\b",
        r"\bwrite\s+a\b",
        r"\bimplement\b",
        r"\b(script|function|method|class|code)\b",
        r"\b(example|snippet|sample)\b",
        r"\busing\s+\w+\s+(library|module|package|api)\b",
    ]

    def _is_code_query(self, query: str, response: str) -> bool:
        """Return True if query is procedural/code-oriented (specificity check should not apply)."""
        q = query.lower()
        if any(re.search(p, q, re.IGNORECASE) for p in self._CODE_QUERY_PATTERNS):
            return True
        # Also detect by presence of code blocks in response
        if "```" in response or "    " in response:
            return True
        return False

    def _check_specificity(self, query: str, response: str, matched_key) -> dict:
        """For factual queries with a known fact, check response isn't all vague qualifiers."""
        if not matched_key:
            return {
                "passed": True,
                "message": "Not a known factual query",
                "score": 1.0,
                "delta": 0.0,
            }

        # Skip specificity check for procedural/code queries — they don't require numbers/dates/names
        if self._is_code_query(query, response):
            return {
                "passed": True,
                "message": "Code/procedural query — specificity check skipped",
                "score": 1.0,
                "delta": 0.0,
            }

        # Look for numbers, dates, proper nouns (capitalised words), or known keywords
        has_specific = bool(
            re.search(r"\b\d+\b", response)
            or re.search(r"\b[A-Z][a-z]+\b", response)
            or re.search(r"\b\d{4}\b", response)  # year
        )

        if has_specific:
            return {
                "passed": True,
                "message": "Response contains specific claims",
                "score": 1.0,
                "delta": 0.0,
            }

        return {
            "passed": False,
            "message": "Response lacks specific numbers/dates/names for a factual query",
            "score": 0.9,
            "delta": -0.1,
        }

    _SPECIFIC_CLAIM_PATTERNS = [
        r"\b(price|cost|pricing|fee|rate|charge|dollar|usd|\$)\b",
        r"\bhow much\b",
        r"\bhow much does\b",
        r"\b(version|v\d|release|build)\b",
        r"\b(employees?|staff|headcount|team\s*size|hire)\b",
        r"\b(funding|series\s+[abc]|raised|valuation|investor)\b",
        r"\b(revenue|arr|mrr|sales figure)\b",
        r"\b(cto|ceo|coo|founder|co-founder)\b",
        r"\b(sku|product code|model number|part number)\b",
        r"\b(filing|patent number|uspto|application number)\b",
        r"\b(exchange rate|credit|token price)\b",
        r"\b(stripe|merchant id|account id)\b",
        r"\b(how\s+long|since\s+when|founding date|established)\b",
        r"\d+\s*%",  # specific percentages
    ]

    # Qualifiers that make a query speculative/theoretical, not factual
    _SAFE_QUALIFIERS = [
        r"in the quantum realm",
        r"in theory",
        r"theoretically",
        r"hypothetically",
        r"in principle",
        r"in a perfect world",
        r"in the abstract",
        r"in the context of",
        r"under the assumption",
        r"assuming",
        r"if",
        r"suppose",
        r"let's say",
        r"for example",
        r"e\.g\.",
        r"i\.e\.",
        r"say",
        r"perhaps",
        r"maybe",
    ]

    def _is_specific_unverifiable_query(self, query: str) -> bool:
        """Return True if query contains specific claims that should be fact-checked."""
        q = query.lower()
        # Skip if query contains safe qualifiers (speculative/theoretical)
        for qual in self._SAFE_QUALIFIERS:
            if re.search(qual, q, re.IGNORECASE):
                return False
        return any(
            re.search(p, q, re.IGNORECASE) for p in self._SPECIFIC_CLAIM_PATTERNS
        )

    @staticmethod
    def _severity(confidence: float) -> str:
        if confidence >= 0.9:
            return "none"
        elif confidence >= 0.7:
            return "low"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "high"

    # ------------------------------------------------------------------
    # Legacy helpers (kept for backward compat)
    # ------------------------------------------------------------------

    def is_factual_consistent(self, query: str, response: str) -> tuple:
        result = self._check_factual_consistency(query, response)
        return result["passed"], result["message"]

    def contains_uncertainty_pattern(self, text: str) -> bool:
        return any(
            re.search(p, text, re.IGNORECASE) for p in self._UNCERTAINTY_PATTERNS
        )

    def contains_speculative_language(self, text: str) -> list:
        found = []
        for p in [r"\b(likely|probably|probably not)\b"]:
            found.extend(re.findall(p, text, re.IGNORECASE))
        return found


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 3:
        query, response = sys.argv[1], sys.argv[2]
        result = HallucinationDetector().validate(query, response)
        out = {
            "query": query,
            "response": response,
            "is_valid": result["valid"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "checks": result["checks"],
            "flags": result["flags"],
        }
        print(json.dumps(out, indent=2))
        with open("hallucination_validation_detailed.json", "w") as f:
            json.dump(
                {"run": result, "timestamp": datetime.now().isoformat() + "Z"},
                f,
                indent=2,
            )
