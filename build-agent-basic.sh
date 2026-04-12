#!/usr/bin/env bash
# build-agent-basic.sh – Automated builder for BASIC OpenClaw agents (no determinism, no action tracking)
# Usage: ./build-agent-basic.sh <agent_name> <skill1> <skill2> ...
# Example: ./build-agent-basic.sh myagent "crm finance market-research"
# Deliverable: A tarball ready for client installation

set -e

# -------------------- CONFIG --------------------
WORKSPACE="/data/.openclaw/workspace"
AGENTS_DIR="/data/.openclaw/agents"
DEFAULT_MODEL="mistral/7b-instruct-v0.3"  # free tier, working model
# ------------------------------------------------

if [ $# -lt 2 ]; then
  echo "Usage: $0 <agent_name> <skill1> [skill2 ...]"
  echo "Example: $0 myagent crm finance market-research"
  exit 1
fi

AGENT_NAME="$1"
shift
SKILLS=("$@")

echo "🔧 Building BASIC agent: $AGENT_NAME"
echo "📦 Skills: ${SKILLS[*]}"
echo "🤖 Model: $DEFAULT_MODEL (OpenRouter free tier)"

# 1️⃣ Create agent directory structure
mkdir -p "$AGENTS_DIR/$AGENT_NAME/agent"
mkdir -p "$AGENTS_DIR/$AGENT_NAME/skills"

# 2️⃣ Generate agent.json (basic config – no determinism, no action tracking)
cat > "$AGENTS_DIR/$AGENT_NAME/agent/agent.json" <<EOF
{
  "name": "$AGENT_NAME",
  "description": "Basic OpenClaw agent – simple, reliable, no extra overhead",
  "model": "$DEFAULT_MODEL",
  "deterministic": false,
  "allowExternalCalls": true,
  "features": {}
}
EOF

# 3️⃣ Create auth-profiles.json (empty – client will fill if they want)
cat > "$AGENTS_DIR/$AGENT_NAME/agent/auth-profiles.json" <<EOF
{}
EOF

# 4️⃣ Install requested skills
for skill in "${SKILLS[@]}"; do
  if [ -d "$AGENTS_DIR/$AGENT_NAME/skills/$skill" ]; then
    echo "✅ Skill already present: $skill"
  else
    if [ -d "$WORKSPACE/skills/$skill" ]; then
      cp -r "$WORKSPACE/skills/$skill" "$AGENTS_DIR/$AGENT_NAME/skills/"
      echo "📦 Copied skill: $skill"
    elif [ -d "/data/.npm-global/lib/node_modules/openclaw/skills/$skill" ]; then
      # Fallback to global skills install
      cp -r "/data/.npm-global/lib/node_modules/openclaw/skills/$skill" "$AGENTS_DIR/$AGENT_NAME/skills/"
      echo "📦 Copied from global: $skill"
    else
      echo "⚠️  Skill NOT found: $skill"
      echo "   (Will need to install manually via ClawHub or copy from backup)"
    fi
  fi
done

# 5️⃣ Register agent with OpenClaw
echo "📝 Registering agent with OpenClaw…"
if openclaw agents add "$AGENT_NAME" --path "$AGENTS_DIR/$AGENT_NAME/agent" 2>/dev/null; then
  echo "✅ Agent registered"
else
  echo "⚠️  Registration command failed – may need manual 'openclaw agents add'"
fi

# 6️⃣ Quick validation (non-deterministic)
echo "🔍 Validating agent…"
# Can we list it?
if openclaw agents list | grep -q "$AGENT_NAME"; then
  echo "✅ Agent appears in OpenClaw registry"
else
  echo "❌ Agent not found in registry"
fi

# Check skill files exist
for skill in "${SKILLS[@]}"; do
  if [ -d "$AGENTS_DIR/$AGENT_NAME/skills/$skill" ]; then
    echo "✅ Skill present: $skill"
  else
    echo "❌ Missing skill: $skill"
  fi
done

# 7️⃣ Create client delivery tarball
echo "📦 Creating delivery package…"
TAR_NAME="${AGENT_NAME}_basic_delivery_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$TAR_NAME" -C "$AGENTS_DIR" "$AGENT_NAME"
echo "✅ Created: $TAR_NAME"

# 8️⃣ Generate client README
cat > "${AGENT_NAME}_README_client.md" <<'EOF'
# Your OpenClaw Agent – Quick Start

## What You Got
- Agent name: AGENT_NAME
- Skills installed: LIST_SKILLS
- Model: mistral/7b-instruct-v0.3 (OpenRouter free tier)
- Deterministic: No (simple, reliable)

## Installation Steps

1. Upload the tarball to your VPS (e.g., via scp).
2. Extract:
   ```bash
   tar -xzf FILENAME.tar.gz
   ```
3. Move into agent folder:
   ```bash
   cd AGENT_NAME
   ```
4. (Optional) If you have an Anthropic API key and want to upgrade, edit:
   ```bash
   nano agent/auth-profiles.json
   # Add: { "anthropic": { "apiKey": "your-key-here" } }
   ```
5. Test the agent:
   ```bash
   openclaw agents query AGENT_NAME "Hello, how are you?"
   ```

That's it! The agent will respond using the free Mistral 7B model.

## Support
If you need help, reply to this message with details.
EOF

# Replace placeholders in README
sed -i "s/AGENT_NAME/$AGENT_NAME/g" "${AGENT_NAME}_README_client.md"
sed -i "s/LIST_SKILLS/${SKILLS[*]}/g" "${AGENT_NAME}_README_client.md"
sed -i "s/FILENAME/$TAR_NAME/g" "${AGENT_NAME}_README_client.md"

echo "✅ Client README: ${AGENT_NAME}_README_client.md"

# 9️⃣ Final summary
echo ""
echo "============================================================="
echo "🤖 BASIC AGENT BUILD COMPLETE"
echo "============================================================="
echo "Agent name:      $AGENT_NAME"
echo "Skills:          ${SKILLS[*]}"
echo "Delivery tarball: $TAR_NAME"
echo "Client README:   ${AGENT_NAME}_README_client.md"
echo "Agent location:  $AGENTS_DIR/$AGENT_NAME"
echo ""
echo "Next steps:"
echo "1. Test manually: openclaw agents query $AGENT_NAME \"test\""
echo "2. Upload tarball + README to client"
echo "3. Keep backup of config for future re-installs"
echo "============================================================="