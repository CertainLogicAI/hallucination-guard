#!/usr/bin/env bash
# Site Launch Audit Pipeline
# Chains: SEO Audit → GEO Audit → LLMs.txt Generator → Content Planner
# Usage: pipeline-site-launch.sh <your_site_url>
# Answers: "Is my site ready for both Google AND AI search?"

set -uo pipefail

URL="${1:?Usage: pipeline-site-launch.sh <your_site_url>}"
DOMAIN=$(echo "$URL" | sed 's|https\?://||;s|/.*||')
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"
REPORT="${WS_DIR}/artifacts/launch-audit-${DOMAIN}-${TIMESTAMP}.md"
mkdir -p "$(dirname "$REPORT")"

echo "🚀 Running site launch audit on ${URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "$REPORT" << EOF
# Site Launch Audit: ${DOMAIN}
Generated: $(date '+%Y-%m-%d %H:%M %Z')
Target: ${URL}

---

EOF

cd "$WS_DIR"

# ═══════════════════════════════════════
# STAGE 1: SEO Health Check
# ═══════════════════════════════════════
echo "🔍 Stage 1/5: SEO — Meta tags..."
SEO_SCORE="?"
if [ -f "skills/seo-audit-pro/scripts/meta-extractor.sh" ]; then
  META_OUT=$(bash skills/seo-audit-pro/scripts/meta-extractor.sh "$URL" 2>&1)
  SEO_SCORE=$(echo "$META_OUT" | grep -o 'Score: [0-9]*/8' | head -1)
  echo "  ${SEO_SCORE:-No score}"
  
  META_FILE=$(echo "$META_OUT" | grep -o '[^ ]*meta-[^ ]*\.md' | head -1)
  if [ -n "$META_FILE" ] && [ -f "$META_FILE" ]; then
    echo "## Stage 1: SEO Meta Tags" >> "$REPORT"
    cat "$META_FILE" >> "$REPORT"
    echo "" >> "$REPORT"
  fi
fi

# ═══════════════════════════════════════
# STAGE 2: Page Speed
# ═══════════════════════════════════════
echo "⚡ Stage 2/5: Page Speed..."
if [ -f "skills/seo-audit-pro/scripts/page-speed-check.sh" ]; then
  SPEED_OUT=$(bash skills/seo-audit-pro/scripts/page-speed-check.sh "$URL" 2>&1)
  echo "$SPEED_OUT" | grep -E "TTFB:|Size:" | head -2
  
  SPEED_FILE=$(echo "$SPEED_OUT" | grep -o '[^ ]*speed-[^ ]*\.md' | head -1)
  if [ -n "$SPEED_FILE" ] && [ -f "$SPEED_FILE" ]; then
    echo "## Stage 2: Page Speed" >> "$REPORT"
    cat "$SPEED_FILE" >> "$REPORT"
    echo "" >> "$REPORT"
  fi
fi

# ═══════════════════════════════════════
# STAGE 3: AI Visibility (GEO)
# ═══════════════════════════════════════
echo "🤖 Stage 3/5: AI Visibility (GEO audit)..."
GEO_SCORE="?"
if [ -f "skills/ai-visibility-pro/scripts/geo-audit.sh" ]; then
  GEO_OUT=$(bash skills/ai-visibility-pro/scripts/geo-audit.sh "$URL" 2>&1)
  GEO_SCORE=$(echo "$GEO_OUT" | grep -o 'Score: [0-9]*/19' | head -1)
  GEO_GRADE=$(echo "$GEO_OUT" | grep -o 'Grade: [A-F][+-]*' | head -1)
  echo "  ${GEO_SCORE:-No score} — ${GEO_GRADE:-No grade}"
  
  GEO_FILE=$(echo "$GEO_OUT" | grep -o '[^ ]*geo-[^ ]*\.md' | head -1)
  if [ -n "$GEO_FILE" ] && [ -f "$GEO_FILE" ]; then
    echo "## Stage 3: AI Visibility (GEO)" >> "$REPORT"
    cat "$GEO_FILE" >> "$REPORT"
    echo "" >> "$REPORT"
  fi
fi

# ═══════════════════════════════════════
# STAGE 4: Generate missing llms.txt
# ═══════════════════════════════════════
echo "📄 Stage 4/5: Checking llms.txt..."
LLMS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/llms.txt" 2>/dev/null)
if [ "$LLMS_STATUS" = "200" ]; then
  echo "  ✅ llms.txt exists"
  echo "## Stage 4: llms.txt" >> "$REPORT"
  echo "✅ Already exists at ${URL}/llms.txt" >> "$REPORT"
else
  echo "  ❌ Missing — generating template"
  if [ -f "skills/ai-visibility-pro/scripts/llms-txt-generator.sh" ]; then
    LLMS_OUT=$(bash skills/ai-visibility-pro/scripts/llms-txt-generator.sh "$DOMAIN" "Website for ${DOMAIN}" 2>&1)
    echo "  ${LLMS_OUT}" | tail -2
    echo "## Stage 4: llms.txt" >> "$REPORT"
    echo "❌ Missing. Template generated — deploy to your site root." >> "$REPORT"
  fi
fi
echo ""

# ═══════════════════════════════════════
# STAGE 5: Content Plan for Gaps
# ═══════════════════════════════════════
echo "📝 Stage 5/5: Content plan for gaps..."
if [ -f "skills/ai-visibility-pro/scripts/content-planner.sh" ]; then
  CONTENT_OUT=$(bash skills/ai-visibility-pro/scripts/content-planner.sh "$DOMAIN" "${WS_DIR}/artifacts/content-plan-${DOMAIN}.md" 2>&1)
  echo "  ✅ Content plan generated"
  echo "" >> "$REPORT"
  echo "## Stage 5: Content Plan" >> "$REPORT"
  echo "Content plan saved to: artifacts/content-plan-${DOMAIN}.md" >> "$REPORT"
  echo "Prioritize articles that fill GEO gaps (FAQ, how-to, comparison)." >> "$REPORT"
fi

# ═══════════════════════════════════════
# Summary
# ═══════════════════════════════════════
cat >> "$REPORT" << EOF

---

## Launch Readiness Summary

| Check | Status |
|-------|--------|
| SEO Meta Tags | ${SEO_SCORE:-Not checked} |
| Page Speed | Checked (see above) |
| AI Visibility | ${GEO_SCORE:-Not checked} |
| llms.txt | $([ "$LLMS_STATUS" = "200" ] && echo "✅ Exists" || echo "❌ Missing") |
| Content Plan | Generated |

### Priority Fixes
1. Fix any SEO issues scoring below 7/8
2. Add llms.txt if missing (template generated above)
3. Target GEO score of 15+/19 before announcing
4. Publish 2-3 FAQ/how-to posts for LLM citation
5. Submit sitemap to Google Search Console + Bing Webmaster
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Launch audit saved: $REPORT"
echo ""
echo "Pipeline: SEO → Speed → GEO → llms.txt → Content Plan"
echo "Is your site ready for Google AND AI search? Check the report."
