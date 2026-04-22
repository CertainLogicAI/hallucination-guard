# Installation Guide

## Prerequisites

- GBrain installed and running (`gbrain serve` or `bun run src/index.ts`)
- Python 3.10+ (for MCP server)
- CertainLogic API key (free tier: 3,000 queries/month)

## Step 1: Get Your API Key

1. Go to https://certainlogic.ai/signup
2. Create a free account
3. Copy your API key from the dashboard

No credit card required for the free tier.

## Step 2: Install the MCP Server

```bash
pip install certainlogic-mcp
```

Set your API key as an environment variable:

```bash
export BRAIN_API_KEY="your_key_here"
```

Or add to your `.env` file:

```
BRAIN_API_KEY=your_key_here
```

### Verify Installation

```bash
python -c "from certainlogic_mcp.server import brain_api_query; print('OK')"
```

## Step 3: Configure Your Agent

### Claude Code

Add to `~/.claude/server.json`:

```json
{
  "mcpServers": {
    "gbrain": {
      "command": "gbrain",
      "args": ["serve"]
    },
    "certainlogic": {
      "command": "certainlogic-mcp"
    }
  }
}
```

Restart Claude Code to pick up the new server.

### Cursor

Add to Settings > MCP Servers:

```json
{
  "mcpServers": {
    "certainlogic": {
      "command": "certainlogic-mcp",
      "env": {
        "BRAIN_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Windsurf

Add to your MCP config:

```json
{
  "mcpServers": {
    "certainlogic": {
      "command": "certainlogic-mcp"
    }
  }
}
```

## Step 4: Install the GBrain Skill

### Option A: Copy Skill File (Recommended)

```bash
cd /path/to/gbrain/skills
cp /path/to/certainlogic-gbrain-integration/skills/CYL-verify.md ./
```

### Option B: Symlink (for Development)

```bash
cd /path/to/gbrain/skills
ln -s /path/to/certainlogic-gbrain-integration/skills/CYL-verify.md ./
```

## Step 5: Configure Cross-Modal Review

Edit `gbrain/skills/conventions/cross-modal.yaml` and add:

```yaml
review_pairs:
  # Existing pairs...
  - trigger_skill: enrich
    review_skill: cyl-verify
    when: "Tier 1 enrichment or any company/person data"
  - trigger_skill: idea-ingest
    review_skill: cyl-verify
    when: "page contains >3 numerical claims or >2 quotes"
  - trigger_skill: media-ingest
    review_skill: cyl-verify
    when: "transcript enrichment produces >5 entity updates"
```

Save and restart your agent.

## Step 6: Test the Integration

Trigger a fact-check in your agent:

```
User: "Elon Musk founded Tesla in 2003."
Agent: → CYL-verify → brain_api_query("Did Elon Musk found Tesla in 2003?")
       → { "answer": "Yes. Elon Musk, JB Straubel, Martin Eberhard, Marc Tarpenning, and Ian Wright founded Tesla Motors in 2003.",
            "confident": true, "method": "facts" }
       → Fact validated → written to brain with [Source: CertainLogic validated]
```

## Step 7: Verify Audit Log

Check that verification decisions are being logged:

```bash
sqlite3 ~/.certainlogic/audit.db "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 5;"
```

(Coming in v2.0 with cryptographic audit chain.)

## Next Steps

- Read the [Architecture Guide](02-architecture.md) to understand how the integration works
- See [Usage Examples](03-usage.md) for common workflows
- Check the [API Reference](04-api-reference.md) for all available tools and parameters
