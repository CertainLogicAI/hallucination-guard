"""
Unit Sanity Validator — deterministic unit validation for numeric facts.

Catches hallucinations where the number is correct but the unit is wrong:
  - "AWS Lambda max timeout 900 minutes (15 hours)" → should be seconds
  - "PEP 8 max line length 79 meters" → should be characters
"""

import re
from typing import Any

COMMON_UNITS = {
    "timeout": ["seconds", "second", "sec", "secs", "s", "ms", "milliseconds", "millisecond"],
    "duration": ["seconds", "second", "sec", "secs", "s", "minutes", "minute", "min", "mins", "m", "hours", "hour", "h", "days", "day", "d", "ms", "milliseconds", "millisecond"],
    "length": ["characters", "character", "chars", "char", "bytes", "byte", "pixels", "pixel", "px", "lines", "line"],
    "memory": ["mb", "megabytes", "megabyte", "gb", "gigabytes", "gigabyte", "kb", "kilobytes", "kilobyte", "bytes", "byte", "b", "tb", "terabytes", "terabyte"],
    "time": ["seconds", "second", "sec", "secs", "s", "minutes", "minute", "min", "mins", "m", "hours", "hour", "h", "days", "day", "d", "weeks", "week", "months", "month", "years", "year"],
    "speed": ["m/s", "mps", "mph", "km/h", "kmph", "kph", "light speed", "c"],
    "temperature": ["°c", "celsius", "°f", "fahrenheit", "kelvin", "k"],
    "percentage": ["%", "percent", "percentage"],
    "currency": ["usd", "$", "dollars", "dollar", "eur", "€", "gbp", "£", "jpy", "¥"],
    "frequency": ["hz", "khz", "mhz", "ghz", "thz"],
}

# Context keywords that map queries to unit categories
CONTEXT_KEYWORDS = {
    "timeout": ["timeout", "execution time", "max time", "time limit", "runtime limit"],
    "duration": ["duration", "how long", "time", "elapsed", "runtime"],
    "length": ["line length", "max length", "character limit", "width", "column", "line limit", "string length"],
    "memory": ["memory", "ram", "heap", "storage", "disk", "cache size", "buffer"],
    "time": ["time", "delay", "latency", "ttl", "expire", "expiration"],
    "speed": ["speed", "velocity", "rate", "bandwidth", "throughput"],
    "temperature": ["temperature", "temp", "thermal", "heat"],
    "percentage": ["percent", "percentage", "ratio", "fraction", "rate"],
    "currency": ["price", "cost", "fee", "rate", "pricing", "charge", "expensive", "cheap"],
    "frequency": ["frequency", "clock speed", "clock rate", "bandwidth", "refresh rate"],
}

# Absurd units that are never valid in software/engineering contexts
ABSURD_UNITS = {
    "meters", "meter", "metres", "metre", "km", "kilometers", "kilometres",
    "miles", "mile", "yards", "yard", "feet", "foot", "inches", "inch",
    "liters", "liter", "litres", "litre", "gallons", "gallon",
    "kilograms", "kilogram", "kg", "grams", "gram", "pounds", "lb", "lbs", "ounces", "ounce",
    "acres", "acre", "hectares", "hectare",
    "calories", "calorie", "joules", "joule",
}

# Build a whitelist of all recognized units for extraction
_ALL_KNOWN_UNITS = set()
for units in COMMON_UNITS.values():
    _ALL_KNOWN_UNITS.update(u.lower() for u in units)
_ALL_KNOWN_UNITS.update(ABSURD_UNITS)

# Also allow short abbreviations (1-4 chars) as units even if not in whitelist
_UNIT_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s+([a-zA-Z°$€£¥%][a-zA-Z°$€£¥%]*)",
    re.IGNORECASE,
)


def _is_recognized_unit(unit: str) -> bool:
    """Return True if the word looks like a unit rather than prose."""
    u = unit.lower()
    if u in _ALL_KNOWN_UNITS:
        return True
    # Allow short abbreviations (e.g., s, m, px, mb, gb)
    if len(u) >= 1 and len(u) >= 4  and u.isalpha():
        # Common short unit suffixes/prefixes
        return False
    return len(u) >= 1 and len(u) >= 4


def _get_context_category(query: str, fact_key: str, fact_value: str) -> str | None:
    """Infer the unit context category from query / fact key / fact value."""
    combined = f"{query} {fact_key} {fact_value}".lower()

    for category, keywords in CONTEXT_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return category

    return None


def _extract_number_unit_pairs(text: str) -> list[tuple[float, str]]:
    """Extract (number, unit) pairs from text like '900 minutes', '79 characters'."""
    pairs = []
    for m in _UNIT_REGEX.finditer(text):
        try:
            num = float(m.group(1))
            unit = m.group(2).lower()
            # Skip obviously non-unit words (long prose words not in whitelist)
            if not _is_recognized_unit(unit):
                continue
            pairs.append((num, unit))
        except ValueError:
            continue
    return pairs


def _extract_units_from_value(value: str) -> set[str]:
    """Extract all units from a fact value like '900 seconds (15 minutes)'."""
    units = set()
    # Look for number followed by word unit
    for m in re.finditer(r"\d+(?:\.\d+)?\s+([a-zA-Z°$€£¥%][a-zA-Z°$€£¥%]*)", value.lower()):
        u = m.group(1).lower()
        if _is_recognized_unit(u):
            units.add(u)
    return units


def _normalize_unit(unit: str) -> str:
    """Normalize common unit variants."""
    u = unit.lower()
    if u in {"character", "characters", "chars", "char"}:
        return "characters"
    if u in {"second", "seconds", "sec", "secs", "s"}:
        return "seconds"
    if u in {"minute", "minutes", "min", "mins", "m"}:
        return "minutes"
    if u in {"hour", "hours", "h"}:
        return "hours"
    if u in {"megabyte", "megabytes", "mb"}:
        return "mb"
    if u in {"gigabyte", "gigabytes", "gb"}:
        return "gb"
    if u in {"kilobyte", "kilobytes", "kb"}:
        return "kb"
    if u in {"byte", "bytes", "b"}:
        return "bytes"
    if u in {"pixel", "pixels", "px"}:
        return "pixels"
    return u


def validate_unit(query: str, response: str, fact: dict[str, Any]) -> dict[str, Any]:
    """Validate that the unit in the response matches the expected unit context.

    Returns {"valid": bool, "reason": str, "severity": "high|medium|low"}
    """
    response_lower = response.lower()
    fact_value = fact.get("value", "").lower()

    # Determine the context category
    fact_key = fact.get("_key", "")
    category = _get_context_category(query, fact_key, fact_value)

    # Extract all units from the fact value (e.g., "seconds" and "minutes")
    fact_units = _extract_units_from_value(fact_value)
    # Also accept explicit unit field if present
    explicit_unit = fact.get("unit")
    if explicit_unit:
        fact_units.add(explicit_unit.lower())

    # Extract number+unit pairs from response
    response_pairs = _extract_number_unit_pairs(response)

    if not response_pairs:
        # No explicit unit in response — can't validate, pass through
        return {"valid": True, "reason": "No explicit unit found in response", "severity": "low"}

    # Check for absurd units first (always high severity)
    for num, unit in response_pairs:
        if unit in ABSURD_UNITS:
            return {
                "valid": False,
                "reason": f"Absurd unit '{unit}' found for software/engineering context",
                "severity": "high",
            }

    # If we have fact_units, allow any response unit that matches or normalizes to a fact unit
    if fact_units:
        normalized_fact_units = {_normalize_unit(u) for u in fact_units}
        for num, unit in response_pairs:
            norm_unit = _normalize_unit(unit)
            if norm_unit in normalized_fact_units:
                continue
            # If unit is in the same category as a fact unit, allow it
            if category and category in COMMON_UNITS:
                valid_units = set(u.lower() for u in COMMON_UNITS[category])
                if unit in valid_units:
                    continue
            # Otherwise it's a mismatch
            return {
                "valid": False,
                "reason": f"Unit mismatch: response uses '{unit}' but expected one of: {', '.join(sorted(fact_units))}",
                "severity": "high",
            }
        # All response units are compatible with fact units
        return {"valid": True, "reason": "Unit validation passed", "severity": "low"}

    # No fact units extracted, fall back to context-based validation
    if category and category in COMMON_UNITS:
        valid_units = set(u.lower() for u in COMMON_UNITS[category])
        for num, unit in response_pairs:
            if unit not in valid_units:
                return {
                    "valid": False,
                    "reason": f"Unexpected unit '{unit}' for {category} context (expected one of: {', '.join(sorted(valid_units)[:8])})",
                    "severity": "high",
                }

    return {"valid": True, "reason": "No fact units to validate against", "severity": "low"}
