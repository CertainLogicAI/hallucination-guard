---
summary: "\"Technical SEO Fixes\""
read_when: ["["skill"]"]
---
# Technical SEO Fixes

Quick reference for the most common technical SEO issues and how to fix them.

## Critical Fixes (do first)

### Slow Page Speed
**Diagnose:** Google PageSpeed Insights, WebPageTest
**Common causes and fixes:**

| Issue | Fix |
|-------|-----|
| Large images | Compress with WebP, use srcset for responsive sizes |
| Unminified CSS/JS | Minify and bundle, defer non-critical JS |
| No caching | Set Cache-Control headers (static: 1 year, HTML: short/no-cache) |
| Too many requests | Combine files, use HTTP/2, remove unused scripts |
| No CDN | CloudFlare, Fastly, or provider CDN |
| Large fonts | Subset fonts, use font-display: swap, limit to 2-3 fonts |
| Render-blocking JS | Add defer or async, move to bottom of body |

### Broken Pages (4xx/5xx)
**Diagnose:** Google Search Console → Coverage, or crawl with Screaming Frog
**Fix:** 
- 404s with backlinks → 301 redirect to most relevant page
- 404s without traffic → delete from sitemap, let them 404
- 5xx → server issue, check logs

### Missing/Duplicate Meta Tags
**Diagnose:** Crawl site, check for duplicate titles/descriptions
**Fix:**
- Every page gets a unique title and description
- Canonical tags on all pages (self-referencing)
- Canonical on duplicates pointing to the original

## Important Fixes (do this month)

### Redirect Chains
**Diagnose:** Follow redirect paths, check for A→B→C→D
**Fix:** Update all links to point to final destination. Max 1 redirect hop.

### Mobile Usability
**Diagnose:** Google Mobile-Friendly Test, Chrome DevTools device mode
**Common fixes:**
- Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Touch targets: minimum 48×48px with 8px spacing
- Font size: minimum 16px on mobile
- No horizontal scrolling

### Indexation Issues
**Diagnose:** `site:yourdomain.com` in Google, check Search Console
**Common issues:**

| Problem | Cause | Fix |
|---------|-------|-----|
| Pages not indexed | noindex tag, robots.txt block, no links | Remove block, add internal links |
| Wrong pages indexed | Thin/duplicate content indexed | noindex or canonical to better page |
| Too many pages indexed | Parameter URLs, faceted navigation | Canonical tags, parameter handling in GSC |

### Schema Markup
**Priority order:**
1. Organization (homepage) — establishes entity
2. BreadcrumbList (all pages) — navigation in SERPs
3. Article (blog) — date, author in SERPs
4. FAQ (FAQ sections) — expandable answers in SERPs
5. Product (product pages) — price, availability, reviews
6. LocalBusiness (local) — map pack eligibility

**Validate:** https://search.google.com/test/rich-results

### XML Sitemap
**Requirements:**
- Under 50MB / 50,000 URLs per sitemap
- Only canonical, indexable pages
- Updated when content changes
- Referenced in robots.txt
- Submitted in Google Search Console

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2025-01-15</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
```

## Link Building Tactics

### High-Value (worth the effort)
| Tactic | Effort | Impact | How |
|--------|--------|--------|-----|
| Guest posting | Medium | High | Write for sites in your niche, link back |
| HARO/Connectively | Low | High | Respond to journalist queries |
| Broken link building | Medium | Medium | Find broken links on relevant sites, offer your content as replacement |
| Original research | High | Very High | Publish data/surveys others cite |
| Tool/calculator | High | Very High | Build free tool people link to |

### Low-Value (avoid or deprioritize)
- Directory submissions (unless niche-specific)
- Blog comment links
- Forum signature links
- Link exchanges ("I'll link you if you link me")
- PBNs (Private Blog Networks) — Google penalty risk

## Monitoring

### Weekly
- Google Search Console: errors, coverage issues
- Core Web Vitals: any regressions
- Rankings for top 10 keywords

### Monthly
- Full crawl: new broken links, redirect chains
- Backlink profile: new/lost links
- Content performance: traffic trends per page

### Quarterly
- Full site audit (use `scripts/site-audit.sh`)
- Competitor analysis: new content, new rankings
- Keyword gap analysis: new opportunities
