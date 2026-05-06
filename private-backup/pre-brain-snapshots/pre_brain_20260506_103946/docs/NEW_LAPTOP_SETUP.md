# CertainLogic Tester Agent — New Laptop Setup

**Goal:** Turn a fresh laptop into a CertainLogic satellite agent for testing, research, and coding overflow.
**Hardware assumption:** Capable of running mid-level local LLM (~8-16GB VRAM or 32GB+ RAM)

---

## Phase 1: Base Install (5 min)

### 1. Install Node.js + OpenClaw
```bash
# macOS (if that's what the laptop is)
brew install node

# Or download from https://nodejs.org (LTS)

# Install OpenClaw globally
npm install -g openclaw

# Verify
openclaw --version
clawhub --version
```

### 2. Install CertainLogic Skills
```bash
# Install our published skills (what actually exists)
clawhub install certainlogic-pathfinder
clawhub install certainlogic-onboarding-wizard 2>/dev/null || echo "optional"
clawhub install certainlogic-context-tokenreducer 2>/dev/null || echo "optional"
clawhub install skill-vetter-plus 2>/dev/null || echo "optional"
clawhub install skill-oracle 2>/dev/null || echo "optional"

# Verify installs
clawhub list | grep certainlogic
```

### 3. Clone Workspace (not full repo, just config)
```bash
# Option A: Fresh clone (when we have a public repo)
git clone https://github.com/CertainLogicAI/workspace.git ~/certainlogic-workspace

# Option B: For now, manually copy key config files from main machine:
# - config/model_routing.json
# - docs/ (for reference)
# - HEARTBEAT.md (for process reference)
```

---

## Phase 2: Local LLM Setup (10 min)

### Option A: Ollama (Recommended — easiest)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a mid-level model (~4-8GB)
ollama pull qwen2.5:14b        # Strong reasoning, code
ollama pull gemma3:12b         # Good general purpose
ollama pull mistral:7b         # Fast, lightweight

# Verify
ollama list
ollama run qwen2.5:14b "Hello"
```

### Option B: LM Studio (GUI, good for testing)
```bash
# Download from https://lmstudio.ai
# Good for interactive testing, less good for automation
```

### Configure OpenClaw to use local model
```bash
# In ~/.openclaw/config.json or via openclaw CLI
# Set local model as fallback or tier
```

---

## Phase 3: CertainLogic Config Sync (5 min)

### Copy model routing config
```bash
# From main workspace to laptop
scp /data/.openclaw/workspace/config/model_routing.json \
    anton@new-laptop:~/certainlogic-workspace/config/
```

### Configure for free-tier operation
```json
{
  "tiers": {
    "local_testing": {
      "provider": "ollama",
      "model": "qwen2.5:14b",
      "base_url": "http://localhost:11434"
    },
    "free_remote": {
      "provider": "openrouter",
      "model": "google/gemma-4-26b-a4b-it:free"
    }
  }
}
```

---

## Phase 4: Verification

```bash
# Test 1: Pathfinder works
python3 ~/.openclaw/skills/certainlogic-pathfinder/scripts/demo_live.py

# Test 2: AgentPathfinder audit trail
python3 -m agentpathfinder audit --version

# Test 3: Local LLM responds
ollama run qwen2.5:14b "What is deterministic AI?"

# Test 4: Git is clean
cd ~/certainlogic-workspace && git status
```

---

## What This Gives You

1. **Independent CertainLogic instance** — can build/test without touching main workspace
2. **Local LLM for privacy** — no API calls leave the machine for sensitive work
3. **Free-tier remote fallback** — when local model isn't enough
4. **Same model routing** — consistent behavior across machines
5. **Clean machine** — validates our install process (B1 audit side benefit)

---

## Optional: Auto-Sync with Main Workspace

```bash
# Cron job to pull latest config from main
# Or use Syncthing/Dropbox for config/ folder
```

## Status: Ready for Anton
