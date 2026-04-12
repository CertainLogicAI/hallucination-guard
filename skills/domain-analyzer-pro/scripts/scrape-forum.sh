#!/usr/bin/env bash
# scrape-forum.sh — Scrape a forum for domain knowledge / fault patterns
# Usage: scrape-forum.sh <forum-url> <output-dir> [--delay 3] [--pages 60]
# Example: scrape-forum.sh "https://forum.example.com/topics/" ./data --delay 3 --pages 10
#
# Supports: XenForo, vBulletin, Discourse, phpBB, generic HTML
# Outputs: thread-urls.txt, threads/*.html, fault-patterns.jsonl
set -euo pipefail

FORUM_URL="${1:?Usage: scrape-forum.sh <forum-url> <output-dir> [--delay 3] [--pages 60]}"
OUTPUT_DIR="${2:?Provide output directory}"
DELAY=3
MAX_PAGES=60

shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --delay) DELAY="$2"; shift 2 ;;
    --pages) MAX_PAGES="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUTPUT_DIR/threads"

echo "Scraping $FORUM_URL"
echo "Delay: ${DELAY}s between requests"
echo "Max pages: $MAX_PAGES"
echo ""

# Phase 1: Collect thread URLs from listing pages
echo "Phase 1: Collecting thread URLs..."
URLS_FILE="$OUTPUT_DIR/thread-urls.txt"
> "$URLS_FILE"

for page in $(seq 1 "$MAX_PAGES"); do
  # Common pagination patterns
  PAGE_URL="${FORUM_URL}page-${page}"

  HTTP_CODE=$(curl -s -o /tmp/forum-page.html -w "%{http_code}" \
    -H "User-Agent: Mozilla/5.0 (compatible; research bot; +https://example.com)" \
    "$PAGE_URL" 2>/dev/null || echo "000")

  if [ "$HTTP_CODE" != "200" ]; then
    echo "  Page $page: HTTP $HTTP_CODE — stopping"
    break
  fi

  # Extract thread URLs (adapt pattern to forum software)
  # XenForo: <a href="/forums/threads/slug.12345/"
  # vBulletin: <a href="showthread.php?t=12345"
  # Discourse: <a href="/t/slug/12345"
  # phpBB: <a href="./viewtopic.php?t=12345"
  FOUND=$(grep -oP 'href="([^"]*threads/[^"]+|[^"]*showthread[^"]+|[^"]*viewtopic[^"]+|[^"]*\/t\/[^"]+)"' \
    /tmp/forum-page.html | grep -oP '"[^"]+"' | tr -d '"' | sort -u)

  if [ -z "$FOUND" ]; then
    echo "  Page $page: no threads found — stopping"
    break
  fi

  COUNT=$(echo "$FOUND" | wc -l)
  echo "$FOUND" >> "$URLS_FILE"
  echo "  Page $page: $COUNT threads"
  sleep "$DELAY"
done

# Deduplicate
sort -u "$URLS_FILE" -o "$URLS_FILE"
TOTAL_URLS=$(wc -l < "$URLS_FILE")
echo ""
echo "Total unique thread URLs: $TOTAL_URLS"
echo ""

# Phase 2: Download each thread
echo "Phase 2: Downloading threads..."
DOWNLOADED=0

while IFS= read -r url; do
  DOWNLOADED=$((DOWNLOADED + 1))

  # Make absolute URL if relative
  if [[ "$url" == /* ]]; then
    DOMAIN=$(echo "$FORUM_URL" | grep -oP 'https?://[^/]+')
    url="${DOMAIN}${url}"
  fi

  # Generate filename from URL slug
  SLUG=$(echo "$url" | grep -oP '[^/]+(?=/?\s*$)' | head -1 | sed 's/[^a-zA-Z0-9_-]/-/g')
  [ -z "$SLUG" ] && SLUG="thread-$DOWNLOADED"

  OUTFILE="$OUTPUT_DIR/threads/${SLUG}.html"

  if [ -f "$OUTFILE" ]; then
    # Already downloaded — skip
    if [ $((DOWNLOADED % 50)) -eq 0 ]; then
      echo "  [$DOWNLOADED/$TOTAL_URLS] Skipping (cached)"
    fi
    continue
  fi

  curl -s -o "$OUTFILE" \
    -H "User-Agent: Mozilla/5.0 (compatible; research bot; +https://example.com)" \
    "$url" 2>/dev/null

  if [ $((DOWNLOADED % 50)) -eq 0 ]; then
    echo "  [$DOWNLOADED/$TOTAL_URLS] Downloaded"
  fi

  sleep "$DELAY"
done < "$URLS_FILE"

echo ""
echo "Downloaded: $DOWNLOADED threads"
echo "Saved to: $OUTPUT_DIR/threads/"
echo ""
echo "Phase 3: Parse threads with your format-specific parser."
echo "Example: python3 parse-threads.py $OUTPUT_DIR/threads/ > $OUTPUT_DIR/fault-patterns.jsonl"
