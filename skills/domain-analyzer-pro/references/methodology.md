---
summary: "\"Domain Analyzer Methodology\""
read_when: ["["skill"]"]
---
# Domain Analyzer Methodology

## Overview

Build a file-format-specific static analyzer in 8 phases. Each phase produces a testable deliverable.

## Phase 1: Format Research

Understand the target file format before writing code.

**Steps:**
1. Identify the file format (XML, JSON, binary, text-based)
2. Find existing parsers/libraries (GitHub, npm, PyPI) — don't reinvent
3. Get 3-5 real-world sample files (open-source repos, forums, user-provided)
4. Document the structure: root element, nesting, how domain logic is encoded

**Deliverable:** Format cheat sheet (10-20 lines) with structure, key elements, gotchas.

**Example (PLC L5X):**
```
Root: RSLogix5000Content > Controller
Programs: Controller > Programs > Program (name attr)
Routines: Program > Routines > Routine (type: RLL/ST/FBD)
Rungs: Routine > RLLContent > Rung (number attr)
Logic: Rung > Text element (instruction syntax: XIC(tag)OTE(tag))
Tags: Controller > Tags > Tag (name, datatype, value)
Modules: Controller > Modules > Module (I/O config)
```

## Phase 2: Parser

Build a parser that extracts structured data from the raw file.

**Design rules:**
- Client-side (browser) when possible — no server, no upload, no security objections
- Output a normalized object: `{ metadata, programs/sections, tags/symbols, crossReferences }`
- Cross-reference is critical: for every symbol/tag, track where it's read and written
- Handle partial/incomplete files gracefully — error message, not crash

**Parser output structure:**
```javascript
{
  metadata: { name, version, processor, exportDate },
  programs: [{ name, routines: [{ name, type, rungs/statements }] }],
  tags: [{ name, type, scope, value }],
  modules: [{ name, type, slot }],
  xref: { tagName: [{ program, routine, rung, access: 'read'|'write' }] }
}
```

**Testing:** Parse every sample file. Log: parse time, element counts, any warnings. Target: 0 crashes, <3s for files under 10MB.

## Phase 3: Rule Engine

Rules detect known-bad patterns. Each rule is a function that takes the parsed project and returns findings.

**Rule anatomy:**
```javascript
{
  rule: 'UNIQUE_ID',           // SCREAMING_SNAKE_CASE
  severity: 'critical|warning|info',
  title: 'Human-readable title',
  description: 'What this means in domain terms — not code terms',
  recommendation: 'Specific action to fix it',
  locations: [{ file, section, line }],
  tag: 'affected_symbol'       // optional
}
```

**Writing good rules:**
1. Start with 10-15 rules covering the most common issues
2. Each rule needs a positive test (must detect) AND negative test (must NOT detect)
3. Descriptions must speak the domain language, not programmer language
4. Recommendations must be actionable — "check X at location Y", not "verify correctness"

**Severity guide:**
- **Critical:** Will cause a runtime failure, crash, or safety issue
- **Warning:** Likely unintentional, will cause intermittent or hard-to-find issues
- **Info:** Code quality, maintenance concern, or suspicious pattern

## Phase 4: False Positive Reduction

The most important phase. A tool that cries wolf is worse than no tool.

**Process:**
1. Run rules against ALL sample files, count findings per rule
2. Any rule producing >50 findings per file is probably too broad
3. For each high-volume rule, examine 10 random findings — what % are real?
4. Add exclusions for known-good patterns (init sequences, alarm tags, config blocks)
5. Re-run and compare: track `Round N → Round N+1` reduction per rule

**Common false positive sources:**
- Initialization code (constants, default values, startup sequences)
- Intentional patterns (alarm latches, heartbeats, watchdogs)
- Library/AOI internal code (not user-written, different conventions)
- Partial exports (missing context that exists in full project)

**Target:** <5% false positive rate on real-world files. Track progression:
```
Round 1 (raw):    1,982 findings
Round 2 (FP fix): 664 findings (-66%)
Round 3 (UX fix): 650 findings (-67%)
```

## Phase 5: Trace Engine

Static analysis says "what's wrong." Trace engine says "why doesn't this work."

**Core algorithm:** Backward dependency trace from any output symbol.
1. User picks a symbol (output, motor, valve, endpoint)
2. Find every rung/statement that WRITES to it
3. For each write location, find all READ dependencies
4. Recursively trace each dependency until reaching:
   - Physical inputs (sensors, switches, buttons)
   - Constants/literals
   - Circular references (flag and stop)

**Output format:**
```
📍 Target_Output ← written at [Location]
   Needs: Condition_A AND Condition_B
   📍 Condition_A ← written at [Location]
      Needs: Sub_Condition_1 AND Sub_Condition_2
      🔌 Sub_Condition_1 — PHYSICAL INPUT (check at terminal)
```

**Derived analysis from trace:**
- **Permissive checklist:** All physical inputs that must be true (walk-the-floor list)
- **Kill conditions:** Anything that forces the output OFF
- **Single points of failure:** Inputs with no redundancy in the chain

## Phase 6: Domain Knowledge Database

Scrape domain forums/knowledge bases for known solutions to common problems.

**Process:**
1. Identify top forums (2-3 sources, public data only)
2. Build a scraper with respectful delays (3+ seconds between requests)
3. Parse threads: title, question, replies, solution indicators
4. Store as JSONL (one record per thread, first 5 replies)
5. Build keyword index for fast lookup

**Matching strategy:** When rule engine finds an issue, search database by:
- Rule type keywords (e.g., "VFD fault", "comm loss", "timeout")
- Component identifiers from the finding
- Return top 3 matching threads with solution excerpts

**This replaces AI for known problems.** Database lookup = free, instant. AI = expensive, slow. Only escalate to AI when database has no match.

## Phase 7: Test Harness

Two types of tests, both required:

**A. Unit tests (synthetic):**
- One test per rule: positive case (must detect) + negative case (must NOT detect)
- Minimal synthetic files — just enough structure to trigger/not trigger the rule
- Run in <1 second total

**B. Integration tests (real files):**
- Run full analysis on every real-world sample file
- Track finding counts per rule across all files
- Fault injection: insert known-bad patterns into a clean file, verify detection, verify count delta matches exactly

**Fault injection pattern:**
```javascript
// Inject N known faults → run analysis → verify:
// 1. Total findings increased by exactly N
// 2. Each injected fault appears in results
// 3. No new false positives introduced (baseline stable)
```

## Phase 8: UI / Delivery

The analysis engine is usable through multiple interfaces:

**Option A: Web app (recommended for broad reach)**
- Client-side file parsing (no upload = no security objection)
- Results grouped by severity, expandable details
- Trace engine as interactive tree (click any symbol to trace)

**Option B: CLI tool**
- `analyze <file>` → JSON or formatted terminal output
- Pipe-friendly for CI/CD integration

**Option C: OpenClaw skill integration**
- Agent reads file, runs parser + rules, reports findings in conversation
- Trace engine available via follow-up questions

All three can share the same parser, rule engine, and trace engine code.
