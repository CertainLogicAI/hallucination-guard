# Reference Curation Checklist

Use this checklist to transform client documents into a deterministic AI reference corpus. This ensures every document is processed consistently for tag indexing, summarization, and validation.

---

## Phase 1: Ingestion

### 1.1 Document Collection
- [ ] Gather all source files from client (PDF, DOCX, MD, L5X, etc.)
- [ ] Create inventory in `documents.csv`:
  - `path`, `filename`, `filetype`, `size`, `last_modified`
- [ ] Verify completeness with client

### 1.2 File Normalization
- [ ] Convert all documents to UTF-8 text
- [ ] Extract text from PDFs:
  - `pdftotext` for selectable PDFs
  - OCR fallback for scanned PDFs (tesseract)
- [ ] Strip metadata, headers, footers where irrelevant
- [ ] Normalize line endings (`\n`)
- [ ] Document any lossy conversions (note in log)

---

## Phase 2: Semantic Tagging

### 2.1 Tag Inference
For each document, assign `read_when` tags based on content:
- [ ] Auto‑suggest tags using keyword matching:
  - `plc` if contains "ladder logic", "l5x", "routine", "rung"
  - `pricing` if contains "$", "cost", "subscription", "tier"
  - `api` if contains "endpoint", "http", "request", "response"
  - `security` if contains "auth", "token", "encrypt", "access"
  - `sops` if contains "procedure", "work instruction", "step"
  - `compliance` if contains "regulation", "policy", "must", "shall"
- [ ] Review auto‑tags; add/remove manually
- [ ] Each document should have 1–3 relevant tags

### 2.2 Tag Validation
- [ ] Run tag coverage report:
  - Which tags appear most/least?
  - Are any critical domains missing tags?
- [ ] Add missing tags to `tags.json` master list

---

## Phase 3: Summarization

### 3.1 Summary Generation
For each document:
- [ ] Extract first heading (`# ...`) if present → candidate summary
- [ ] If no heading, take first non‑empty paragraph
- [ ] Limit to **500 characters**
- [ ] Ellipsis truncation: `...` at the end if trimmed
- [ ] Remove markdown formatting from summary
- [ ] Store in `summaries/<filename>.txt`

### 3.2 Summary Quality Check
- [ ] Sample 10% of summaries; verify they capture the document's gist
- [ ] Flag documents with poor summaries for manual rewrite
- [ ] Ensure summaries don't contain disallowed sections:
  - No tables (summaries should be plain text)
  - No code blocks
  - No images / references to figures

---

## Phase 4: Reference Canonicalization

### 4.1 Identify Canonical Documents
- [ ] Mark documents that should be **full‑text references** (not just summarized):
  - Product definitions
  - Pricing tables
  - Regulatory frameworks
  - Core technical specifications
- [ ] Store these in `workspace-references/` with key names (e.g., `faulttrace-product.md`)
- [ ] Verify they contain complete, authoritative information

### 4.2 Reference Deduplication
- [ ] Find near‑duplicate references (fuzzy match >90%)
- [ ] Keep one canonical; mark duplicates as `deprecated`
- [ ] Update cache index to point only to canonical

---

## 5. Build Workspace Cache

### 5.1 Cache Structure
Create `workspace-cache.json`:
```json
{
  "files": [
    {
      "path": "relative/path/to/file.md",
      "summary": "Short 500‑char summary...",
      "tags": ["tag1", "tag2"],
      "last_modified": "2026-03-27T00:00:00Z"
    }
  ],
  "references": [
    {
      "key": "faulttrace-product",
      "content": "Full canonical text..."
    }
  ],
  "index": {
    "tag1": ["relative/path/to/file.md"],
    "tag2": ["relative/path/to/file2.md"]
  }
}
```

### 5.2 Validation Steps
- [ ] Run `build-cache-clean.js` (no errors)
- [ ] Check cache size (<100 MB for typical client)
- [ ] Spot‑check a few entries:
  - Paths are correct relative to workspace root
  - Summaries match source documents
  - Tags match `read_when` arrays in original frontmatter
  - References contain full content

---

## 6. Testing

### 6.1 Tag Coverage Test
```bash
node tag-coverage.js --cache workspace-cache.json
```
- [ ] All critical use‑case tags have at least 3 files each
- [ ] No tag has 0 files (orphan)

### 6.2 Summaries Sanity Check
```bash
node summary-audit.js --cache workspace-cache.json --sample 20
```
- [ ] No truncation in middle of a sentence (check `...` usage)
- [ ] No markdown remnants (`#`, `-`, `*`)
- [ ] Summaries < 500 chars

### 6.3 Reference Completeness
- [ ] All `references.[]` have `content` field non‑empty
- [ ] No `null` or `undefined` values

---

## 7. Delivery & Documentation

### 7.1 Deliverables
- [ ] `workspace-cache.json` (compiled corpus)
- [ ] `workspace-references/` (canonical full‑text refs, if any)
- [ ] `CURATION_LOG.md` (documents processed, tags applied, summary edits)
- [ ] `TEST_RESULTS.md` (outputs of the validation scripts above)

### 7.2 Client Handoff Guide
Write `CLIENT_USAGE.md` covering:
- How to add new documents
- How to re‑run the cache build
- How to update tags and summaries
- How to validate after updates
- Emergency rollback procedure

### 7.3 Sign‑off
- [ ] Client SME reviews `workspace-cache.json` sample entries
- [ ] Client signs off on reference selections
- [ ] Project moves to Agent Build phase

---

## Common Pitfalls & Mitigation

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Missing tags | Queries return no context | Add appropriate tags to documents; re‑build cache |
| Over‑long summaries | Cache bloat, slower loads | Enforce 500‑char limit; truncate cleanly |
| Reference not canonical | Cached responses may diverge | Mark one version as canonical; deprecate others |
| Non‑UTF‑8 files | Extraction errors | Convert encoding before processing |
| OCR garbage in scanned PDFs | Gibberish in summaries | Manual review of scanned documents |

---

## Checklist Sign‑off

**Curator:** ____________________  
**Date:** ____________________  
**Client Representative:** ____________________  

---

*This checklist ensures every client reference corpus is built to production‑grade standards for deterministic AI agents.*
