---
summary: "\"False Positive Reduction Guide\""
read_when: ["["skill"]"]
---
# False Positive Reduction Guide

## Why This Matters

A tool with 50% false positives is abandoned after the first use. Engineers don't have time to sort signal from noise. Target: <5% false positive rate.

## The Reduction Loop

```
Run rules on ALL real files
    ↓
Count findings per rule
    ↓
Rules with >50 findings/file? → Too broad
    ↓
Sample 10 findings → categorize each as real/false
    ↓
Identify the false positive PATTERN (not individual cases)
    ↓
Add exclusion for the pattern
    ↓
Re-run → compare counts → repeat
```

Track every round:
```
                 🔴Crit  🟡Warn  🔵Info  Total
Round 1 (raw)        72    1738    172   1982
Round 2 (fixes)      13     479    172    664
Round 3 (UX)          3     475    172    650
```

## Common False Positive Categories

### 1. Initialization Patterns
**What:** Startup code that sets defaults, constants, initial states.
**Why flagged:** Looks like unconditional writes.
**Fix:** Exclude literal/constant assignments, detect init routine names, exclude first-rung patterns.

### 2. Intentional Domain Patterns
**What:** Heartbeats, watchdogs, alarm latches, config blocks.
**Why flagged:** Matches generic "no condition" or "no reset" rules.
**Fix:** Build a naming-pattern exclusion list. Common suffixes: `_Heartbeat`, `_Watchdog`, `_Alarm`, `_Fault`, `_Config`.

### 3. Library/Framework Code
**What:** Third-party libraries, AOIs, imported modules, vendor templates.
**Why flagged:** Different coding conventions than user code.
**Fix:** Detect library markers (AOI flag, namespace prefix, import path) and reduce severity or skip.

### 4. Partial Context
**What:** File is an export/subset of a larger project.
**Why flagged:** References to things that exist in the full project but not in the export.
**Fix:** Detect partial exports (missing root elements, empty sections) and suppress rules that need full context.

### 5. Domain-Specific Valid Patterns
**What:** Patterns that LOOK wrong generically but are correct in this domain.
**Why flagged:** Rules too generic.
**Fix:** Add domain-aware exclusions. Examples:
- PLC: `MOV(literal, tag)` is standard init — not an unconditional output
- Config: Duplicate keys in different environments are intentional
- CSS: Duplicate selectors for media query overrides are valid

## Exclusion Implementation Patterns

### Pattern-based exclusion (naming)
```javascript
// Skip alarm/fault tags for latch-without-unlatch rule
const skipPatterns = /alarm|fault|error|warning|status/i;
if (skipPatterns.test(tagName)) return; // not a false positive
```

### Context-based exclusion (structure)
```javascript
// Skip unconditional output if it's a MOV with a literal (init pattern)
if (instr.name === 'MOV' && isLiteral(instr.args[0])) return;
```

### Scope-based exclusion (origin)
```javascript
// Skip findings inside AOI/library code — different conventions
if (container.isAOI || container.isLibrary) return;
```

### Relationship-based exclusion (cross-ref)
```javascript
// Only flag circular dependency when BOTH sides use same write type
// OTL→OTU interlock is intentional, OTE↔OTE is likely a bug
if (writeA.type !== writeB.type) return;
```

## Validation Checklist

After each reduction round, verify:
- [ ] No rule dropped to 0 findings (did you kill the rule entirely?)
- [ ] Total reduction is plausible (>80% reduction in one round = suspicious)
- [ ] Existing test harness still passes (didn't break detection)
- [ ] Sample 5 remaining findings per rule — still real?
- [ ] Any new false positive categories discovered? Add to exclusion list.
