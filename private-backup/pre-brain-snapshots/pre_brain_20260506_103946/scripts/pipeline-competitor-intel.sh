#!/usr/bin/env bash
# Full Competitor Intelligence Pipeline
# Chains: Market Research → SEO Audit → GEO Audit → Outreach Setup
# Usage: pipeline-competitor-intel.sh <competitor_url>
# Output: Combined report + ICP template ready for outreach

set -uo pipefail

URL="${1:?Usage: pipeline-competitor-intel.sh <competitor_url>}"
DOMAIN=$(echo "$URL" | sed 's|https\?://||;s|/.*||')
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
REPORT="workspace/artifacts/intel-${DOMAIN}-${TIMESTAMP}.md"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

cd "$WS_DIR"
mkdir -p workspace/artifacts 2>/dev/null || mkdir -p artifacts 2>/dev/null

# Use artifacts dir that exists
if [ -d "artifacts" ]; then
  REPORT="artifacts/intel-${DOMAIN}-${TIMESTAMP}.md"
elif [ -d "workspace/artifacts" ]; then
  REPORT="workspace/artifacts/intel-${DOMAIN}-${TIMESTAMP}.md"
fi

echo "🔍 Running full competitor intelligence pipeline on ${URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "$REPORT" << EOF
# Competitor Intelligence Report: ${DOMAIN}
Generated: $(date '+%Y-%m-%d %H:%M %Z')
Target: ${URL}

---

EOF

# ═══════════════════════════════════════
# STAGE 1: Market Research — Who are they?
# ═══════════════════════════════════════
echo "📊 Stage 1/5: Market Research (competitor scraper)..."
SCRAPE_OUTPUT=""
if [ -f "skills/market-research-pro/scripts/competitor-scraper.sh" ]; then
  SCRAPE_OUTPUT=$(bash skills/market-research-pro/scripts/competitor-scraper.sh "$URL" 2>&1)
  echo "$SCRAPE_OUTPUT" | tail -2
  
  # Find the generated scan file and append to report
  SCAN_FILE=$(echo "$SCRAPE_OUTPUT" | grep -o 'workspace/artifacts/scan-[^ ]*\|artifacts/scan-[^ ]*' | head -1)
  if [ -n "$SCAN_FILE" ] && [ -f "$SCAN_FILE" ]; then
    echo "" >> "$REPORT"
    echo "## Stage 1: Market Positioning" >> "$REPORT"
    cat "$SCAN_FILE" >> "$REPORT"
  fi
else
  echo "  ⚠️ market-research-pro not installed, skipping"
fi
echo ""

# ═══════════════════════════════════════
# STAGE 2: SEO Audit — Where are they weak?
# ═══════════════════════════════════════
echo "🔍 Stage 2/5: SEO Audit (meta extraction + speed)..."
if [ -f "skills/seo-audit-pro/scripts/meta-extractor.sh" ]; then
  META_OUTPUT=$(bash skills/seo-audit-pro/scripts/meta-extractor.sh "$URL" 2>&1)
  echo "$META_OUTPUT" | grep -E "Score:|Title:|Description:" | head -5
  
  META_FILE=$(echo "$META_OUTPUT" | grep -o 'workspace/artifacts/meta-[^ ]*\|artifacts/meta-[^ ]*' | head -1)
  if [ -n "$META_FILE" ] && [ -f "$META_FILE" ]; then
    echo "" >> "$REPORT"
    echo "## Stage 2: SEO Analysis" >> "$REPORT"
    cat "$META_FILE" >> "$REPORT"
  fi
fi

if [ -f "skills/seo-audit-pro/scripts/page-speed-check.sh" ]; then
  SPEED_OUTPUT=$(bash skills/seo-audit-pro/scripts/page-speed-check.sh "$URL" 2>&1)
  echo "$SPEED_OUTPUT" | grep -E "TTFB:|Size:|avg" | head -3
  
  SPEED_FILE=$(echo "$SPEED_OUTPUT" | grep -o 'workspace/artifacts/speed-[^ ]*\|artifacts/speed-[^ ]*' | head -1)
  if [ -n "$SPEED_FILE" ] && [ -f "$SPEED_FILE" ]; then
    echo "" >> "$REPORT"
    echo "### Page Speed" >> "$REPORT"
    cat "$SPEED_FILE" >> "$REPORT"
  fi
fi
echo ""

# ═══════════════════════════════════════
# STAGE 3: GEO Audit — Are they visible to LLMs?
# ═══════════════════════════════════════
echo "🤖 Stage 3/5: AI Visibility (GEO audit)..."
if [ -f "skills/ai-visibility-pro/scripts/geo-audit.sh" ]; then
  GEO_OUTPUT=$(bash skills/ai-visibility-pro/scripts/geo-audit.sh "$URL" 2>&1)
  echo "$GEO_OUTPUT" | grep -E "Score:|Grade:" | head -2
  
  GEO_FILE=$(echo "$GEO_OUTPUT" | grep -o 'workspace/artifacts/geo-[^ ]*\|artifacts/geo-[^ ]*' | head -1)
  if [ -n "$GEO_FILE" ] && [ -f "$GEO_FILE" ]; then
    echo "" >> "$REPORT"
    echo "## Stage 3: AI Visibility (GEO)" >> "$REPORT"
    cat "$GEO_FILE" >> "$REPORT"
  fi
else
  echo "  ⚠️ ai-visibility-pro not installed, skipping"
fi
echo ""

# ═══════════════════════════════════════
# STAGE 4: ICP Generation — Who do we target?
# ═══════════════════════════════════════
echo "🎯 Stage 4/5: ICP Generation..."
if [ -f "skills/cold-outreach-pro/scripts/icp-builder.sh" ]; then
  ICP_OUTPUT=$(bash skills/cold-outreach-pro/scripts/icp-builder.sh "${DOMAIN} customer" 2>&1)
  echo "$ICP_OUTPUT" | tail -2
  
  echo "" >> "$REPORT"
  echo "## Stage 4: Ideal Customer Profile" >> "$REPORT"
  echo "ICP template generated for: ${DOMAIN} customer" >> "$REPORT"
  echo "Fill in the template, then run sequence-generator.sh to create outreach." >> "$REPORT"
fi
echo ""

# ═══════════════════════════════════════
# STAGE 5: Summary + Next Steps
# ═══════════════════════════════════════
echo "📋 Stage 5/5: Generating summary..."

cat >> "$REPORT" << 'SUMMARY'

## Stage 5: Pipeline Next Steps

### Immediate Actions
1. [ ] Review SEO weaknesses — target keywords they're missing
2. [ ] Check GEO score — if low, we can outrank them in LLM citations
3. [ ] Fill in ICP template with real customer data
4. [ ] Run sequence-generator.sh to create outreach targeting their customers
5. [ ] Monitor their X account with x-search.sh for engagement opportunities

### Competitive Advantages to Exploit
- If their GEO score < 10/19: They're invisible to AI. We can own that space.
- If their TTFB > 500ms: Speed is a ranking factor. We're faster.
- If no JSON-LD: Their products don't appear in rich results. Ours do.
- If no llms.txt: LLMs can't efficiently index them. We have both files.

### Outreach Angle
Use their weaknesses as your opening line:
"I noticed [competitor] doesn't have [specific thing]. Here's how that affects [prospect's business]..."
SUMMARY

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Full intelligence report saved: $REPORT"
echo ""
echo "Pipeline: Market Research → SEO → GEO → ICP → Next Steps"
echo "5 tools chained. 1 command. ~30 seconds."
