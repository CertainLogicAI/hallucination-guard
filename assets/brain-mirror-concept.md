# Asset Archive: Brain-Mirror Concept

**Status:** Archived — deferred until brain scale demands it  
**Date archived:** 2026-05-07  
**Triggered by:** Anton approved concept, wants revisit at scale threshold  
**Trigger threshold:** 10,000 facts in brain (or start of Wikipedia validation)

---

## One-Pager

**What:** Read-only replica of the production brain for safe experimentation and validation.

**Why:**
- Test config changes without risk
- A/B test content ingestion
- Anomaly detection (drift detection)
- Training data capture
- Load testing without affecting production

**Architecture:**
```
Production Brain (~/.gbrain/)  ──sync──>  Brain-Mirror (~/.gbrain-mirror/)
     (read-write)                           (read-only)
```

**Cost:** Disk space only (~10MB now, ~500MB at 100K facts). Zero API cost.

**Implementation:** `rsync` on ingest + `--data-dir` flag for CLI queries.

**Full concept:** See `journal/2026-05-07.md` "Speculative Product Idea: Brain-Mirror"

---

## Why Deferred

- Current scale: 443 facts. Git + backups sufficient.
- Wikipedia validation will push facts to 100K+. That's the trigger.
- Low complexity build (~30 min prototype) — no need to maintain it idle.

---

## Revisit Checklist (when triggered)

- [ ] Brain fact count ≥ 10,000
- [ ] Or: Wikipedia validation project started
- [ ] Review this archive
- [ ] Build prototype: `scripts/brain-mirror-sync.sh`
- [ ] Add mirror query flag: `--data-dir ~/.gbrain-mirror`
- [ ] Document anomaly detection workflow
- [ ] Consider: should mirror be a product feature or internal tool?
