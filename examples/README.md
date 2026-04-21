# Examples

| Script | Description |
|--------|-------------|
| `basic_validation.py` | Validate AI responses locally using `HallucinationDetector` — no server needed |
| `api_client.py` | Interact with the running FastAPI service endpoints |
| `langchain_integration.py` | LangChain callback handler + LCEL Runnable integration |

## Quick Start

```bash
# Install the package
pip install -e ..

# Run basic validation (no server needed)
python basic_validation.py

# Or start the API server and use the client
cd ..
uvicorn main:app --port 8000 &
python examples/api_client.py
```

## Custom Facts Database

See `basic_validation.py` for how to create and use a custom facts database.
The schema is documented in the main [README](../README.md#facts-database-schema).
