---
allowed_ops: brain.put_page, brain.get_page, brain.query
forbidden_ops: brain.sync, brain.ingest
required_fields: source
---

# Anton's Security & Privacy Rules

## Non-Negotiables
1. PRIVATE DATA STAYS PRIVATE: No exfiltration to training datasets.
2. MINIMAL DATA COLLECTION: Collect only what's operationally necessary.
3. ENCRYPTION AT REST: Keys, tokens, and secrets encrypted before storage.
4. NO HARDCODED SECRETS: All secrets via env vars or secret managers.
5. AUDIT EVERYTHING: Append-only logs. Non-repudiable.

## Credential Management
- Development: `.env` files in `.gitignore`
- Production: Cloudflare secrets or similar
- Never commit API keys (git-filter-branch if leaked)
- Rotate keys quarterly

## Third-Party Trust
- Assume partner services can disappear (Hostinger lesson)
- Maintain export capability for all data
- Prefer EU-hosted services for EU customers (GDPR)

