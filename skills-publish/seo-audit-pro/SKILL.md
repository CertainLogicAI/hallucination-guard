---
summary: "SEO Audit Pro"
read_when: ["[]"]
---



# SEO Audit Pro

Audit websites, plan keyword strategy, optimize content, and fix technical issues to improve search rankings.

## Quick Reference

| Need | Resource |
|------|----------|
| Full site SEO audit | `scripts/site-audit.sh <domain>` |
| Keyword research plan | `scripts/keyword-planner.sh <niche>` |
| Optimize content for rankings | `references/content-optimization.md` |
| Fix technical SEO issues | `references/technical-fixes.md` |
| Extract & score meta tags from any URL | `scripts/meta-extractor.sh <url>` |
| Test page speed (TTFB, load time, size) | `scripts/page-speed-check.sh <url>` |

## Audit Process

### 1. Run the Site Audit
```bash
bash scripts/site-audit.sh example.com workspace/artifacts/audit-example.md
```
Walk through each section, checking against the live site using `web_fetch` and `browser`.

### 2. Prioritize Fixes
Group findings into:
- 🔴 **Critical** (fix this week) — broken pages, no HTTPS, Core Web Vitals failures
- 🟡 **Important** (fix this month) — missing meta tags, mobile issues, redirect chains
- 🟢 **Nice to have** (backlog) — schema markup, content refreshes, minor optimizations

### 3. Keyword Research
```bash
bash scripts/keyword-planner.sh "your niche" workspace/artifacts/keywords.md
```
Research with:
- Google Search Console (actual query data)
- Google autocomplete ("your topic" + alphabet)
- "People Also Ask" sections in SERPs
- Competitor content analysis (`web_fetch` their top pages)

### 4. Content Plan
Map keywords to content types:
- **Pillar pages** (2500+ words) — broad, high-volume topics
- **Cluster pages** (1000-1500 words) — specific, long-tail, link to pillar
- **Quick wins** — existing pages ranked 4-20, optimize to push higher

See `references/content-optimization.md` for the writing playbook.

### 5. Technical Fixes
Work through issues using `references/technical-fixes.md`:
- Page speed optimization
- Mobile usability
- Indexation issues
- Schema markup implementation
- Sitemap and robots.txt

### 6. Monitor
- **Weekly:** Search Console errors, Core Web Vitals, top 10 keyword rankings
- **Monthly:** Full crawl, backlink changes, content performance
- **Quarterly:** Full site audit, competitor analysis, keyword gaps

## Core Rules
- **Intent first** — match content to what the searcher actually wants
- **Answer fast** — primary answer in first 100 words
- **Unique value** — original insight competitors don't have
- **Measure everything** — no optimization without baseline data
- **No shortcuts** — PBNs, keyword stuffing, and link schemes get penalized
