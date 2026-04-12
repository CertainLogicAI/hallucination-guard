---
summary: "\"OpenClaw Workspace Optimization — Token-Burn Reduction\""
read_when: ["["idea"]"]
---
# OpenClaw Workspace Optimization — Token-Burn Reduction

**Project scope:** Treat the entire `/data/.openclaw/workspace` as a product and optimize everything for minimal LLM token consumption while preserving information density and utility.

---

## Problem

The workspace has grown organically:
- 50+ markdown files scattered across `ideas/`, `memory/`, `workspace/artifacts/`, `skills/`
- Many files are **duplicative** or **stale**
- No standardized format → each file loaded costs full tokens
- No semantic indexing → LLM must read entire files to find relevant info
- Large artifacts (scans, full webpage dumps) stored as raw text
- Skills and project docs bloated with boilerplate

**Result:** Every agent interaction burns 2,000–5,000 tokens just loading context. We need to cut that by 80%.

---

## Optimization Strategy

### 1. Consolidate & Prune

**Actions:**
- Merge similar idea files into a single `ideas/index.md` with TOC and section anchors
- Archive daily memory files older than 90 days into compressed `.tar.gz` (keep index)
- Delete artifacts that are not referenced (use `grep -r` to find references)
- Standardize all project docs to use the same frontmatter + section template

**Target:** Reduce file count by 40%, total corpus size by 60%

### 2. Semantic Indexing

**Create a search index** (`workspace-index.json`) that maps:
- Keywords → file path + line numbers
- Projects → related files
- Decisions → MEMORY.md snippets

This allows `memory_search` to be **faster and more precise**, reducing the need to load full files.

**Implementation:** Use a simple JSON inverted index built by a nightly cron job.

### 3. Chunk & Compress

**Large files (>5KB) should be split into chunks** with summaries:
- Example: `decoupled-agent-architecture-costs.md` → split into `overview`, `cost-model`, `timeline`, `stack`
- Each chunk has a 50-word summary stored in the index
- When queried, load only relevant chunks + summaries

**Expected token savings:** 70% on large docs

### 4. Frontmatter Standardization

Add YAML frontmatter to every markdown file:

```yaml
---
summary: "One-line description"
read_when:
  - faulttrace
  - api
  - pricing
---
```

This tells the agent **when to load the file** without reading it first. Agent scans frontmatter only (~50 tokens/file) and loads only matching files.

**Implementation:** Audit all .md files, add frontmatter where missing, use consistent tags.

### 5. Reference Files for Boilerplate

Move reusable content (e.g., "What is FaultTrace?", "Pricing model") into `references/` directory and **link** instead of embedding. For example, in a new idea doc:

```markdown
## FaultTrace Overview
See [references/faulttrace-product.md]{faulttrace} for details.
```

When the agent encounters `{faulttrace}`, it loads that reference file **once** and caches it. Avoids repeating same 500-token paragraph 20 times.

### 6. Binary Artifacts → Summaries

Convert large artifact scans (web dumps, PDFs) to **summaries** + store original in `artifacts/original/` (not loaded by default). The summary is what agents see; full text only if explicitly requested.

**Example:** `artifacts/intel-www.shopclawmart.com-2026-03-22_2049.md` → 500-word summary + link to full dump.

### 7. Cache Warm-Up

Create a `workspace-cache.json` that stores:
- Frontmatter of all files (for fast scanning)
- Summaries of all large files
- Recent memory entries (last 7 days)

This cache is loaded **once at agent startup** (~500 tokens) instead of scanning all files on-demand. Subsequent file reads fetch only what's needed.

### 8. Dead Link & Duplicate Detection

Run a script to find:
- Files that are never referenced (candidates for archiving)
- Near-duplicate content (cosine similarity >90%) — merge or delete
- Orphaned reference links

---

## Implementation Plan (2–3 days)

### Day 1: Audit & Frontmatter
- Script to list all .md files without frontmatter
- Add standardized frontmatter to every file (using GPT to generate summaries)
- Create `references/` directory, move boilerplate there
- Update all linking documents to use `{ref-name}` syntax

### Day 2: Index & Chunking
- Build `workspace-index.json` (inverted keyword index + summaries)
- Split large idea files into chunks
- Convert artifact scans to summaries + archive originals
- Implement cache warm-up loader

### Day 3: Integration & Testing
- Modify agent startup to load cache first
- Update `memory_search` to use index (fallback to file read if miss)
- Test token consumption before/after on typical queries
- Document the new structure in `WORKSPACE-OPTIMIZATION.md`

---

## Expected Savings

**Before:** Typical agent query loads 10 files × average 1,500 tokens = 15,000 tokens
**After:** Loads cache (500) + 3 relevant chunks (300 each) = 1,400 tokens

**Per-query savings:** ~13,600 tokens (91%)

At 100 queries/day: **1.36M tokens/day saved** → ~$100/month saved on API costs (Sonnet/Opus mix).

---

## Software Stack

- **Scripting:** Node.js (same runtime)
- **Index format:** JSON (fast parse, human-readable)
- **Cache:** In-memory JSON loaded at startup (or Redis if >5MB)
- **Frontmatter parsing:** `gray-matter` npm package
- **Summarization:** Use Haiku to generate frontmatter summaries (one-time batch)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Index out of date | Cron job rebuilds nightly |
| Agents ignore cache | Force cache-first in agent code |
| Lost context after split | Maintain TOC with section anchors |
| Reference link rot | Script to verify all `{ref-name}` exist |

---

## Decision

This is **high-value, low-risk**. The workspace is small enough to refactor manually; the token savings pay for the 3-day effort in ~1 month of reduced API bills.

**Approve?** If yes, I'll start with Day 1: audit + frontmatter standardization.

---
*Created: 2026-03-27*
*Status: proposed*
*Owner: workspace*
