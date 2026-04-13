# CertainLogic.ai — Site Scope
*Created: 2026-04-13*

## Vision
Full business platform — not a landing page. The home for everything we sell, publish, and offer.

## Site Structure

### Pages (MVP Launch)

**Home** — hero + value prop + featured products + latest blog posts + CTA
- "AI tools that work the same way. Every time."
- Featured skills/products
- Latest 3 blog posts
- "Need something custom?" CTA → services

**Shop** — premium skills and tools
- Individual skills ($19-59)
- Bundles ($59-99)
- Stripe checkout (2.9% vs Gumroad's 10%)
- Product pages with descriptions, screenshots, what's included
- Instant digital delivery (download after purchase)
- Categories: AI Agent Tools, Business Automation, SEO & Marketing, Industrial

**Blog** — content hub
- AI reliability, business automation, cost reduction
- Target: business owners, not developers
- Categories: AI for Business, Case Studies, Tutorials, Industry Insights
- SEO-optimized, shareable
- Email capture on each post

**Services** — consulting and custom builds
- What we build (deterministic automation tools)
- How it works (process: discovery → build → deliver → maintain)
- Pricing tiers (small/medium/large builds)
- Example use cases
- Contact form / booking link
- Testimonials (once available)

**About** — who's behind CertainLogic
- Anton's background (controls engineering + AI)
- Why deterministic AI matters
- The CertainLogic philosophy

**FaultTrace** — product page (or link to faulttrace.ai)
- Overview of the industrial tool
- Link to the app
- Pricing when ready

### Pages (Phase 2)
- **Resources** — free tools, calculators, guides
- **Case Studies** — detailed client stories
- **Documentation** — for purchased skills
- **Pricing** — dedicated pricing page when product line expands
- **Login/Dashboard** — for retainer clients (future)

## Tech Stack Options

### Option A: Static (GitHub Pages + Stripe)
- **Pros:** Free hosting, fast, simple, git-based content
- **Cons:** No dynamic features without JS, no built-in shop/blog CMS
- **Blog:** Markdown → static HTML (11ty, Hugo, or hand-built)
- **Shop:** Stripe Payment Links or Stripe Checkout embedded
- **Cost:** $0/mo (domain only)

### Option B: Lightweight CMS (Ghost, WordPress)
- **Pros:** Blog-native, SEO tools built in, themes, plugins
- **Cons:** Hosting cost, maintenance, security updates
- **Blog:** Built-in
- **Shop:** WooCommerce (WP) or Ghost memberships
- **Cost:** $10-30/mo hosting

### Option C: Modern Jamstack (Next.js/Astro + Stripe + MDX blog)
- **Pros:** Fast, modern, full control, great SEO, Stripe integration
- **Cons:** More build time upfront
- **Blog:** MDX files → static pages
- **Shop:** Stripe Checkout + webhook for delivery
- **Cost:** $0 on Vercel/Cloudflare Pages

**Recommendation:** Option C (Astro + Stripe). Fast, free to host, blog is markdown files, shop is Stripe Checkout, full control. No monthly costs beyond the domain. We can deploy on Cloudflare Pages since you already have Cloudflare for DNS.

## Design Direction
- Clean, professional, not flashy
- Dark mode default (matches FaultTrace aesthetic)
- Trust signals: "deterministic", "verified", "auditable"
- No stock photos of robots or brains
- Show real output, real tools, real results
- Mobile-first (business owners browse on phones)

## Content Priorities (Launch)
- 3-5 blog posts ready at launch
- 4-6 premium skills listed in shop
- Services page with clear pricing
- Home page that converts visitors to either shop or services inquiry

## Migration Plan
- Move Gumroad products → CertainLogic.ai shop
- Redirect ShopClawMart.com → certainlogic.ai/shop
- Keep free skills on ClawHub (marketing funnel stays)
- Update ClawHub @blenderism profile to link to CertainLogic.ai

## Decision Needed
- Confirm tech stack (Astro recommended)
- Design preferences (dark mode? minimal? specific references?)
- Priority: launch with shop + blog + services, or blog-first?

## Status: SCOPED — Ready to build on Anton's go
