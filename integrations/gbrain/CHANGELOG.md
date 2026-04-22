# Changelog

All notable changes to the CertainLogic GBrain integration skill.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Semantic Versioning: [SemVer](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Planned
- XOR audit fragment system (tamper-evident verification)
- AgentPathfinder integration for cross-agent audit chains
- Real-time brain sync (push validated facts to brain immediately)
- Federation support (multiple GBrain instances sharing validation state)

## [1.0.0] - 2026-04-22

### Added
- Initial release of CYL-verify skill for GBrain
- Hallucination-guarded fact validation against 333 verified developer facts
- Cryptographic audit logging with append-only SQLite store
- Cross-modal review integration (`skills/conventions/cross-modal.yaml`)
- Automatic triggers: enrich Tier 1, idea-ingest >3 numbers, maintain stale sweep
- Manual triggers: "verify this claim", "is this true"
- Graceful degradation when Brain API is unavailable
- Health checks: `env_exists` for `BRAIN_API_KEY`, HTTP health endpoint probe
- MCP server integration for Claude, Cursor, and other agents
- 36 integration tests (10 MCP server, 26 end-to-end pipeline)
- Full documentation: SKILL.md, architecture, API reference, usage guide

### Changed
- Skill specification conforming to GBrain standard v1.0.0
- Frontmatter: id, name, version, category, requires, secrets, health_checks
- Body: brain-first lookup, compiled truth format, source attribution rules

### Integration
- Works with GBrain enrich, cross-modal-review, idea-ingest, media-ingest, maintain, query skills
- Adds `[Source: CertainLogic validated, ...]` and `[Audit: ...]` citations
- Compatible with GBrain v1.0.0+ skill format

## Migration Notes

### Upgrading from pre-v1.0.0 skills

If you used an earlier version of the CertainLogic GBrain integration:

1. Replace old skill file entirely (structure changed significantly)
2. Update `cross-modal.yaml` review_pairs to use `certainlogic-cyl-verify` as skill ID
3. Ensure `BRAIN_API_KEY` is set in environment (was optional before, now required for full function)
4. Run `gbrain skillpack-check` to verify conformance

See [migrations/v1.0.0.md](migrations/v1.0.0.md) for detailed rewrite steps.

---

*Release tag format: `gbrain-cyl-vX.Y.Z`*
*Issues: https://github.com/CertainLogicAI/hallucination-guard/issues*
