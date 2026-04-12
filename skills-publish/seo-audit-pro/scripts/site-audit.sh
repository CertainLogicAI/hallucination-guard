#!/usr/bin/env bash
# Site SEO Audit Generator
# Creates a structured audit template pre-filled with checkpoints
# Usage: ./site-audit.sh <domain> <output-file>

set -uo pipefail

DOMAIN="${1:?Usage: site-audit.sh <domain> [output-file]}"
DOMAIN_CLEAN=$(echo "$DOMAIN" | sed 's|https\?://||' | sed 's|/.*||')
OUTPUT="${2:-workspace/artifacts/seo-audit-${DOMAIN_CLEAN}.md}"
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" << TEMPLATE
# SEO Audit: $DOMAIN_CLEAN
**Date:** $(date +%Y-%m-%d)
**Auditor:** AI Agent

---

## 1. Technical SEO

### Crawlability
- [ ] robots.txt exists and is valid → \`$DOMAIN_CLEAN/robots.txt\`
- [ ] XML sitemap exists and is linked in robots.txt → \`$DOMAIN_CLEAN/sitemap.xml\`
- [ ] No critical pages blocked by robots.txt
- [ ] Site loads without JavaScript (SSR/SSG check)
- [ ] No orphan pages (pages not linked from anywhere)
- [ ] Redirect chains under 3 hops
- [ ] No redirect loops
- [ ] 404 page returns proper 404 status code

### Performance (Core Web Vitals)
- [ ] **LCP** (Largest Contentful Paint): < 2.5s → Actual: ___s
- [ ] **INP** (Interaction to Next Paint): < 200ms → Actual: ___ms
- [ ] **CLS** (Cumulative Layout Shift): < 0.1 → Actual: ___
- [ ] Page size under 3MB → Actual: ___MB
- [ ] Time to First Byte (TTFB): < 800ms → Actual: ___ms

### Security & Infrastructure
- [ ] HTTPS enabled (no mixed content)
- [ ] HTTP → HTTPS redirect works
- [ ] www → non-www (or vice versa) canonicalized
- [ ] SSL certificate valid and not expiring soon

### Mobile
- [ ] Viewport meta tag present
- [ ] Responsive design (no horizontal scroll on mobile)
- [ ] Touch targets > 48px
- [ ] Font size > 16px on mobile
- [ ] No intrusive interstitials

---

## 2. On-Page SEO

### Homepage
- [ ] Title tag: present, under 60 chars, includes primary keyword
  - Current: \`\`
- [ ] Meta description: present, under 160 chars, compelling CTA
  - Current: \`\`
- [ ] H1 tag: exactly one, includes primary keyword
  - Current: \`\`
- [ ] Canonical URL set correctly
- [ ] Open Graph tags (og:title, og:description, og:image)
- [ ] Twitter Card tags

### Content Pages (check top 5 pages)
| Page | Title | H1 | Meta Desc | Word Count | Target Keyword |
|------|-------|----|-----------|------------|----------------|
| / | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

### Common Issues
- [ ] No duplicate title tags across pages
- [ ] No duplicate meta descriptions
- [ ] No missing alt text on images
- [ ] No broken internal links
- [ ] No keyword stuffing (natural language)
- [ ] Heading hierarchy is logical (H1 → H2 → H3, no skips)

---

## 3. Content Quality

### E-E-A-T Signals
- [ ] Author bios with credentials on content pages
- [ ] About page with company/team info
- [ ] Contact page with real contact info
- [ ] Privacy policy and terms of service
- [ ] External citations to authoritative sources
- [ ] Original research, data, or unique insights

### Content Assessment
- [ ] Content matches search intent for target keywords
- [ ] Primary question answered in first 100 words
- [ ] FAQ section for "People Also Ask" queries
- [ ] Content depth: comprehensive coverage of topic
- [ ] Internal links to related content
- [ ] Updated date visible on time-sensitive content

---

## 4. Keywords

### Current Rankings (check manually or with tool)
| Keyword | Current Position | Search Volume | Difficulty | Page |
|---------|-----------------|---------------|------------|------|
| | | | | |
| | | | | |
| | | | | |

### Keyword Gaps (competitors rank, you don't)
| Keyword | Competitor | Their Position | Opportunity |
|---------|-----------|----------------|-------------|
| | | | |
| | | | |

### Quick Wins (positions 4-20, improve with optimization)
| Keyword | Current Position | Page | Action Needed |
|---------|-----------------|------|---------------|
| | | | |
| | | | |

---

## 5. Links

### Internal Linking
- [ ] Every page reachable within 3 clicks from homepage
- [ ] Logical link hierarchy (pillar → cluster pages)
- [ ] Anchor text descriptive (not "click here")
- [ ] No broken internal links

### Backlink Profile
- Referring domains: ___
- Toxic/spammy links: ___
- Highest authority backlinks:
  1.
  2.
  3.
- Missing backlinks (competitors have, you don't):
  1.
  2.

---

## 6. Local SEO (if applicable)
- [ ] Google Business Profile claimed and verified
- [ ] NAP (Name, Address, Phone) consistent across web
- [ ] Local keywords in title tags and content
- [ ] Reviews: ___ total, ___ avg rating
- [ ] Responding to reviews (positive and negative)
- [ ] Local schema markup (LocalBusiness)

---

## 7. Schema Markup
- [ ] Organization schema on homepage
- [ ] Breadcrumb schema on content pages
- [ ] Article schema on blog posts
- [ ] Product schema on product pages (if applicable)
- [ ] FAQ schema on FAQ sections
- [ ] Review/Rating schema where applicable
- Validate at: https://search.google.com/test/rich-results

---

## Priority Actions

### 🔴 Critical (fix this week)
1.
2.
3.

### 🟡 Important (fix this month)
1.
2.
3.

### 🟢 Nice to Have (backlog)
1.
2.
3.

---

## Score Summary

| Category | Score | Notes |
|----------|-------|-------|
| Technical SEO | /10 | |
| On-Page SEO | /10 | |
| Content Quality | /10 | |
| Keywords | /10 | |
| Links | /10 | |
| Local SEO | /10 | |
| Schema | /10 | |
| **TOTAL** | **/70** | |

| Score Range | Rating |
|-------------|--------|
| 60-70 | Excellent — minor tweaks |
| 45-59 | Good — targeted improvements needed |
| 30-44 | Needs work — prioritize critical fixes |
| <30 | Major overhaul required |

---
Generated by SEO Audit Pro
TEMPLATE

echo "✅ SEO audit template created: $OUTPUT"
echo "Run the audit by checking each item against the live site."
