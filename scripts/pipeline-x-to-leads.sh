#!/usr/bin/env bash
# X-to-Leads Pipeline
# Chains: X Monitor → Lead Qualification → ICP Match → Outreach Prep → Pipeline Tracking
# Usage: pipeline-x-to-leads.sh
# Answers: "Who's talking about my niche on X and should I reach out?"

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
REPORT="${WS_DIR}/artifacts/x-leads-${TIMESTAMP}.md"
mkdir -p "$(dirname "$REPORT")"

echo "📡 Running X-to-Leads pipeline"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "$REPORT" << EOF
# X-to-Leads Report
Generated: $(date '+%Y-%m-%d %H:%M %Z')

---

EOF

cd "$WS_DIR"

# ═══════════════════════════════════════
# STAGE 1: Scan X for prospects
# ═══════════════════════════════════════
echo "📡 Stage 1/4: Scanning X for prospects..."
if [ -f "skills/x-monitor-pro/scripts/x-search.sh" ]; then
  X_OUT=$(bash skills/x-monitor-pro/scripts/x-search.sh 2>&1)
  POST_COUNT=$(echo "$X_OUT" | grep -c "✅\|🟡\|⬜" || echo "0")
  HIGH=$(echo "$X_OUT" | grep -c "\[HIGH\]" || echo "0")
  echo "  Found ${POST_COUNT} posts (${HIGH} high-priority)"
  
  echo "## Stage 1: X Scan Results" >> "$REPORT"
  echo "\`\`\`" >> "$REPORT"
  echo "$X_OUT" >> "$REPORT"
  echo "\`\`\`" >> "$REPORT"
  echo "" >> "$REPORT"
else
  echo "  ⚠️ x-monitor-pro not installed"
  X_OUT=""
fi

# ═══════════════════════════════════════
# STAGE 2: Extract potential leads
# ═══════════════════════════════════════
echo "🎯 Stage 2/4: Qualifying leads..."

echo "## Stage 2: Lead Qualification" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Account | Followers | Tier | Topic Fit | Action |" >> "$REPORT"
echo "|---------|-----------|------|-----------|--------|" >> "$REPORT"

# Parse the X output for accounts with engagement
if [ -n "$X_OUT" ]; then
  # Extract accounts that posted about relevant topics
  echo "$X_OUT" | grep -E "@[a-zA-Z0-9_]+ \(" | while read -r line; do
    HANDLE=$(echo "$line" | grep -o '@[a-zA-Z0-9_]*' | head -1)
    FOLLOWERS=$(echo "$line" | grep -o '([0-9,]* followers)' | tr -dc '0-9' | head -1)
    
    if [ -z "$FOLLOWERS" ]; then
      FOLLOWERS="?"
      TIER="UNKNOWN"
    elif [ "${FOLLOWERS:-0}" -gt 100000 ]; then
      TIER="VIP — engage publicly"
    elif [ "${FOLLOWERS:-0}" -gt 10000 ]; then
      TIER="HIGH — reply + follow"
    elif [ "${FOLLOWERS:-0}" -gt 1000 ]; then
      TIER="MEDIUM — reply if relevant"
    else
      TIER="LOW — skip unless perfect fit"
    fi
    
    echo "| ${HANDLE} | ${FOLLOWERS} | ${TIER} | Check manually | Pending |" >> "$REPORT"
  done
fi
echo "" >> "$REPORT"

echo "  ✅ Leads extracted and tiered"

# ═══════════════════════════════════════
# STAGE 3: Check if pipeline tracker exists
# ═══════════════════════════════════════
echo "📋 Stage 3/4: Pipeline status..."
if [ -f "skills/cold-outreach-pro/scripts/follow-up-tracker.sh" ]; then
  PIPELINE_OUT=$(bash skills/cold-outreach-pro/scripts/follow-up-tracker.sh status 2>&1)
  echo "  ${PIPELINE_OUT}" | head -3
  echo "## Stage 3: Current Pipeline" >> "$REPORT"
  echo "${PIPELINE_OUT}" >> "$REPORT"
  echo "" >> "$REPORT"
fi

# ═══════════════════════════════════════
# STAGE 4: Draft engagement plan
# ═══════════════════════════════════════
echo "📝 Stage 4/4: Engagement plan..."

cat >> "$REPORT" << 'PLAN'
## Stage 4: Engagement Plan

### Immediate (today):
1. [ ] Reply to HIGH-tier accounts with value-add comments (no links)
2. [ ] Follow accounts that posted about your niche
3. [ ] Bookmark posts for quote-tweet later

### This week:
4. [ ] DM any HIGH-tier accounts that reply back
5. [ ] Add qualified leads to follow-up tracker
6. [ ] Create outreach sequence for best-fit leads

### Rules:
- No links in first interaction (builds trust)
- Reply with insights, not pitches
- One reply per account per day max
- VIP accounts: engage publicly first, DM only after 2-3 interactions
- Track everything in the pipeline tracker

### Reply Templates:
**Value-add reply:** "[Specific insight about their post]. We found [data point] when we [related experience]."
**Question reply:** "Interesting — have you tried [approach]? We tested it and [result]."
**Agreement + expansion:** "This. Plus [additional point they didn't mention]."
PLAN

echo "  ✅ Engagement plan generated"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ X-to-Leads report saved: $REPORT"
echo ""
echo "Pipeline: X Scan → Lead Qualification → Pipeline Check → Engagement Plan"
echo "Found prospects. Qualified them. Plan ready. Go engage."
