#!/usr/bin/env bash
# Skill Security Scanner — automated pattern detection for ClawHub skills
# Usage: ./security-scan.sh <skill-directory>
# Exit codes: 0 = clean, 1 = warnings found, 2 = critical findings

set -uo pipefail

SKILL_DIR="${1:?Usage: security-scan.sh <skill-directory>}"
SKILL_NAME=$(basename "$SKILL_DIR")

if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ Directory not found: $SKILL_DIR"
  exit 2
fi

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

CRITICAL=0
WARNINGS=0
INFO=0

header() { echo -e "\n${NC}=== $1 ===${NC}"; }
critical() { echo -e "${RED}[CRITICAL]${NC} $1"; ((CRITICAL++)); }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; ((WARNINGS++)); }
info() { echo -e "${GREEN}[OK]${NC} $1"; ((INFO++)); }

header "Security Scan: $SKILL_NAME"
echo "Path: $SKILL_DIR"
echo "Scan time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- File inventory ---
header "File Inventory"
TOTAL_FILES=$(find "$SKILL_DIR" -type f | grep -v ".clawhub\|_meta.json\|node_modules" | wc -l)
echo "Total files: $TOTAL_FILES"
find "$SKILL_DIR" -type f | grep -v ".clawhub\|_meta.json\|node_modules" | while read -r f; do
  size=$(wc -c < "$f" | tr -d ' ')
  echo "  $(basename "$f") ($size bytes)"
done

# --- Script/executable detection ---
header "Executable Content"
SCRIPTS=$(find "$SKILL_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.mjs" -o -name "*.ts" \) | grep -v ".clawhub\|node_modules" || true)
if [ -n "$SCRIPTS" ]; then
  warning "Contains executable scripts — manual review required:"
  echo "$SCRIPTS" | while read -r s; do echo "  $(basename "$s")"; done
else
  info "No executable scripts found"
fi

# --- Network/exfiltration patterns ---
header "Network & Exfiltration"
NET_HITS=$(grep -rni "curl\|wget\|fetch(\|http\.get\|https\.get\|axios\|request(\|XMLHttpRequest" "$SKILL_DIR" --include="*.md" --include="*.json" --include="*.sh" --include="*.py" --include="*.js" --include="*.mjs" 2>/dev/null | grep -v ".clawhub\|_meta.json\|node_modules\|package-lock" || true)
if [ -n "$NET_HITS" ]; then
  COUNT=$(echo "$NET_HITS" | wc -l)
  warning "$COUNT network-related patterns found:"
  echo "$NET_HITS" | head -10 | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
  [ "$COUNT" -gt 10 ] && echo "  ... and $((COUNT - 10)) more"
else
  info "No network patterns detected"
fi

# --- Credential/secret patterns ---
header "Credentials & Secrets"
CRED_HITS=$(grep -rni "api.key\|apikey\|api_key\|token\|password\|secret\|\.env\|credentials\|private.key\|ssh.key" "$SKILL_DIR" --include="*.md" --include="*.json" --include="*.sh" --include="*.py" --include="*.js" --include="*.mjs" 2>/dev/null | grep -v ".clawhub\|_meta.json\|node_modules\|package-lock" || true)
if [ -n "$CRED_HITS" ]; then
  COUNT=$(echo "$CRED_HITS" | wc -l)
  warning "$COUNT credential-related patterns found (review for hardcoded secrets):"
  echo "$CRED_HITS" | head -10 | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
else
  info "No credential patterns detected"
fi

# --- Destructive commands ---
header "Destructive Commands"
DEST_HITS=$(grep -rni "rm -rf\|rm -r /\|rmdir /\|sudo rm\|drop table\|truncate table\|format [cC]:" "$SKILL_DIR" --include="*.md" --include="*.json" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | grep -v ".clawhub\|_meta.json\|node_modules" || true)
if [ -n "$DEST_HITS" ]; then
  COUNT=$(echo "$DEST_HITS" | wc -l)
  warning "$COUNT destructive command patterns found:"
  echo "$DEST_HITS" | head -5 | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
else
  info "No destructive commands detected"
fi

# --- Prompt injection patterns ---
header "Prompt Injection"
INJECT_HITS=$(grep -rni "ignore previous\|disregard\|system prompt\|you are now\|forget your instructions\|override\|jailbreak\|do anything now" "$SKILL_DIR" --include="*.md" --include="*.json" 2>/dev/null | grep -v ".clawhub\|_meta.json" || true)
if [ -n "$INJECT_HITS" ]; then
  COUNT=$(echo "$INJECT_HITS" | wc -l)
  critical "$COUNT prompt injection patterns found:"
  echo "$INJECT_HITS" | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
else
  info "No prompt injection patterns detected"
fi

# --- Obfuscated code ---
header "Obfuscation"
OBF_HITS=$(grep -rni "eval(\|exec(\|base64\|atob\|btoa\|\\\\x[0-9a-f]\|fromCharCode\|String.raw" "$SKILL_DIR" --include="*.sh" --include="*.py" --include="*.js" --include="*.mjs" 2>/dev/null | grep -v ".clawhub\|_meta.json\|node_modules\|package-lock" || true)
if [ -n "$OBF_HITS" ]; then
  COUNT=$(echo "$OBF_HITS" | wc -l)
  critical "$COUNT obfuscation patterns found — requires manual review:"
  echo "$OBF_HITS" | head -5 | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
else
  info "No obfuscation patterns detected"
fi

# --- Pipe-to-shell installs ---
header "Risky Install Patterns"
PIPE_HITS=$(grep -rni "curl.*|.*sh\|wget.*|.*sh\|curl.*|.*bash\|pip install.*--break" "$SKILL_DIR" --include="*.md" --include="*.sh" 2>/dev/null | grep -v ".clawhub\|_meta.json" || true)
if [ -n "$PIPE_HITS" ]; then
  COUNT=$(echo "$PIPE_HITS" | wc -l)
  warning "$COUNT pipe-to-shell install patterns found:"
  echo "$PIPE_HITS" | while read -r h; do
    echo "  $(echo "$h" | sed "s|$SKILL_DIR/||")"
  done
else
  info "No risky install patterns detected"
fi

# --- SKILL.md frontmatter check ---
header "Skill Quality"
if grep -q "^---" "$SKILL_DIR/SKILL.md" 2>/dev/null; then
  if grep -q "^description:" "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    info "SKILL.md has frontmatter with description"
  else
    warning "SKILL.md frontmatter missing description field (won't trigger properly)"
  fi
  if grep -q "^name:" "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    info "SKILL.md has name field"
  else
    warning "SKILL.md frontmatter missing name field"
  fi
else
  warning "SKILL.md has no YAML frontmatter"
fi

# Unnecessary files
CLUTTER=$(find "$SKILL_DIR" -maxdepth 1 \( -name "README.md" -o -name "CHANGELOG.md" -o -name "REVIEW.md" -o -name "INSTALLATION_GUIDE.md" \) | grep -v ".clawhub" || true)
if [ -n "$CLUTTER" ]; then
  warning "Contains unnecessary files (per AgentSkill spec):"
  echo "$CLUTTER" | while read -r c; do echo "  $(basename "$c")"; done
else
  info "No unnecessary clutter files"
fi

# SKILL.md size
SKILL_LINES=$(wc -l < "$SKILL_DIR/SKILL.md" 2>/dev/null || echo 0)
if [ "$SKILL_LINES" -gt 300 ]; then
  warning "SKILL.md is $SKILL_LINES lines — consider splitting into reference files (<300 recommended)"
elif [ "$SKILL_LINES" -gt 500 ]; then
  critical "SKILL.md is $SKILL_LINES lines — will bloat context window significantly"
else
  info "SKILL.md is $SKILL_LINES lines (good)"
fi

# --- Summary ---
header "SUMMARY"
echo -e "Critical: ${RED}$CRITICAL${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Passed:   ${GREEN}$INFO${NC}"
echo ""

if [ "$CRITICAL" -gt 0 ]; then
  echo -e "${RED}⛔ CRITICAL ISSUES FOUND — do not install without thorough manual review${NC}"
  exit 2
elif [ "$WARNINGS" -gt 0 ]; then
  echo -e "${YELLOW}⚠️  WARNINGS — review flagged items before installing${NC}"
  exit 1
else
  echo -e "${GREEN}✅ CLEAN — no issues detected${NC}"
  exit 0
fi
