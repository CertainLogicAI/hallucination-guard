---
summary: "\"Analyzer Porting Guide\""
read_when: ["["faulttrace", "api"]"]
---
# Analyzer Porting Guide

**Move FaultTrace from browser to Node.js**

---

## Overview

The FaultTrace analyzer lives in `faulttrace-app/src/` as browser JavaScript. We need to port it to Node to power the API.

**Key challenges:**
- Browser APIs (`DOMParser`, `URL`, `File`, `Web Workers`) aren't in Node
- No `localStorage` or `IndexedDB`
- Module system: ESM in browser vs CommonJS in Node (or use ESM)

---

## Step-by-Step

### 1. Audit Dependencies

From `faulttrace-app/package.json`, list all imports. Likely:

- `xmldom` or native `DOMParser` → replace with `xmldom` or `fast-xml-parser`
- `regenerator-runtime` (if async/await) → Node 18+ has this
- Any file I/O (unlikely in browser) → use `fs` in Node

### 2. Parser Port

**Browser version** (likely):
```javascript
const parser = new DOMParser();
const xmlDoc = parser.parseFromString(l5xString, 'text/xml');
```

**Node version:**
```javascript
const { DOMParser } = require('xmldom'); // or fast-xml-parser
const xmlDoc = new DOMParser().parseFromString(l5xString, 'text/xml');
```

Install: `npm install xmldom`

Alternative: `fast-xml-parser` is faster and more lenient. Test both.

### 3. Rule Engine Port

Copy the entire `rules/` directory. Most rules are pure functions:

```javascript
// Rule signature
function unusedTagRule(tags, xref) {
  return tags.filter(tag => !tag.used).map(tag => ({
    id: `unused-${tag.name}`,
    severity: 'warning',
    rule: 'UnusedTag',
    message: `Tag ${tag.name} declared but never used`,
    location: tag.location,
    suggestion: 'Remove or use'
  }));
}
```

Ensure all dependencies are available in Node (no browser globals).

### 4. Trace Engine Port

Trace likely walks the program rungs, tracking rung/bit states. May need:

- A `Program` class that holds all routines, tags, I/O
- `trace(startRung, targetTag)` method returning path array

Check for `requestAnimationFrame` or `setTimeout` loops — replace with `setImmediate` or direct loops.

### 5. Cross-Reference Builder

Xref builds maps: tag→rungs, rung→tags, routine↔routine. Pure JS, should port easily.

### 6. I/O Map Extraction

L5X has `<I/O>` or similar sections. Parser should extract:

- Inputs: `<Input>` tags with `Address` (e.g., `Local:1:I.Data.0`)
- Outputs: `<Output>` tags
- Build array of `{name, type, address}`

### 7. Tags List

Collect all `<Tag>` declarations with:
- `Name` attribute
- `DataType` (BOOL, DINT, etc.)
- `Usage` (if present) or compute from xref

### 8. Assemble Report

In `analyzeL5XBuffer`:

```javascript
async function analyzeL5XBuffer(l5xBuffer) {
  const l5xString = l5xBuffer.toString('utf8');
  const xmlDoc = parse(l5xString); // your parser

  const tags = buildTags(xmlDoc);
  const xref = buildXRef(xmlDoc, tags);
  const ioMap = buildIOMap(xmlDoc);
  const summary = computeSummary(tags, xref);

  const issues = [
    ...unusedTagRule(tags, xref),
    ...otherRules(xmlDoc, tags, xref),
    // 18 rules total
  ];

  return {
    metadata: { /* ... */ },
    summary,
    issues,
    ioMap,
    tags
  };
}
```

### 9. Performance

- 4,032-rung file should analyze in <5s on 4 vCPU
- If slow: consider streaming parser (sax instead of DOM)
- Cache parsed AST if multiple analyses on same file? (unlikely)
- Use `--max-old-space-size` if memory pressure

### 10. Testing

Add test files to `test/`:

```javascript
const { analyzeL5XBuffer } = require('../src/analyzer');
const fs = require('fs');

test('analyzes small file', async () => {
  const buf = fs.readFileSync('test/fixtures/simple.l5x');
  const report = await analyzeL5XBuffer(buf);
  expect(report.summary.totalRungs).toBeGreaterThan(0);
  expect(Array.isArray(report.issues)).toBe(true);
});
```

Run with `npm test` (use Jest or Vitest).

---

## Integration Checklist

- [ ] Parser works on all 33 test L5X files (same results as browser version)
- [ ] Output matches `types.js` schema exactly
- [ ] No `document` or `window` references
- [ ] Memory usage <500MB per analysis
- [ ] 4k-rung file processes in <5s
- [ ] Errors thrown on malformed L5X (try/catch in route)
- [ ] Remove mock data and `setTimeout`

---

## Common Pitfalls

| Issue | Browser | Node fix |
|-------|---------|----------|
| DOMParser | built-in | `npm install xmldom` |
| URL constructor | built-in | `require('url').URL` |
| Text encoding | automatic | `l5xBuffer.toString('utf8')` |
| CORS | not applicable | set Express CORS headers |
| Web Workers | available | not needed (single-threaded); use cluster if needed |

---

**When done:** Update `src/analyzer.js` to remove the mock and the `throw` in production.
