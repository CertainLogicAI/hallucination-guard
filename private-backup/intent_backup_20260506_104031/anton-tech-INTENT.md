---
allowed_ops: brain.put_page, brain.get_page, brain.query, brain.search
forbidden_ops: brain.sync
required_fields: source
---

# Anton's Technical Preferences

## Stack Defaults (Use unless justification exists)
- Frontend: Astro v6 + Tailwind v4
- Backend: Python (FastAPI/Flask) or TypeScript (Bun runtime)
- Database: SQLite/PGLite for embedded, Postgres for production
- Host: Cloudflare Pages (free tier) or Hetzner ($5/mo)
- AI: Free models until revenue; Kimi K2.6 for architecture; cheap models for crons
- Auth: Simple > Complex (token-based first, OAuth when needed)

## Quality Thresholds
- Tests: Every non-trivial module gets pytest before prod
- Documentation: README + inline comments. No novels.
- Commits: Clear messages. `git commit -m "what and why"`

## Anti-Patterns (Avoid)
- Serverless for predictable workloads (too expensive)
- Kubernetes for < 10 services (overengineering)
- LLM for logic that rules can handle (waste + risk)
- Over-abstracting before you have 3 examples (YAGNI)

## Approved Vendors
- Cloudflare (DNS, Pages, Workers)
- Hetzner (compute)
- Backblaze (backups)
- GitHub (code + issues — already there)

