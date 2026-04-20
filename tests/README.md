# Tests

Unit and integration tests for the CertainLogic Verifier.

## Running Tests

```sh
pip install -e ".[dev]"   # installs dependencies
pytest tests/ -v
```

## Test Data

The `tests/facts_db.json` file contains sample facts for testing. Real usage should replace with organization-specific facts database.

## Test Coverage

Aims to:

- Validate hallucination detection accuracy across facts
- Test token reduction engine's similarity search
- Test intent router's classification accuracy  
- API endpoint functionality (RESTful)
- Integration with Docker and Kubernetes deployments

Please add new tests ensuring forward and backward compatibility.