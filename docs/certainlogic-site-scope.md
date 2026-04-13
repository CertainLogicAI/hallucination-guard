# CertainLogic.ai — Site Scope
*Created: 2026-04-13 | Updated: 2026-04-13*

## Vision
The full business platform for CertainLogic. Not a landing page — a polished, professional home for the brand, the blog, the shop, and the services. Built right the first time.

## Decisions Made
- **Tech:** Astro + Stripe + Cloudflare Pages
- **Priority:** Blog-first to build traffic, shop and services launch together
- **Design:** Light mode, business credibility, very polished — not a dev tool aesthetic
- **Domain:** certainlogic.ai (already on Cloudflare DNS)
- **Hosting:** Cloudflare Pages (free, fast, global CDN)
- **Payments:** Stripe (2.9% vs Gumroad's 10%)
- **No shortcuts** — build properly once, migrate all products here permanently

---

## Site Structure

### Phase 1 — Launch (Blog + Services + Shop)

#### Home (`/`)
- **Hero:** Strong headline focused on business outcomes, not tech
  - Draft: *"AI That Does What You Expect. Every Single Time."*
  - Sub: "We build deterministic AI tools for small businesses that can't afford to be wrong."
- Featured blog posts (3 latest)
- Featured products from shop (3 bestsellers)
- Services CTA: "Need something custom?"
- Trust signals: no stock robot photos, real outputs, real tools
- Email capture (newsletter)

#### Blog (`/blog`)
- Primary traffic driver, SEO-optimized
- Target audience: **business owners**, not developers
- Content pillars:
  1. **AI Gone Wrong** — hallucination horror stories, real business costs
  2. **AI Cost Control** — token waste, budget tools, "free vs expensive"
  3. **Practical Automation** — what agents actually do for SMBs
  4. **Case Studies** — client wins (once available)
  5. **Industry Insights** — AI trends through a business lens
- Each post: estimated read time, email capture, social share, related posts
- Categories clearly labeled
- Author: Anton (real name and background — builds credibility)

#### Shop (`/shop`)
- All premium skills and tools sold directly via Stripe
- Product pages with: description, what's included, who it's for, file format, instant delivery
- Categories:
  - AI Agent Tools (Skill Auditor Pro, Cold Outreach Pro, etc.)
  - Business Automation
  - Industrial (FaultTrace-adjacent tools when ready)
  - Bundles
- Pricing: $19-59 individual, $59-99 bundles
- Digital delivery: download link via Stripe webhook after payment
- No Gumroad, no ShopClawMart — all here permanently

#### Services (`/services`)
- **Headline:** "Custom AI Automation — Built to Work Every Time"
- What we build: deterministic automation tools for SMBs
- **Use cases** (concrete, business-owner language):
  - Auto-quoting from parts database — zero pricing errors
  - Customer support bot that only answers from verified facts
  - Inventory and order lookup — always accurate
  - Compliance checklists that never skip a step
  - Invoice processing and vendor validation
- **How it works:**
  1. Discovery call (30 min, free)
  2. Scope + fixed price quote
  3. Build (1-4 weeks depending on complexity)
  4. Deliver + test together
  5. Optional retainer for maintenance
- **Pricing:**
  - Small (1 function, <1 week): $2,000–3,500
  - Medium (multi-function, 1-2 weeks): $5,000–7,500
  - Large (full system, 2-4 weeks): $8,000–15,000
  - Retainer: $200–500/mo
- **Contact:** Calendly or simple form → Anton's email
- Testimonials section (placeholder until first clients)

#### About (`/about`)
- Anton's background: controls engineer, marketing degree, sales, real estate, crypto
- Why CertainLogic exists: "I got tired of AI that lies. So I built AI that can't."
- The philosophy: deterministic > probabilistic for business-critical tasks
- Not a faceless agency — a real expert you can talk to

#### FaultTrace (`/faulttrace`)
- Product overview page
- Link to faulttrace.ai app
- "Currently in beta — join waitlist" until pricing is live
- Industrial automation framing, separate from SMB consulting

---

### Phase 2 (Post-Launch)
- `/resources` — free tools, calculators, guides (lead magnets)
- `/case-studies` — detailed client stories with results
- `/docs` — documentation for purchased skills
- `/dashboard` — client portal for retainer clients (login required)

---

## Tech Stack

### Astro (Static Site Generator)
- Pages and blog posts written in Markdown/MDX
- No database needed for blog or static pages
- Extremely fast — static HTML served from Cloudflare edge
- Built-in image optimization, SEO meta tags
- Component-based (reuse header, footer, cards across pages)

### Stripe (Payments)
- Stripe Checkout for shop purchases
- Webhook receives `checkout.session.completed` → sends download email
- Stripe Customer Portal for receipts/history
- Products managed in Stripe dashboard
- No recurring subscriptions at launch (digital downloads only)

### Cloudflare Pages (Hosting)
- Free tier covers this entirely
- Deploys automatically on git push to main branch
- Global CDN — fast everywhere
- Custom domain (certainlogic.ai) already on Cloudflare DNS

### Email (Transactional + Newsletter)
- **Transactional** (purchase confirmations, download links): Resend.com ($0 for first 3K/mo)
- **Newsletter** (blog subscribers): ConvertKit free tier or Resend broadcasts
- Email capture on every blog post and homepage

### Analytics
- Cloudflare Web Analytics (free, privacy-respecting, no cookies)
- No Google Analytics — keeps the site clean and fast

---

## Design Direction

### Tone
- Professional, confident, direct
- Business credibility over tech showcase
- "We've solved this problem" not "look at our cool tech"

### Visual Style
- **Light mode** — clean white/light gray backgrounds
- **Typography:** Sharp, readable sans-serif (Inter or similar)
- **Accent color:** One strong brand color (TBD — could use deep blue or dark teal for trust/precision)
- No gradients, no animations for the sake of it
- No stock photos of robots, brains, or glowing circuits
- Real screenshots of tools, real output examples
- Generous whitespace — not cramped

### Trust Signals
- "Deterministic" and "verified" language throughout
- Hash verification, audit trail mentions where relevant
- Real expertise shown, not claimed (Anton's background front and center)
- Concrete numbers: "0.8% hallucination rate", "85% token reduction"

---

## Content Plan for Launch

### Blog Posts (write before launch)
1. "Why Your AI Assistant Is Lying to Your Customers" — hallucination explainer for business owners
2. "I Cut My AI Costs by 85% — Here's the System" — token reduction, practical guide
3. "The $50,000 Mistake: What Happens When AI Gets It Wrong in Business" — horror story format, drives urgency
4. "Deterministic AI: The Boring Technology Your Business Actually Needs" — positioning piece
5. "AI Agents for Small Business: What They Can (and Can't) Do" — realistic expectations, trust builder

### Shop Products at Launch
1. Skill Auditor Pro ($19)
2. Cold Outreach Pro ($19)
3. Market Research Pro ($19)
4. SEO Audit Pro ($19)
5. Business Starter Bundle ($59) — 4 skills bundled

---

## Build Plan

### Phase 1A: Foundation (2-3 days)
- Astro project setup
- Cloudflare Pages deployment pipeline (git push → live)
- Custom domain connected
- Base layout: header, footer, nav
- Design system: colors, typography, spacing

### Phase 1B: Blog (2-3 days)
- Blog index page
- Individual post template
- Markdown blog posts (5 posts written and published)
- SEO meta tags, Open Graph images
- Email capture form (Resend integration)

### Phase 1C: Shop (2-3 days)
- Shop index page
- Individual product pages
- Stripe Checkout integration
- Webhook → email delivery of digital products
- Order confirmation emails

### Phase 1D: Services + About + Home (2 days)
- Services page with pricing
- About page
- Home page tying everything together
- Final polish + mobile QA

### Phase 1E: Launch (1 day)
- Migrate products from Gumroad → Stripe
- Redirect ShopClawMart.com → certainlogic.ai/shop
- Announce on ClawHub profile
- First social posts

**Total estimated build time: 10-12 days working at good pace**

---

## Migration Checklist
- [ ] All Gumroad products recreated in Stripe with proper pricing
- [ ] ShopClawMart.com redirect set up
- [ ] ClawHub @blenderism profile updated to link CertainLogic.ai
- [ ] Existing customers notified (if any)
- [ ] Google Search Console set up for certainlogic.ai

---

## Status: SCOPED — Ready to build. Start with Phase 1A.
