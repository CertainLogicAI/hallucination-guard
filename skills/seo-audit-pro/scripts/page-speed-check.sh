#!/usr/bin/env bash
# Page Speed Quick Check — measures real load metrics
# Usage: ./page-speed-check.sh <url> [output-file]
# Measures: TTFB, total load time, page size, redirect count

set -uo pipefail

URL="${1:?Usage: page-speed-check.sh <url> [output-file]}"
DOMAIN=$(echo "$URL" | sed 's|https\?://||' | sed 's|/.*||')
OUTPUT="${2:-workspace/artifacts/speed-${DOMAIN}.md}"
mkdir -p "$(dirname "$OUTPUT")"

echo "⏱️ Testing page speed for $URL ..."

# Write curl format string to temp file
FORMAT_FILE=$(mktemp)
cat > "$FORMAT_FILE" << 'CURLFORMAT'
time_namelookup:  %{time_namelookup}s\n
time_connect:     %{time_connect}s\n
time_appconnect:  %{time_appconnect}s\n
time_pretransfer: %{time_pretransfer}s\n
time_redirect:    %{time_redirect}s\n
time_starttransfer: %{time_starttransfer}s\n
time_total:       %{time_total}s\n
size_download:    %{size_download} bytes\n
speed_download:   %{speed_download} bytes/s\n
http_code:        %{http_code}\n
num_redirects:    %{num_redirects}\n
CURLFORMAT

# Run the timing test (3 runs, take the median-ish)
RESULTS=""
for i in 1 2 3; do
  RESULT=$(curl -sL -o /dev/null -w "@$FORMAT_FILE" --max-time 30 -A "Mozilla/5.0 (compatible; SEOAuditBot/1.0)" "$URL" 2>/dev/null)
  RESULTS="${RESULTS}\n--- Run $i ---\n${RESULT}"
  
  # Parse this run
  eval "TTFB_$i=$(echo "$RESULT" | grep 'time_starttransfer' | awk '{print $2}' | sed 's/s//')"
  eval "TOTAL_$i=$(echo "$RESULT" | grep 'time_total' | awk '{print $2}' | sed 's/s//')"
  eval "SIZE_$i=$(echo "$RESULT" | grep 'size_download' | awk '{print $2}')"
  
  [ "$i" -lt 3 ] && sleep 1
done

rm -f "$FORMAT_FILE"

# Use run 2 as representative (warmed cache)
TTFB="$TTFB_2"
TOTAL="$TOTAL_2"
SIZE="$SIZE_2"
HTTP_CODE=$(echo -e "$RESULTS" | grep 'http_code' | tail -1 | awk '{print $2}')
REDIRECTS=$(echo -e "$RESULTS" | grep 'num_redirects' | tail -1 | awk '{print $2}')
DNS=$(echo -e "$RESULTS" | grep 'time_namelookup' | tail -1 | awk '{print $2}' | sed 's/s//')
CONNECT=$(echo -e "$RESULTS" | grep 'time_connect' | tail -1 | awk '{print $2}' | sed 's/s//')
TLS=$(echo -e "$RESULTS" | grep 'time_appconnect' | tail -1 | awk '{print $2}' | sed 's/s//')

# Convert size to human readable
SIZE_KB=$(echo "scale=1; $SIZE / 1024" | bc 2>/dev/null || echo "$SIZE")
SIZE_MB=$(echo "scale=2; $SIZE / 1048576" | bc 2>/dev/null || echo "?")

# Score TTFB
TTFB_MS=$(echo "$TTFB * 1000" | bc 2>/dev/null | sed 's/\..*//' || echo "?")
if [ "$TTFB_MS" != "?" ]; then
  if [ "$TTFB_MS" -lt 200 ]; then TTFB_GRADE="🟢 Excellent"
  elif [ "$TTFB_MS" -lt 500 ]; then TTFB_GRADE="🟢 Good"
  elif [ "$TTFB_MS" -lt 800 ]; then TTFB_GRADE="🟡 Needs work"
  else TTFB_GRADE="🔴 Slow"
  fi
else
  TTFB_GRADE="?"
fi

# Score total time
TOTAL_MS=$(echo "$TOTAL * 1000" | bc 2>/dev/null | sed 's/\..*//' || echo "?")
if [ "$TOTAL_MS" != "?" ]; then
  if [ "$TOTAL_MS" -lt 1000 ]; then TOTAL_GRADE="🟢 Fast"
  elif [ "$TOTAL_MS" -lt 2500 ]; then TOTAL_GRADE="🟢 Acceptable"
  elif [ "$TOTAL_MS" -lt 4000 ]; then TOTAL_GRADE="🟡 Slow"
  else TOTAL_GRADE="🔴 Very slow"
  fi
else
  TOTAL_GRADE="?"
fi

# Score page size
if [ "$SIZE" -lt 500000 ]; then SIZE_GRADE="🟢 Light"
elif [ "$SIZE" -lt 1500000 ]; then SIZE_GRADE="🟡 Medium"
elif [ "$SIZE" -lt 3000000 ]; then SIZE_GRADE="🟠 Heavy"
else SIZE_GRADE="🔴 Bloated"
fi

cat > "$OUTPUT" << REPORT
# Page Speed Report: $DOMAIN
**URL:** $URL
**Tested:** $(date +%Y-%m-%d\ %H:%M)
**HTTP Status:** $HTTP_CODE
**Redirects:** $REDIRECTS

---

## Key Metrics

| Metric | Value | Target | Grade |
|--------|-------|--------|-------|
| **TTFB** | ${TTFB_MS}ms | <800ms | $TTFB_GRADE |
| **Total Load** | ${TOTAL_MS}ms | <2500ms | $TOTAL_GRADE |
| **Page Size** | ${SIZE_KB}KB (${SIZE_MB}MB) | <3MB | $SIZE_GRADE |

## Connection Breakdown

| Phase | Time |
|-------|------|
| DNS Lookup | ${DNS}s |
| TCP Connect | ${CONNECT}s |
| TLS Handshake | ${TLS}s |
| TTFB (server response) | ${TTFB}s |
| Content Transfer | $(echo "$TOTAL - $TTFB" | bc 2>/dev/null || echo "?")s |
| **Total** | **${TOTAL}s** |

## 3-Run Comparison

| Run | TTFB | Total |
|-----|------|-------|
| 1 (cold) | ${TTFB_1}s | ${TOTAL_1}s |
| 2 (warm) | ${TTFB_2}s | ${TOTAL_2}s |
| 3 (warm) | ${TTFB_3}s | ${TOTAL_3}s |

## Recommendations

$([ "$TTFB_MS" != "?" ] && [ "$TTFB_MS" -ge 800 ] && echo "### 🔴 Fix TTFB (${TTFB_MS}ms)
- Enable server-side caching
- Use a CDN (Cloudflare, Fastly)
- Optimize database queries
- Consider edge computing / SSG
")
$([ "$TOTAL_MS" != "?" ] && [ "$TOTAL_MS" -ge 2500 ] && echo "### 🟡 Reduce Total Load Time (${TOTAL_MS}ms)
- Compress images (WebP)
- Minify CSS/JS
- Defer non-critical JavaScript
- Enable HTTP/2
- Lazy load below-fold content
")
$([ "$SIZE" -ge 1500000 ] && echo "### 🟡 Reduce Page Size (${SIZE_KB}KB)
- Compress images
- Remove unused CSS/JS
- Enable gzip/brotli compression
- Audit third-party scripts
")
$([ "$REDIRECTS" -ge 2 ] && echo "### ⚠️ Redirect Chain ($REDIRECTS redirects)
- Update links to point to final URL
- Aim for max 1 redirect hop
")
$([ "$TTFB_MS" != "?" ] && [ "$TTFB_MS" -lt 800 ] && [ "$TOTAL_MS" != "?" ] && [ "$TOTAL_MS" -lt 2500 ] && [ "$SIZE" -lt 1500000 ] && echo "### ✅ Looking good!
Server response and page size are within targets. Focus on Core Web Vitals (LCP, INP, CLS) for further optimization — those require browser-based testing.
")

---

*Note: These are server-side metrics (HTML document only). Full page performance including images, JS, CSS requires browser-based testing (PageSpeed Insights, WebPageTest).*

---
Generated by SEO Audit Pro — Page Speed Check
REPORT

echo "✅ Speed report saved: $OUTPUT"
echo "TTFB: ${TTFB_MS}ms ($TTFB_GRADE) | Total: ${TOTAL_MS}ms | Size: ${SIZE_KB}KB"
