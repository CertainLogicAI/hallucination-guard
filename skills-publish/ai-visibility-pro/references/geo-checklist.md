---
summary: "\"GEO Checklist — Generative Engine Optimization\""
read_when: ["[]"]
---
# GEO Checklist — Generative Engine Optimization

## 🔴 Critical (Do First)

### llms.txt
- [ ] Create `llms.txt` at site root — brief summary of what your site does
- [ ] Create `llms-full.txt` — detailed reference with all products/services/content
- [ ] Include: site name, what you do, key pages, contact info
- [ ] Update whenever site content changes significantly

### Structured Data
- [ ] JSON-LD schema on every page (minimum: Organization or WebPage)
- [ ] Product schema with pricing for any products/services
- [ ] Article schema on blog posts (author, date, headline)
- [ ] FAQ schema on any page with Q&A content
- [ ] Breadcrumb schema for navigation

### Answer-Format Content
- [ ] At least 3 blog posts that directly answer questions in your niche
- [ ] Each post starts with a direct answer (no "In this article, we'll explore...")
- [ ] FAQ sections with 3-5 questions on every content page
- [ ] TL;DR sections near the top of long articles

## 🟡 Important (Do Next)

### Original Research
- [ ] At least 1 post with original data, findings, or benchmarks
- [ ] Data that nobody else has published (surveys, audits, experiments)
- [ ] Clear methodology section (builds trust with AI systems)
- [ ] Specific numbers over vague claims ("3 out of 10" not "several")

### Semantic HTML
- [ ] Use `<article>`, `<section>`, `<nav>`, `<header>`, `<main>`, `<footer>`
- [ ] Proper heading hierarchy (H1 → H2 → H3, no skipping)
- [ ] Descriptive headings (match natural language queries)
- [ ] Lists and tables for structured information

### Meta Tags
- [ ] Unique title per page (50-60 chars, includes primary keyword)
- [ ] Meta description per page (80-160 chars, answers "what is this page about?")
- [ ] Open Graph tags (title, description, image, type, url)
- [ ] Twitter Card tags (card type, title, description, image)
- [ ] Canonical URL on every page

### Technical
- [ ] Sitemap.xml with all content pages
- [ ] robots.txt that doesn't block AI crawlers
- [ ] RSS/Atom feed for blog content
- [ ] Fast load time (<2s) — slow sites get deprioritized
- [ ] Mobile responsive — AI crawlers check mobile rendering
- [ ] HTTPS — non-negotiable

## 🟢 Nice to Have (Ongoing)

### Platform Submissions
- [ ] Submit to Perplexity Pages (if available for your niche)
- [ ] Ensure Google indexes all pages (Search Console)
- [ ] Submit sitemap to Bing Webmaster Tools (Copilot uses Bing index)
- [ ] Get listed on relevant directories and databases

### Backlink Building
- [ ] Post original research on Reddit (relevant subreddits)
- [ ] Submit to Hacker News (Show HN for tools/products)
- [ ] Guest posts or mentions on niche blogs
- [ ] Contribute to open-source projects (README links)
- [ ] Answer questions on Stack Overflow / forums with link to content

### Content Freshness
- [ ] Update key articles quarterly with new data
- [ ] Add "Last updated" dates to content
- [ ] Remove or redirect outdated content
- [ ] Expand FAQ sections based on actual questions received

### Monitoring
- [ ] Monthly: search your key queries on Perplexity, note if cited
- [ ] Monthly: ask ChatGPT about your topic, see if mentioned
- [ ] Monthly: check Google Search Console for new queries finding your site
- [ ] Track which content gets cited and double down on that format

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 16-19/19 | Excellent — you're AI-visible |
| 12-15/19 | Good — fix the gaps |
| 8-11/19 | Needs work — missing key signals |
| 0-7/19 | Invisible to AI — start with Critical items |

## What NOT to Do

- ❌ Don't block AI crawlers in robots.txt (unless you have a specific legal reason)
- ❌ Don't stuff keywords unnaturally — LLMs detect this
- ❌ Don't create thin "SEO content" — LLMs prefer depth over quantity
- ❌ Don't hide content behind JavaScript that crawlers can't render
- ❌ Don't use only images for key information — LLMs can't read images reliably
- ❌ Don't ignore FAQs — they're the highest-citation content format
