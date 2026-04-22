# Contributing to CertainLogic + GBrain Integration

## Philosophy

CertainLogic is a free contribution to the gbrain ecosystem. We believe that
validated facts make every brain better. This integration is maintained openly
and welcomes community contributions.

## How to Contribute

### 1. Report Issues

Found a bug? A fact that validates incorrectly?

- Open an issue with:
  - The claim that was checked
  - Expected result vs actual result
  - Your `BRAIN_API_KEY` tier (not the key itself)
  - Timestamp of the check (for audit log lookup)

### 2. Submit PRs

**Skill changes:**
1. Fork gbrain and/or this integration repo
2. Edit `skills/CYL-verify.md`
3. Update test cases in `tests/`
4. Ensure frontmatter remains valid
5. Submit PR with description of the change

**Code changes:**
1. Fork the `certainlogic-mcp` repo
2. Write tests first (TDD preferred)
3. Ensure all 10 tests pass: `pytest tests/`
4. Submit PR

**Documentation:**
1. Edit the relevant `.md` file in `docs/`
2. Keep style consistent with existing docs
3. Submit PR

### 3. Validate Facts for the Community

The biggest contribution: verified facts.

If you verify a fact through CYL-verify, it enters the CertainLogic facts DB
and helps ALL users. Every validated fact improves the brain of every gbrain
user.

Submit validated facts via PR to the CertainLogic facts repository.

## Code of Conduct

- Be respectful. We debate facts, not people.
- Assume good intent. A wrong fact is not a wrong person.
- All contributions are valuated on their factual merit.
- Sources matter more than opinions.

## Development Setup

```bash
# Clone repos
git clone https://github.com/garrytan/gbrain.git
git clone https://github.com/certainlogic/certainlogic-mcp.git
git clone https://github.com/certainlogic/gbrain-integration.git

# Install MCP server
cd certainlogic-mcp
pip install -e .
pytest tests/

# Link to gbrain
cd ../gbrain
ln -s ../gbrain-integration/skills/CYL-verify.md skills/

# Run tests
pytest tests/skills/test_cyl_verify.py
```

## Release Process

| Version | Trigger | Action |
|---|---|---|
| Patch (1.0.x) | Bug fix | Update skill file, submit PR |
| Minor (1.x.0) | New feature | Update docs, tests, skill file |
| Major (x.0.0) | Breaking change | Coordinate with gbrain maintainers |

## Communication

- **Issues:** Use GitHub issues for bugs, feature requests, fact corrections
- **Pull Requests:** Use GitHub PRs for code changes
- **Discussions:** Use GitHub Discussions for general questions

## Credits

Contributors will be listed in `CONTRIBUTORS.md` and mentioned in release notes.

---

*CertainLogic is the "validated data guys" for the gbrain community.*
