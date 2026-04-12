#!/usr/bin/env bash
# scaffold-test-harness.sh — Generate a test harness + fault injector for an analyzer
# Usage: scaffold-test-harness.sh <analyzer-dir>
# Example: scaffold-test-harness.sh ./my-analyzer
set -euo pipefail

ANALYZER_DIR="${1:?Usage: scaffold-test-harness.sh <analyzer-dir>}"

if [ ! -f "$ANALYZER_DIR/rule-engine.js" ]; then
  echo "❌ No rule-engine.js found in $ANALYZER_DIR. Run scaffold-parser.sh first."
  exit 1
fi

# Extract rule IDs from rule-engine.js
RULES=$(grep -oP "rule:\s*'([A-Z_]+)'" "$ANALYZER_DIR/rule-engine.js" | grep -oP "'[A-Z_]+'" | tr -d "'" | sort -u)

echo "Found rules: $RULES"

cat > "$ANALYZER_DIR/test-harness.js" << 'TESTEOF'
/**
 * Test Harness — Validates rule detection with positive and negative cases.
 *
 * Each test creates a minimal synthetic project and verifies that:
 *   - Positive case: rule detects the issue
 *   - Negative case: rule does NOT false-positive on clean input
 *
 * Run: node test-harness.js
 */

const RuleEngine = require('./rule-engine.js');

let passed = 0;
let failed = 0;
const failures = [];

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✅ ${name}`);
  } catch (e) {
    failed++;
    failures.push({ name, error: e.message });
    console.log(`  ❌ ${name}: ${e.message}`);
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || 'Assertion failed');
}

function makeProject(overrides) {
  return {
    metadata: { name: 'test' },
    sections: [],
    symbols: [],
    xref: {},
    ...overrides,
  };
}

function findingsByRule(results, ruleId) {
  return results.findings.filter(f => f.rule === ruleId);
}

console.log('══════════════════════════════════════════════════════════════');
console.log('TEST HARNESS');
console.log('══════════════════════════════════════════════════════════════\n');

// ─── DUPLICATE_OUTPUT ───────────────────────────────────────────────
test('Duplicate output: same symbol 2 locations', () => {
  const project = makeProject({
    xref: {
      'MyOutput': [
        { section: 'Main', item: 'Routine1', line: 1, access: 'write' },
        { section: 'Main', item: 'Routine2', line: 5, access: 'write' },
        { section: 'Main', item: 'Routine1', line: 2, access: 'read' },
      ]
    }
  });
  const results = RuleEngine.analyze(project);
  const f = findingsByRule(results, 'DUPLICATE_OUTPUT');
  assert(f.length === 1, `Expected 1 finding, got ${f.length}`);
});

test('Duplicate output: single write = OK', () => {
  const project = makeProject({
    xref: {
      'MyOutput': [
        { section: 'Main', item: 'Routine1', line: 1, access: 'write' },
        { section: 'Main', item: 'Routine1', line: 2, access: 'read' },
      ]
    }
  });
  const results = RuleEngine.analyze(project);
  const f = findingsByRule(results, 'DUPLICATE_OUTPUT');
  assert(f.length === 0, `Expected 0 findings, got ${f.length}`);
});

// ─── UNUSED_SYMBOL ──────────────────────────────────────────────────
test('Unused symbol: declared not referenced', () => {
  const project = makeProject({
    symbols: [{ name: 'OldTag', type: 'BOOL', scope: 'global' }],
    xref: {}
  });
  const results = RuleEngine.analyze(project);
  const f = findingsByRule(results, 'UNUSED_SYMBOL');
  assert(f.length === 1, `Expected 1 finding, got ${f.length}`);
});

test('Unused symbol: referenced = OK', () => {
  const project = makeProject({
    symbols: [{ name: 'ActiveTag', type: 'BOOL', scope: 'global' }],
    xref: { 'ActiveTag': [{ section: 'Main', item: 'R1', line: 1, access: 'read' }] }
  });
  const results = RuleEngine.analyze(project);
  const f = findingsByRule(results, 'UNUSED_SYMBOL');
  assert(f.length === 0, `Expected 0 findings, got ${f.length}`);
});

// TODO: Add tests for each rule in your rule engine.
// Pattern: positive test (must detect) + negative test (must NOT detect)

// ─── RESULTS ────────────────────────────────────────────────────────
console.log('\n══════════════════════════════════════════════════════════════');
console.log(`RESULTS: ${passed} passed, ${failed} failed out of ${passed + failed}`);
if (failures.length > 0) {
  console.log('\nFAILURES:');
  failures.forEach(f => console.log(`  ❌ ${f.name}: ${f.error}`));
}
console.log('══════════════════════════════════════════════════════════════');

process.exit(failed > 0 ? 1 : 0);
TESTEOF

# --- Batch runner ---
cat > "$ANALYZER_DIR/scripts/run-all-files.sh" << 'BATCHEOF'
#!/usr/bin/env bash
# Run analysis on all test files and show aggregate results
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="$SCRIPT_DIR/test-files"

if [ ! -d "$TEST_DIR" ] || [ -z "$(ls "$TEST_DIR" 2>/dev/null)" ]; then
  echo "No test files in $TEST_DIR. Add sample files first."
  exit 1
fi

node -e "
const fs = require('fs');
const Parser = require('$SCRIPT_DIR/parser.js');
const RuleEngine = require('$SCRIPT_DIR/rule-engine.js');

const dir = '$TEST_DIR';
const files = fs.readdirSync(dir).filter(f => !f.startsWith('.'));

let tc = 0, tw = 0, ti = 0, errors = 0;
const ruleCounts = {};

files.forEach(file => {
  const content = fs.readFileSync(dir + '/' + file, 'utf8');
  try {
    const project = Parser.parse(content);
    const results = RuleEngine.analyze(project);
    tc += results.summary.critical;
    tw += results.summary.warning;
    ti += results.summary.info;
    results.findings.forEach(f => {
      ruleCounts[f.rule] = (ruleCounts[f.rule] || 0) + 1;
    });
    console.log('✅ ' + file + ': ' + results.summary.total + ' findings');
  } catch(e) {
    console.log('❌ ' + file + ': ' + e.message.substring(0, 80));
    errors++;
  }
});

console.log('');
console.log('=== TOTALS (' + files.length + ' files) ===');
console.log('Parse errors: ' + errors);
console.log('🔴 Critical: ' + tc);
console.log('🟡 Warning:  ' + tw);
console.log('🔵 Info:     ' + ti);
console.log('Total:       ' + (tc + tw + ti));
console.log('');
console.log('=== BY RULE ===');
Object.entries(ruleCounts).sort((a,b) => b[1]-a[1]).forEach(([rule, count]) => {
  console.log('  ' + rule.padEnd(30) + count);
});
"
BATCHEOF

chmod +x "$ANALYZER_DIR/scripts/run-all-files.sh"

echo ""
echo "✅ Test harness created in $ANALYZER_DIR/"
echo ""
echo "Files created:"
echo "  test-harness.js           — Unit tests (4 starter tests for 2 rules)"
echo "  scripts/run-all-files.sh  — Batch runner for real file testing"
echo ""
echo "Run tests:  node $ANALYZER_DIR/test-harness.js"
echo "Run batch:  bash $ANALYZER_DIR/scripts/run-all-files.sh"
echo ""
echo "Add tests for each rule you create — positive AND negative cases."
