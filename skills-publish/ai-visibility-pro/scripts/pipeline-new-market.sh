#!/usr/bin/env bash
# New Market Entry Pipeline
# Chains: TAM Calculator → SWOT → Competitor Scraper → Keyword Planner → ICP Builder
# Usage: pipeline-new-market.sh <market_description> [competitor_url]
# Answers: "Should I enter this market, and how?"

set -uo pipefail

MARKET="${1:?Usage: pipeline-new-market.sh \"market description\" [competitor_url]}"
COMP_URL="${2:-}"
SAFE_NAME=$(echo "$MARKET" | tr ' ' '-' | tr -cd 'a-zA-Z0-9-' | head -c 40)
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"
REPORT="${WS_DIR}/artifacts/market-entry-${SAFE_NAME}-${TIMESTAMP}.md"
mkdir -p "$(dirname "$REPORT")"

echo "🎯 Running market entry analysis: ${MARKET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "$REPORT" << EOF
# Market Entry Analysis: ${MARKET}
Generated: $(date '+%Y-%m-%d %H:%M %Z')
$([ -n "$COMP_URL" ] && echo "Competitor: ${COMP_URL}")

---

EOF

cd "$WS_DIR"

# ═══════════════════════════════════════
# STAGE 1: Market Sizing
# ═══════════════════════════════════════
echo "📊 Stage 1/6: Market Sizing (TAM/SAM/SOM)..."
if [ -f "skills/market-research-pro/scripts/tam-calculator.sh" ]; then
  TAM_OUT=$(bash skills/market-research-pro/scripts/tam-calculator.sh "$MARKET" 2>&1)
  echo "  ✅ $(echo "$TAM_OUT" | head -1)"
  echo "## Stage 1: Market Sizing" >> "$REPORT"
  echo "TAM/SAM/SOM template created. Fill in with real data." >> "$REPORT"
  echo "" >> "$REPORT"
fi

# ═══════════════════════════════════════
# STAGE 2: SWOT Analysis
# ═══════════════════════════════════════
echo "📋 Stage 2/6: SWOT Analysis..."
if [ -f "skills/market-research-pro/scripts/swot-generator.sh" ]; then
  SWOT_OUT=$(bash skills/market-research-pro/scripts/swot-generator.sh "$MARKET" 2>&1)
  echo "  ✅ $(echo "$SWOT_OUT" | head -1)"
  
  SWOT_FILE=$(echo "$SWOT_OUT" | grep -o '[^ ]*swot-[^ ]*\.md' | head -1)
  if [ -n "$SWOT_FILE" ] && [ -f "$SWOT_FILE" ]; then
    echo "## Stage 2: SWOT Analysis" >> "$REPORT"
    cat "$SWOT_FILE" >> "$REPORT"
    echo "" >> "$REPORT"
  fi
fi

# ═══════════════════════════════════════
# STAGE 3: Competitor Intel (if URL provided)
# ═══════════════════════════════════════
if [ -n "$COMP_URL" ]; then
  echo "🔍 Stage 3/6: Competitor Scrape (${COMP_URL})..."
  if [ -f "skills/market-research-pro/scripts/competitor-scraper.sh" ]; then
    COMP_OUT=$(bash skills/market-research-pro/scripts/competitor-scraper.sh "$COMP_URL" 2>&1)
    echo "  ✅ $(echo "$COMP_OUT" | head -1)"
    
    COMP_FILE=$(echo "$COMP_OUT" | grep -o '[^ ]*scan-[^ ]*\.md' | head -1)
    if [ -n "$COMP_FILE" ] && [ -f "$COMP_FILE" ]; then
      echo "## Stage 3: Competitor Analysis" >> "$REPORT"
      cat "$COMP_FILE" >> "$REPORT"
      echo "" >> "$REPORT"
    fi
  fi

  # Also run SEO + GEO on competitor
  echo "  → Checking competitor SEO..."
  if [ -f "skills/seo-audit-pro/scripts/meta-extractor.sh" ]; then
    META_OUT=$(bash skills/seo-audit-pro/scripts/meta-extractor.sh "$COMP_URL" 2>&1)
    COMP_SEO=$(echo "$META_OUT" | grep -o 'Score: [0-9]*/8' | head -1)
    echo "    SEO: ${COMP_SEO:-unknown}"
  fi

  echo "  → Checking competitor AI visibility..."
  if [ -f "skills/ai-visibility-pro/scripts/geo-audit.sh" ]; then
    GEO_OUT=$(bash skills/ai-visibility-pro/scripts/geo-audit.sh "$COMP_URL" 2>&1)
    COMP_GEO=$(echo "$GEO_OUT" | grep -o 'Score: [0-9]*/19' | head -1)
    COMP_GRADE=$(echo "$GEO_OUT" | grep -o 'Grade: [A-F][+-]*' | head -1)
    echo "    GEO: ${COMP_GEO:-unknown} ${COMP_GRADE}"
    echo "## Stage 3b: Competitor GEO Score" >> "$REPORT"
    echo "SEO: ${COMP_SEO:-not checked} | GEO: ${COMP_GEO:-not checked} (${COMP_GRADE:-?})" >> "$REPORT"
    echo "" >> "$REPORT"
  fi
else
  echo "⏭️  Stage 3/6: Skipped (no competitor URL provided)"
fi
echo ""

# ═══════════════════════════════════════
# STAGE 4: Keyword Opportunities
# ═══════════════════════════════════════
echo "🔑 Stage 4/6: Keyword Research..."
if [ -f "skills/seo-audit-pro/scripts/keyword-planner.sh" ]; then
  KW_OUT=$(bash skills/seo-audit-pro/scripts/keyword-planner.sh "$MARKET" 2>&1)
  echo "  ✅ $(echo "$KW_OUT" | head -1)"
  echo "## Stage 4: Keyword Opportunities" >> "$REPORT"
  echo "Keyword plan generated. Prioritize low-competition, high-intent terms." >> "$REPORT"
  echo "" >> "$REPORT"
fi

# ═══════════════════════════════════════
# STAGE 5: Content Plan
# ═══════════════════════════════════════
echo "📝 Stage 5/6: Content Plan (GEO-optimized)..."
if [ -f "skills/ai-visibility-pro/scripts/content-planner.sh" ]; then
  CP_OUT=$(bash skills/ai-visibility-pro/scripts/content-planner.sh "$MARKET" "${WS_DIR}/artifacts/content-plan-${SAFE_NAME}.md" 2>&1)
  echo "  ✅ Content plan generated"
  echo "## Stage 5: Content Plan" >> "$REPORT"
  echo "GEO-optimized content plan generated. See: artifacts/content-plan-${SAFE_NAME}.md" >> "$REPORT"
  echo "" >> "$REPORT"
fi

# ═══════════════════════════════════════
# STAGE 6: ICP + Outreach Setup
# ═══════════════════════════════════════
echo "🎯 Stage 6/6: ICP + Outreach Setup..."
if [ -f "skills/cold-outreach-pro/scripts/icp-builder.sh" ]; then
  ICP_OUT=$(bash skills/cold-outreach-pro/scripts/icp-builder.sh "$MARKET" 2>&1)
  echo "  ✅ $(echo "$ICP_OUT" | head -1)"
  echo "## Stage 6: Ideal Customer Profile" >> "$REPORT"
  echo "ICP template generated for: $MARKET" >> "$REPORT"
  echo "Next: Fill in ICP → Run sequence-generator.sh → Start outreach" >> "$REPORT"
fi

# ═══════════════════════════════════════
# Decision Framework
# ═══════════════════════════════════════
cat >> "$REPORT" << 'DECISION'

---

## Market Entry Decision Framework

### Go if:
- [ ] TAM > $100M (or niche TAM > $10M with low competition)
- [ ] SWOT shows more opportunities than threats
- [ ] Competitor GEO score < 12/19 (you can win AI visibility)
- [ ] Keyword gaps exist (topics nobody's covering)
- [ ] ICP is specific enough to target (not "everyone")

### Don't go if:
- [ ] Market is shrinking or commoditized
- [ ] Competitors have strong SEO + GEO (hard to break in)
- [ ] No clear differentiation in your SWOT
- [ ] ICP too broad (can't write a specific first email)

### Your edge:
Fill in: What do you know/have that competitors don't?
DECISION

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Market entry analysis saved: $REPORT"
echo ""
echo "Pipeline: TAM → SWOT → Competitor Intel → Keywords → Content Plan → ICP"
echo "Should you enter this market? Check the report."
