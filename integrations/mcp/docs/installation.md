# MCP Server Installation

## Requirements

- Python 3.10 or higher
- `pip` or `uv`
- Brain API key (free at https://certainlogic.ai/signup)

## Install from PyPI

```bash
pip install certainlogic-mcp
```

Or with `uv` (faster):

```bash
uv add certainlogic-mcp
```

## Install from Source

```bash
git clone https://github.com/certainlogic/certainlogic-mcp.git
cd certainlogic-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

## Set Your API Key

### Option 1: Environment Variable (Recommended)

```bash
export BRAIN_API_KEY="your_key_here"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export BRAIN_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: .env File

Create `.env` in your project root:

```
BRAIN_API_KEY=your_key_here
```

### Option 3: Direct Parameter (Not Recommended)

Pass `api_key` in the tool call. This exposes the key to the LLM context. Use only for testing.

## Configure Your MCP Client

### Claude Code

Add to `~/.claude/server.json`:

```json
{
  "mcpServers": {
    "certainlogic-brain": {
      "command": "certainlogic-mcp",
      "env": {
        "BRAIN_API_KEY": "your_key_here"
      }
    }
  }
}
```

Restart Claude Code:

```bash
claude mcp restart
```

Verify:

```bash
claude mcp list
```

You should see `certainlogic-brain` in the list.

### Cursor

1. Open Settings (Cmd/Ctrl + ,)
2. Go to "MCP Servers"
3. Click "Add Server"
4. Name: `certainlogic-brain`
5. Command: `certainlogic-mcp`
6. Add env var: `BRAIN_API_KEY=your_key_here`
7. Save

### Windsurf

Add to `~/.windsurf/mcp.json`:

```json
{
  "mcpServers": {
    "certainlogic-brain": {
      "command": "certainlogic-mcp",
      "env": {
        "BRAIN_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Claude Desktop (Remote)

For remote MCP via HTTP:

```bash
# Start the server on a port
certainlogic-mcp --port 8787

# Or use ngrok for external access
ngrok http 8787 --url your-domain.ngrok.app
```

Then add to Claude Desktop config:

```json
{
  "mcpServers": {
    "certainlogic-brain": {
      "url": "https://your-domain.ngrok.app/mcp",
      "headers": {
        "Authorization": "Bearer your_key_here"
      }
    }
  }
}
```

**Note:** Remote MCP requires HTTPS and authentication. Local stdio transport is preferred.

## Test the Connection

Ask Claude Code: "What is the capital of France?"

Claude should use `brain_api_query` and return a verified answer with source attribution.

If it doesn't automatically use the tool, prompt it explicitly:

```
Use brain_api_query to check: What is the capital of France?
```

## Verify Installation

```bash
python -c "from certainlogic_mcp.server import brain_api_query; print('OK')"
```

If this fails with `ModuleNotFoundError`, ensure you're in the correct Python environment.

## Uninstall

```bash
pip uninstall certainlogic-mcp
```

## Next Steps

- Read the [Architecture Guide](architecture.md)
- See [Usage Examples](usage.md)
- Check the [API Reference](api-reference.md)
