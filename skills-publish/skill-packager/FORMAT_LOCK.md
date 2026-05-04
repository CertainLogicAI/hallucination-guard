# README Format Lock v1.0
# Enforced by Skill Packager — every CertainLogic skill MUST match this structure

## Required Sections (in order)

```
1. # [Skill Name]                     ← H1 title only
2. ## What This Is                     ← One sentence, no jargon
3. ## What It Does vs. What It Doesn't ← Two-column table (Does / Does NOT)
4. ## What You Get (Free Forever)      ← Benefits table with 2 columns
5. ## Honest Limitations               ← Specific limitations table
6. ## Quick Start                      ← Install options in priority order:
                                          a) One-line install (curl | bash)
                                          b) Single file drop-in
                                          c) ClawHub install
7. ## Usage                            ← CLI examples + Python API
8. ## When to Use This                 ← Good for / Not for lists
9. ## Related CertainLogic Tools       ← Cross-sell table (auto-injected)
10. [Brand Footer]                     ← Auto-injected
```

## Section Validation Rules

| Section | Must Contain | Fails If |
|---------|-------------|----------|
| What This Is | One sentence under 30 words | >30 words, OR jargon detected |
| What It Does NOT | Table with ❌ column | ❌ column missing, OR no limitations listed |
| What You Get | Table with "Feature" and "What It Means" columns | Either column missing |
| Honest Limitations | Table with "Limitation" and "What That Means" | Either column missing |
| Quick Start | At least one install method | No install instructions found |
| Brand Footer | CertainLogic links | Footer missing entirely |

## Prohibited Elements

| Element | Why Banned |
|---------|-----------|
| "100%" | Unverifiable claim |
| "eliminates" | Implies complete removal |
| "guarantees" | Legal-level claim |
| "proves" | Stronger than "records" |
| "deterministic" | Only if ZERO probabilistic components exist |
| "verified" | Ambiguous — "I checked" vs "system checked" |
| "cryptographic proof" | Does it verify truth or just authorship? |
| "zero hallucinations" | Unachievable |
| Cost % without methodology | Must be from live data, disclosed methodology |

## ClawHub SEO Requirements

| Field | Rule |
|-------|------|
| skill.json `name` | Searchable keywords first (not cute names) |
| skill.json `displayName` | Human-readable, under 40 chars |
| skill.json `description` | First sentence must include primary keyword + benefit |
| skill.json `tags` | Min 3, max 10. Mix of generic + specific + brand |
| README first paragraph | Include primary keyword in first 50 words |
