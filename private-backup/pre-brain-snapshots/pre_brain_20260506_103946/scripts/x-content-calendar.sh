#!/usr/bin/env bash
# X Content Calendar Generator — HSCR Framework
# Generates a week of pre-filled tweet drafts based on the 5-type rotation
# Usage: x-content-calendar.sh [topic] [week_number]
# Example: x-content-calendar.sh "AI agent tools" 2

set -uo pipefail

TOPIC="${1:-AI agent automation}"
WEEK="${2:-1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="${WS_DIR}/artifacts/x-calendar-week-${WEEK}.md"
mkdir -p "$(dirname "$OUTPUT")"
DATE=$(date +%Y-%m-%d)

cat > "$OUTPUT" << EOF
# X Content Calendar — Week ${WEEK}
Generated: ${DATE}
Topic Focus: ${TOPIC}
Framework: HSCR (Hook → Story → CTA → Repeat)

---

## Schedule
| Day | Type | Time (EST) | Status |
|-----|------|-----------|--------|
| Mon | 🪝 Hook | 9:00 AM | ⬜ |
| Tue | 📊 Proof | 9:00 AM | ⬜ |
| Wed | 💡 Lesson | 12:00 PM | ⬜ |
| Thu | 🧵 Thread | 9:00 AM | ⬜ |
| Fri | 💬 Engagement | 5:00 PM | ⬜ |
| Sat | 📊 Recap | 10:00 AM | ⬜ |

---

## MON 🪝 Hook Tweet
**Goal:** Stop the scroll. Curiosity gap.
**Pattern:** [Surprising claim] + [Unexpected twist]
**Rules:** Front-load hook in first 50 chars. No links. Under 280 chars.

**Main tweet:**
\`\`\`
[HOOK — Write a tweet using one of these patterns:
  "I [did X] and [unexpected result]."
  "[Number] [things] that [audience] gets wrong about [topic]."
  "Most people [common approach]. The ones making money [contrarian approach]."]
\`\`\`

**Reply tweet (optional — add detail or link):**
\`\`\`
[REPLY — Expand on the hook. Link goes here if needed.]
\`\`\`

---

## TUE 📊 Proof Tweet
**Goal:** Build credibility through evidence. Real output > claims.
**Pattern:** Run a real tool → paste output → one-line insight
**Rules:** Terminal output > marketing copy. Numbers > adjectives.

**Action:** Run one of these and paste the output:
- \`security-scan.sh\` on a popular skill
- \`geo-audit.sh\` on a website
- \`meta-extractor.sh\` on a competitor
- \`page-speed-check.sh\` on our site
- \`tam-calculator.sh\` on a market

**Main tweet:**
\`\`\`
[PROOF — Paste real tool output + one-line insight. Example:
  "Ran our GEO audit on [site]:
   llms.txt: ❌ missing
   JSON-LD: ❌ missing
   Score: 5/19 — Grade F
   This site is invisible to ChatGPT and Perplexity."]
\`\`\`

---

## WED 💡 Lesson Tweet
**Goal:** Share a build-in-public insight. Gets bookmarked.
**Pattern:** What happened → Why it matters → What I'd do differently
**Rules:** Be specific (name the tool, cost, time). Vulnerability > perfection.

**Main tweet:**
\`\`\`
[LESSON — Write using this format:
  "Lesson from this week:
   [What happened — specific]
   [Why it matters — the principle]
   [What I'd do differently — actionable]
   Would've saved me [time/money]."]
\`\`\`

---

## THU 🧵 Thread (4 tweets)
**Goal:** Deep dive. 3-5x impressions of single tweets.
**Pattern:** Hook → Point 1 → Point 2 → TL;DR + CTA
**Rules:** Every tweet stands alone. Number points. Link only in final tweet.

**Tweet 1 — Hook (80% of thread's success):**
\`\`\`
[HOOK — Who is this for? What do they get? Must grab in 1.5 seconds.
  Pattern: "[Surprising stat]. [Twist]. Here's [what they get]:"]
\`\`\`

**Tweet 2 — Point 1:**
\`\`\`
[POINT — One key idea. Must work as a standalone tweet.
  Include a specific number or proof point.]
\`\`\`

**Tweet 3 — Point 2:**
\`\`\`
[POINT — Second key idea. Real example > abstract advice.
  Show before/after or contrast.]
\`\`\`

**Tweet 4 — TL;DR + CTA:**
\`\`\`
[SUMMARY — "TL;DR:" + 3-4 bullet points + one CTA.
  Link goes here (only place in thread).
  End with "Follow for more [topic]" or link.]
\`\`\`

---

## FRI 💬 Engagement Tweet
**Goal:** Generate replies. Replies = #1 algorithm signal.
**Pattern:** Question or controversial take that invites responses
**Rules:** "I'll go first" gets more replies. Stay in replies 30 min after posting.

**Main tweet:**
\`\`\`
[ENGAGEMENT — Use one of these patterns:
  "Hot take: [opinion]. Change my mind."
  "What's the first thing you [verb]? I'll go first: [answer]"
  "Unpopular opinion: [take]. Here's why:"]
\`\`\`

---

## SAT 📊 Weekly Recap
**Goal:** Build-in-public accountability. Honesty > impressive stats.
**Pattern:** "This week in numbers" + one-line reflection
**Rules:** Real numbers only. \$0 revenue is fine. Include what didn't work.

**Main tweet:**
\`\`\`
Week ${WEEK} numbers:

🐦 Impressions: [check X analytics]
💬 Replies: [count]
👀 Site visits: [check analytics badge]
💰 Revenue: [real number]
📦 Free downloads: [count]
🔥 Best performer: [which tweet/post]

[One-line honest reflection]
\`\`\`

---

## Post-Tweet Checklist
- [ ] Reply to every comment in first 60 minutes
- [ ] Quote-tweet best thread 2-3 days later with new hook
- [ ] Check engagement rate (target: 2-5%)
- [ ] Log results in memory/$(date +%Y-%m-%d).md
EOF

echo "✅ Content calendar created: $OUTPUT"
echo "Topic: ${TOPIC}"
echo "Framework: HSCR — 5-type rotation + weekly recap"
echo "Fill in the code blocks with real content, then schedule via cron."
