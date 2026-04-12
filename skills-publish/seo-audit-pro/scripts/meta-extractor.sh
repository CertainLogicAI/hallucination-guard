#!/usr/bin/env bash
# Meta Tag Extractor — Pull SEO-critical tags from any URL
# Usage: ./meta-extractor.sh <url> [output-file]
# Checks: title, description, H1, canonical, OG tags, schema, robots, viewport

set -uo pipefail

URL="${1:?Usage: meta-extractor.sh <url> [output-file]}"
DOMAIN=$(echo "$URL" | sed 's|https\?://||' | sed 's|/.*||')
OUTPUT="${2:-workspace/artifacts/meta-${DOMAIN}.md}"
mkdir -p "$(dirname "$OUTPUT")"

echo "🔍 Extracting meta tags from $URL ..."

HTML=$(curl -sL --max-time 15 -A "Mozilla/5.0 (compatible; SEOAuditBot/1.0)" "$URL" 2>/dev/null || echo "")

if [ -z "$HTML" ]; then
  echo "❌ Could not fetch $URL"
  exit 1
fi

# --- Extract everything ---
TITLE=$(echo "$HTML" | grep -oi '<title>[^<]*</title>' | head -1 | sed 's/<[^>]*>//g' | xargs)
TITLE_LEN=${#TITLE}

META_DESC=$(echo "$HTML" | grep -oi 'meta[^>]*name="description"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')
[ -z "$META_DESC" ] && META_DESC=$(echo "$HTML" | grep -oi 'meta[^>]*content="[^"]*"[^>]*name="description"' | head -1 | sed 's/.*content="//;s/".*//')
DESC_LEN=${#META_DESC}

H1=$(echo "$HTML" | grep -oi '<h1[^>]*>[^<]*</h1>' | head -1 | sed 's/<[^>]*>//g' | xargs)
H1_COUNT=$(echo "$HTML" | grep -oi '<h1' | wc -l)
H2_COUNT=$(echo "$HTML" | grep -oi '<h2' | wc -l)
H3_COUNT=$(echo "$HTML" | grep -oi '<h3' | wc -l)

CANONICAL=$(echo "$HTML" | grep -oi 'link[^>]*rel="canonical"[^>]*href="[^"]*"' | head -1 | sed 's/.*href="//;s/".*//')

ROBOTS=$(echo "$HTML" | grep -oi 'meta[^>]*name="robots"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')

VIEWPORT=$(echo "$HTML" | grep -oi 'meta[^>]*name="viewport"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')

OG_TITLE=$(echo "$HTML" | grep -oi 'meta[^>]*property="og:title"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')
OG_DESC=$(echo "$HTML" | grep -oi 'meta[^>]*property="og:description"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')
OG_IMAGE=$(echo "$HTML" | grep -oi 'meta[^>]*property="og:image"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')
OG_TYPE=$(echo "$HTML" | grep -oi 'meta[^>]*property="og:type"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')

TW_CARD=$(echo "$HTML" | grep -oi 'meta[^>]*name="twitter:card"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')
TW_TITLE=$(echo "$HTML" | grep -oi 'meta[^>]*name="twitter:title"[^>]*content="[^"]*"' | head -1 | sed 's/.*content="//;s/".*//')

HAS_SCHEMA="No"
echo "$HTML" | grep -qi "application/ld+json" && HAS_SCHEMA="Yes"
SCHEMA_TYPES=$(echo "$HTML" | grep -oP '"@type"\s*:\s*"[^"]*"' | sed 's/.*"@type"\s*:\s*"//;s/".*//' | sort -u | tr '\n' ', ' | sed 's/, $//')

HAS_SITEMAP="Unknown"
ROBOTS_TXT=$(curl -sL --max-time 5 "https://$DOMAIN/robots.txt" 2>/dev/null || echo "")
echo "$ROBOTS_TXT" | grep -qi "sitemap" && HAS_SITEMAP="Yes (referenced in robots.txt)"

IMG_NO_ALT=$(echo "$HTML" | grep -oi '<img[^>]*>' | grep -cv 'alt="[^"]\+' 2>/dev/null || echo "0")
TOTAL_IMGS=$(echo "$HTML" | grep -oi '<img' | wc -l)

# --- Score it ---
SCORE=0
ISSUES=""

# Title
if [ -n "$TITLE" ] && [ "$TITLE_LEN" -le 60 ]; then
  SCORE=$((SCORE + 1))
elif [ -n "$TITLE" ]; then
  ISSUES="${ISSUES}\n⚠️ Title too long (${TITLE_LEN} chars, target ≤60)"
else
  ISSUES="${ISSUES}\n🔴 Missing title tag"
fi

# Meta description
if [ -n "$META_DESC" ] && [ "$DESC_LEN" -le 160 ]; then
  SCORE=$((SCORE + 1))
elif [ -n "$META_DESC" ]; then
  ISSUES="${ISSUES}\n⚠️ Meta description too long (${DESC_LEN} chars, target ≤160)"
else
  ISSUES="${ISSUES}\n🔴 Missing meta description"
fi

# H1
if [ "$H1_COUNT" -eq 1 ]; then
  SCORE=$((SCORE + 1))
elif [ "$H1_COUNT" -eq 0 ]; then
  ISSUES="${ISSUES}\n🔴 No H1 tag found"
else
  ISSUES="${ISSUES}\n⚠️ Multiple H1 tags found ($H1_COUNT)"
fi

# Canonical
[ -n "$CANONICAL" ] && SCORE=$((SCORE + 1)) || ISSUES="${ISSUES}\n⚠️ No canonical URL set"

# OG tags
[ -n "$OG_TITLE" ] && [ -n "$OG_DESC" ] && [ -n "$OG_IMAGE" ] && SCORE=$((SCORE + 1)) || ISSUES="${ISSUES}\n⚠️ Incomplete Open Graph tags"

# Twitter card
[ -n "$TW_CARD" ] && SCORE=$((SCORE + 1)) || ISSUES="${ISSUES}\n⚠️ No Twitter Card meta tags"

# Schema
[ "$HAS_SCHEMA" = "Yes" ] && SCORE=$((SCORE + 1)) || ISSUES="${ISSUES}\n⚠️ No structured data (JSON-LD)"

# Viewport (mobile)
[ -n "$VIEWPORT" ] && SCORE=$((SCORE + 1)) || ISSUES="${ISSUES}\n🔴 No viewport meta tag (mobile broken)"

cat > "$OUTPUT" << REPORT
# Meta Tag Audit: $DOMAIN
**URL:** $URL
**Scanned:** $(date +%Y-%m-%d\ %H:%M)
**Quick Score:** $SCORE/8

---

## Core SEO Tags

| Tag | Value | Status |
|-----|-------|--------|
| **Title** | \`${TITLE:-MISSING}\` | ${TITLE_LEN} chars $([ "$TITLE_LEN" -le 60 ] && echo "✅" || echo "⚠️ >60") |
| **Meta Description** | \`${META_DESC:-MISSING}\` | ${DESC_LEN} chars $([ "$DESC_LEN" -le 160 ] && echo "✅" || echo "⚠️ >160") |
| **H1** | \`${H1:-MISSING}\` | $H1_COUNT found $([ "$H1_COUNT" -eq 1 ] && echo "✅" || echo "⚠️") |
| **Canonical** | \`${CANONICAL:-NOT SET}\` | $([ -n "$CANONICAL" ] && echo "✅" || echo "⚠️") |
| **Robots** | \`${ROBOTS:-NOT SET}\` | — |

## Heading Structure
- H1: $H1_COUNT
- H2: $H2_COUNT
- H3: $H3_COUNT

## Open Graph
| Tag | Value |
|-----|-------|
| og:title | \`${OG_TITLE:-NOT SET}\` |
| og:description | \`${OG_DESC:-NOT SET}\` |
| og:image | \`${OG_IMAGE:-NOT SET}\` |
| og:type | \`${OG_TYPE:-NOT SET}\` |

## Twitter Card
| Tag | Value |
|-----|-------|
| twitter:card | \`${TW_CARD:-NOT SET}\` |
| twitter:title | \`${TW_TITLE:-NOT SET}\` |

## Technical
| Check | Result |
|-------|--------|
| Viewport | $([ -n "$VIEWPORT" ] && echo "✅ Set" || echo "🔴 Missing") |
| Schema/JSON-LD | $([ "$HAS_SCHEMA" = "Yes" ] && echo "✅ Found: $SCHEMA_TYPES" || echo "⚠️ None") |
| Sitemap | $HAS_SITEMAP |
| Images without alt | $IMG_NO_ALT of $TOTAL_IMGS |

## Issues Found
$(echo -e "$ISSUES" | grep -v "^$" || echo "✅ No issues — looking good!")

---
Generated by SEO Audit Pro — Meta Extractor
REPORT

echo "✅ Meta audit saved: $OUTPUT"
echo "Score: $SCORE/8 — $([ "$SCORE" -ge 7 ] && echo "Excellent" || ([ "$SCORE" -ge 5 ] && echo "Decent, fix the gaps" || echo "Needs work"))"
