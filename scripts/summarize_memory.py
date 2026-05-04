#!/usr/bin/env python3
"""Daily chat log summarizer — writes key decisions to memory/YYYY-MM-DD.md"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path to transcript
TRANSCRIPT = Path("/data/.openclaw/agents/main/sessions/da094e1a-f299-4cef-9987-f7ac0a0f3a8c.jsonl")
MEMORY_DIR = Path("/data/.openclaw/workspace/memory")

# Parse arguments
if len(sys.argv) > 1:
    # Run for a specific transcript file
    TRANSCRIPT = Path(sys.argv[1])

if not TRANSCRIPT.exists():
    print(f"Transcript not found: {TRANSCRIPT}")
    sys.exit(1)

MEMORY_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
memory_file = MEMORY_DIR / f"{today}.md"

# Read transcript lines
lines = TRANSCRIPT.read_text().strip().split("\n")

# Extract key user messages and assistant responses
key_points = []
decisions = []
errors = []

for line in lines:
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        continue

    # Look for user messages
    if entry.get("role") == "user":
        content = entry.get("content", "")
        if content and len(content.split()) > 5:
            key_points.append(("user", content[:200]))

    # Look for tool results showing failures
    if "result" in entry and "error" in str(entry.get("result", "")).lower():
        tool = entry.get("tool", "?")
        key_points.append(("error", f"Tool failure: {tool}"))

# Build memory entry
memory_content = f"""# Memory Log — {today}

## Key Decisions
"""

# Add any decisions we can infer
# (This would be enhanced with actual LLM summarization)
memory_content += "\n".join(f"- {content[:150]}" for _, content in key_points[-20:])

memory_content += f"""

## Status
- Transcript lines: {len(lines)}
- Logged at: {datetime.now(timezone.utc).isoformat()}

## Notes
Add manual notes here as needed.
"""

# Write or append
if memory_file.exists():
    # Append to existing
    existing = memory_file.read_text()
    memory_file.write_text(existing + "\n\n" + memory_content)
else:
    memory_file.write_text(memory_content)

print(f"Memory written to: {memory_file}")
print(f"Lines processed: {len(lines)}")
print(f"Key points: {len(key_points)}")
