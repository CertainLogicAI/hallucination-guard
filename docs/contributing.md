# Contributing

We welcome contributions! Here's how to get started.

## Setup

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Development Workflow

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Run linting: `black src tests && ruff check src tests && isort src tests`
5. Submit a pull request

## Code Style

- **Formatter:** black (line length 88)
- **Linter:** ruff
- **Import sorting:** isort (black-compatible profile)

Pre-commit hooks enforce these automatically.

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=hallucination_guard --cov-report=term-missing
```

## Adding Facts

To add facts to the database, follow the [Facts Schema](api/facts-schema.md) and submit a PR with:

1. New entries in `facts_db.json`
2. Source URL or documentation reference
3. Verification date

## Reporting Issues

Use the [bug report template](https://github.com/CertainLogicAI/hallucination-guard/issues/new?template=bug_report.md) or [feature request template](https://github.com/CertainLogicAI/hallucination-guard/issues/new?template=feature_request.md).

## Code of Conduct

Please read our [Code of Conduct](https://github.com/CertainLogicAI/hallucination-guard/blob/main/CODE_OF_CONDUCT.md) before contributing.
