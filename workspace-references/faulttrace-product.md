# FAULTTFAULTTRACE-REFERENCE-START
# FaultTrace — Product Definition

FaultTrace is a **static analysis tool for Allen-Bradley PLC code** (L5X files). It scans programs for common issues, unused tags, type mismatches, and safety violations without executing the code.

## Core Capabilities

- **18 built-in rules** covering:
  - Unused/uninitialized tags
  - Instruction misuse (OTL/OTU pairs, ONS patterns)
  - Data type safety
  - Cross-rung analysis
  - I/O mapping verification
- **Trace engine** — maps signal flow through routines
- **Cross-reference builder** — shows where tags are read/written
- **I/O map extraction** — lists all physical I/O addresses
- **Export formats** — JSON (for APIs), CSV, HTML reports

## Target Users

- Controls engineers working with Studio 5000
- Industrial automation teams needing code reviews
- OEMs requiring compliance documentation
- Integrators validating customer programs

## Positioning

> "A linter for PLC code — like ESLint for ladder logic."

It does **not** simulate runtime behavior; it's purely static.

## Current Access

- Web app: browser-based upload
- API (planned): `POST /api/v1/analyze` returning JSON

## Integration Points

- CI/CD pipelines (GitHub Actions, Jenkins)
- Version control hooks
- Documentation generators
- Compliance checkers (ISO 13849, UL 1998)

---
*Canonical reference. Do not edit without updating dependents.*
# FAULTTFAULTTRACE-REFERENCE-END
