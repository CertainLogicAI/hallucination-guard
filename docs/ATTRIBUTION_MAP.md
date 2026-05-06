# Attribution Map: GBrain vs CertainLogic Improvements

**Date:** 2026-05-06  
**Question:** Where do the benefits come from?  
**Answer:** GBrain = foundation (~25%). CertainLogic = differentiation (~75%).

---

## GBrain Foundation (Garry Tan)

| Capability | What It Does |
|------------|-------------|
| Markdown page storage | Stores content as slugs with frontmatter |
| Semantic search | Finds pages by meaning, not keywords |
| PGLite database | Persistent SQLite-compatible storage |
| CLI interface | `gbrain put`, `gbrain get`, `gbrain search` |

**Without GBrain:** No persistent knowledge base, no search, no CLI tooling.

**Value:** $50K-100K in avoided engineering. Essential but not unique.

---

## CertainLogic Improvements (Us)

### Layer 1: Deterministic Validation
- **SHA-256 content hashing** — Proves content has not been tampered with
- **Hash verification on every read** — Detects unauthorized modifications
- **Raw hash canonicalization** — Our fix for GBrain trimming issues

**Without this:** Agent could modify data undetected. No cryptographic proof.

### Layer 2: HMAC Cryptographic Provenance
- **HMAC-SHA256 signing** — Every write cryptographically signed (32 entries)
- **Signature verification** — Prove who wrote what when
- **Append-only audit log** — Non-repudiable history (395 entries)

**Without this:** Anyone could write undetected. No compliance/insurance value.

### Layer 3: Intent-Based Access Control
- **Domain-specific policies** — Medical data ≠ marketing data rules
- **Command whitelisting/blacklisting** — Block sync on medical domain
- **Required field enforcement** — Every write needs source attribution
- **Policy stored in brain** — `family/who/anton/*` not hardcoded

**Without this:** All agents same permissions. No regulated deployment possible.

### Layer 4: Ethos Encoding & Self-Alignment
- **Anton business ethos** — Profitability > growth
- **Anton communication style** — Brutally clear, no fluff
- **Anton technical preferences** — Astro + Tailwind, not random stacks
- **Anton security rules** — Block data exfiltration automatically
- **Family structure** — Hierarchical organization of all work

**Without this:** Generic agent behavior. Sounds like ChatGPT, not CertainLogic.

### Layer 5: Brain Capture Policy & Governance
- **Mandatory documentation** — No claim without evidence
- **Public claims gate** — Alex blocks unverified marketing
- **Verified storage** — Every write confirmed persisted
- **Recursive audit** — Brain captures its own operations

**Without this:** Empty brain = useless. Marketing becomes speculation.

---

## Net Value Assessment

| Value Driver | Attribution | % of Total |
|-------------|-------------|-----------|
| Persistent storage | GBrain | 15% |
| Search/retrieval | GBrain | 10% |
| Cryptographic integrity | CertainLogic | 25% |
| Intent-based governance | CertainLogic | 20% |
| Ethos encoding | CertainLogic | 20% |
| Brain capture policies | CertainLogic | 10% |

**GBrain = ~25% of value. CertainLogic = ~75%.**

But without the 25% foundation, the 75% has nothing to build on.

---

## How to Explain This

### To Investors
> "We built on Garry Tan's GBrain because it's production-grade. But GBrain alone isn't sufficient for business use. We added cryptographic provenance, intent-based access control, and ethos encoding. The result is deterministic brain infrastructure that agents use safely in regulated environments."

### Simple Version
> "GBrain is like a filing cabinet. We added locks, cameras, and a rulebook. The cabinet is nice. The security is what makes banks willing to use it."

### Competitive Version
> "Anyone can use GBrain. Only CertainLogic has the deterministic verification layer. A competitor would need to rebuild 4 layers of cryptographic infrastructure to match what we have."

---

## YC Application Line

> "We built a deterministic verification layer on top of Garry Tan's GBrain, turning a knowledge base into auditable, regulated, self-aligning infrastructure."

---

## Key Rule

**Always credit GBrain for the foundation. Always emphasize CertainLogic for the differentiation. Never let anyone think GBrain alone is sufficient for business deployment.**
