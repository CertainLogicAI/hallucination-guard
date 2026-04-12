---
summary: "\"Platform-Specific GEO Guide\""
read_when: ["["skill"]"]
---
# Platform-Specific GEO Guide

How each major AI platform finds and cites content — and how to optimize for each.

---

## ChatGPT (OpenAI)

**How it works:**
- Training data (cutoff ~6 months ago) + Browse with Bing plugin + GPT-4 web access
- Browse mode uses Bing index, not Google
- Favors authoritative, well-structured content
- Quotes text directly when citing sources

**Optimize for ChatGPT:**
- Get indexed by Bing (submit sitemap via Bing Webmaster Tools)
- Strong meta descriptions (ChatGPT shows these as source previews)
- JSON-LD schema (helps understand page content without rendering)
- FAQ sections (high extraction rate for Q&A format)
- Don't block OAI-SearchBot in robots.txt

**robots.txt:**
```
User-agent: OAI-SearchBot
Allow: /
```

---

## Perplexity

**How it works:**
- Real-time web search for every query
- Cites sources inline with numbered references
- Prioritizes recent, specific, authoritative content
- Has its own crawler (PerplexityBot)

**Optimize for Perplexity:**
- llms.txt is highly effective (Perplexity reads it)
- Fresh content wins — update dates matter
- Specific data/numbers get cited over generic advice
- Clear headings that match question phrasing
- Original research is cited 3-5x more than summaries
- RSS feeds help Perplexity discover new content faster

**robots.txt:**
```
User-agent: PerplexityBot
Allow: /
```

---

## Google Gemini

**How it works:**
- Uses Google Search index (strongest index)
- AI Overviews appear above organic results
- Extracts content from top-ranking pages
- Favors Google's own structured data standards

**Optimize for Gemini:**
- Everything that works for Google SEO works for Gemini
- Schema markup is critical (Google's been pushing this for years)
- FAQ schema gets pulled into AI Overviews frequently
- HowTo schema for step-by-step content
- Google Search Console is your monitoring tool

**Key difference:** Gemini relies on Google's index, so traditional SEO matters most here.

---

## Microsoft Copilot

**How it works:**
- Uses Bing index (same as ChatGPT browse mode)
- Integrated into Windows, Edge, Office
- Cites sources with preview cards
- Favors .edu, .gov, and high-authority domains

**Optimize for Copilot:**
- Bing Webmaster Tools — submit sitemap, monitor indexing
- Strong backlink profile matters (Bing weights authority heavily)
- Clear, formal writing style (Copilot tends toward professional sources)
- Avoid aggressive ad/popup patterns (Bing penalizes these)

**robots.txt:**
```
User-agent: bingbot
Allow: /
```

---

## Claude (Anthropic)

**How it works:**
- Training data only (no real-time web access in base model)
- API users can add web search via tools
- Very strong at reading structured content in context
- OpenClaw agents can fetch and read your site directly

**Optimize for Claude/OpenClaw users:**
- Clean, semantic HTML (Claude processes this well)
- llms.txt and llms-full.txt (OpenClaw agents look for these)
- Markdown-friendly content structure
- Avoid complex JavaScript rendering (agents use text extraction)

---

## Cross-Platform Priority List

| Action | ChatGPT | Perplexity | Gemini | Copilot | Priority |
|--------|---------|------------|--------|---------|----------|
| llms.txt | ✅ | ✅✅ | — | — | 🔴 High |
| JSON-LD schema | ✅✅ | ✅ | ✅✅ | ✅ | 🔴 High |
| Bing indexing | ✅✅ | — | — | ✅✅ | 🔴 High |
| Google indexing | — | ✅ | ✅✅ | — | 🔴 High |
| FAQ content | ✅✅ | ✅✅ | ✅✅ | ✅ | 🔴 High |
| Original data | ✅ | ✅✅ | ✅ | ✅ | 🟡 Medium |
| RSS feed | — | ✅✅ | — | — | 🟡 Medium |
| Fresh content | ✅ | ✅✅ | ✅ | ✅ | 🟡 Medium |
| Semantic HTML | ✅ | ✅ | ✅ | ✅ | 🟡 Medium |
| robots.txt allow | ✅ | ✅ | ✅ | ✅ | 🟢 Check |

## Monitoring Schedule

**Weekly:**
- Check Google Search Console for new queries

**Monthly:**
- Search 3-5 key queries on Perplexity → are you cited?
- Ask ChatGPT your key questions → does it mention you?
- Check Bing Webmaster for indexing issues

**Quarterly:**
- Update all content with fresh data/dates
- Review which content gets cited and create more like it
- Update llms.txt with any new pages/products
