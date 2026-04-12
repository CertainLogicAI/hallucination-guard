---
summary: "AI Visibility Pro"
read_when: ["[]"]
---



# AI Visibility Pro

Make your site visible to AI. ChatGPT, Perplexity, Gemini, and Copilot are replacing Google for millions of queries. If LLMs don't know about you, you don't exist.

## Quick Reference

| Need | Resource |
|------|----------|
| Audit AI visibility of any site | `scripts/geo-audit.sh <url>` |
| Generate llms.txt + llms-full.txt | `scripts/llms-txt-generator.sh <url>` |
| Plan content LLMs will cite | `scripts/content-planner.sh <niche>` |
| GEO checklist (what matters) | `references/geo-checklist.md` |
| Content templates for AI citation | `references/content-templates.md` |
| Platform-specific guidance | `references/platform-guide.md` |

## How GEO Works

Traditional SEO optimizes for Google's crawler. GEO optimizes for how LLMs find, understand, and cite your content.

LLMs cite sources that:
1. **Answer specific questions** — not sales pages, but genuinely useful content
2. **Have structured data** — JSON-LD, clear headings, semantic HTML
3. **Are referenced by other sites** — backlinks still matter
4. **Provide unique data or research** — original findings, not rehashed content
5. **Have llms.txt** — the emerging standard for AI crawlers

## Audit Process

### 1. Run the GEO Audit
```bash
bash scripts/geo-audit.sh https://example.com
```
Checks 12 signals across 4 categories. Outputs a scored report.

### 2. Generate llms.txt
```bash
bash scripts/llms-txt-generator.sh https://example.com
```
Crawls your site and generates both `llms.txt` (summary) and `llms-full.txt` (detailed reference).

### 3. Plan Citeable Content
```bash
bash scripts/content-planner.sh "your niche"
```
Generates a content plan of articles LLMs would cite when answering questions in your niche.

### 4. Implement Fixes
Follow `references/geo-checklist.md` for the full optimization process. Prioritize:
- 🔴 **Critical:** llms.txt, JSON-LD structured data, answer-format content
- 🟡 **Important:** Original research/data, FAQ sections, semantic HTML
- 🟢 **Nice to have:** Platform submissions, RSS feed, citation-optimized headers

## Rules
- GEO supplements SEO — don't sacrifice Google rankings for AI visibility
- Content must be genuinely useful, not keyword-stuffed for AI
- Original data/research gets cited 3-5x more than summaries
- Update llms.txt whenever site content changes significantly
- Monitor AI citations monthly — check if Perplexity/ChatGPT mention you
