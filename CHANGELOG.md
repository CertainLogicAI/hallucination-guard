# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026‑04‑20

### Added
- Initial open‑source release of CertainLogic hallucination‑guard.
- Core components:
  - Hallucination detector with factual‑consistency, uncertainty, internal‑consistency, and specificity checks.
  - Token‑reduction engine with deterministic caching and fallback summarization.
  - Deterministic memory search (TF‑IDF) over verified facts.
  - Intent router for goal‑driven query classification.
- Full FastAPI service (`validate`, `reduce`, `search`, `route`, `health`, `metrics`, `cache` endpoints).
- Helm chart for Kubernetes deployment.
- Complete test suite (11/11 passing).
- OpenClaw skill (`hallucination-guard.skill`) for agent auto‑installation.
- Social preview banner, badges, comparison table in README.

### Fixed
- Numeric matching with unit awareness.
- Safe‑qualifier handling (“in the quantum realm”, “in theory”) to avoid false positives.
- Import structure and packaging (`pyproject.toml`, `src/` layout).
- API endpoint validation models (RouteRequest, SearchRequest, etc.).

### Changed
- Restructured repository to proper Python package (`src/hallucination_guard/`).
- Updated README with hero section, benchmarks, quick‑start guide.

### Security
- No known vulnerabilities. Facts DB is read‑only; all user‑provided inputs are validated.
- SQLite cache isolated per instance; no sensitive data stored.