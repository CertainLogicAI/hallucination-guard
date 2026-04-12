#!/usr/bin/env bash
# scaffold-parser.sh — Generate a parser skeleton for a given file format
# Usage: scaffold-parser.sh <format-name> <file-extension> <output-dir>
# Example: scaffold-parser.sh plc-l5x l5x ./my-analyzer
set -euo pipefail

FORMAT_NAME="${1:?Usage: scaffold-parser.sh <format-name> <file-extension> <output-dir>}"
FILE_EXT="${2:?Provide file extension (e.g., l5x, json, xml, yaml, csv)}"
OUTPUT_DIR="${3:?Provide output directory}"

mkdir -p "$OUTPUT_DIR"/{test-files,scripts}

# Detect format family
case "$FILE_EXT" in
  xml|l5x|svg|html|xhtml|plist|csproj)
    FORMAT_FAMILY="xml" ;;
  json|jsonl|geojson)
    FORMAT_FAMILY="json" ;;
  yaml|yml)
    FORMAT_FAMILY="yaml" ;;
  csv|tsv)
    FORMAT_FAMILY="csv" ;;
  ini|conf|cfg|toml)
    FORMAT_FAMILY="config" ;;
  *)
    FORMAT_FAMILY="text" ;;
esac

echo "Scaffolding $FORMAT_NAME analyzer ($FORMAT_FAMILY format) in $OUTPUT_DIR..."

# --- Parser ---
cat > "$OUTPUT_DIR/parser.js" << 'PARSEREOF'
/**
 * PARSER_TITLE Parser
 * Parses PARSER_EXT files into a normalized project structure.
 *
 * Output: {
 *   metadata: { name, version, ... },
 *   sections: [{ name, items: [{ type, name, content, line }] }],
 *   symbols: [{ name, type, scope, value }],
 *   xref: { symbolName: [{ section, item, line, access: 'read'|'write' }] }
 * }
 */
const Parser = (function() {
  'use strict';

  function parse(content) {
    const startTime = performance.now();

    // TODO: Implement format-specific parsing
    PARSE_LOGIC

    const parseTime = performance.now() - startTime;

    const project = {
      metadata: {
        name: 'unknown',
        parseTimeMs: Math.round(parseTime),
      },
      sections: [],
      symbols: [],
      xref: {},
    };

    // TODO: Populate sections, symbols, xref from parsed data

    return project;
  }

  return { parse };
})();

if (typeof module !== 'undefined') module.exports = Parser;
PARSEREOF

# Replace placeholders based on format family
case "$FORMAT_FAMILY" in
  xml)
    PARSE_BLOCK="const parser = new DOMParser();
    const doc = parser.parseFromString(content, 'text/xml');
    const parseError = doc.querySelector('parsererror');
    if (parseError) throw new Error('XML parse error: ' + parseError.textContent.substring(0, 100));

    // TODO: Navigate the DOM tree to extract sections, symbols, cross-references
    // Example: const root = doc.documentElement;
    // const sections = root.querySelectorAll('YourSectionElement');"
    ;;
  json)
    PARSE_BLOCK="const data = JSON.parse(content);

    // TODO: Navigate the JSON structure to extract sections, symbols, cross-references"
    ;;
  yaml)
    PARSE_BLOCK="// Requires a YAML parser (e.g., js-yaml)
    // const yaml = require('js-yaml');
    // const data = yaml.load(content);

    // TODO: Navigate the YAML structure to extract sections, symbols, cross-references"
    ;;
  csv)
    PARSE_BLOCK="const lines = content.split('\\n');
    const headers = lines[0].split(',').map(h => h.trim());

    // TODO: Parse rows into structured records
    // const rows = lines.slice(1).map(line => { ... });"
    ;;
  *)
    PARSE_BLOCK="const lines = content.split('\\n');

    // TODO: Implement line-by-line or regex-based parsing"
    ;;
esac

sed -i "s|PARSER_TITLE|$FORMAT_NAME|g" "$OUTPUT_DIR/parser.js"
sed -i "s|PARSER_EXT|$FILE_EXT|g" "$OUTPUT_DIR/parser.js"
# Use a temp file for multiline replacement
TMPF=$(mktemp)
echo "$PARSE_BLOCK" > "$TMPF"
python3 -c "
import sys
with open('$OUTPUT_DIR/parser.js') as f: content = f.read()
with open('$TMPF') as f: replacement = f.read()
content = content.replace('PARSE_LOGIC', replacement)
with open('$OUTPUT_DIR/parser.js', 'w') as f: f.write(content)
"
rm -f "$TMPF"

# --- Rule Engine ---
cat > "$OUTPUT_DIR/rule-engine.js" << 'RULEEOF'
/**
 * RULE_TITLE Rule Engine
 * Analyzes parsed project for common issues.
 */
const RuleEngine = (function() {
  'use strict';

  function analyze(project) {
    const findings = [];

    // Run each rule
    findings.push(...checkDuplicateOutputs(project));
    findings.push(...checkUnusedSymbols(project));
    findings.push(...checkUnconditionalWrites(project));
    // TODO: Add more rules

    // Sort by severity
    const order = { critical: 0, warning: 1, info: 2 };
    findings.sort((a, b) => (order[a.severity] || 3) - (order[b.severity] || 3));

    return {
      findings,
      summary: {
        critical: findings.filter(f => f.severity === 'critical').length,
        warning: findings.filter(f => f.severity === 'warning').length,
        info: findings.filter(f => f.severity === 'info').length,
        total: findings.length,
      }
    };
  }

  // ─── RULE: Duplicate outputs ──────────────────────────────────────
  function checkDuplicateOutputs(project) {
    const findings = [];
    const writeLocations = {};

    for (const [symbol, refs] of Object.entries(project.xref)) {
      const writes = refs.filter(r => r.access === 'write');
      if (writes.length > 1) {
        findings.push({
          rule: 'DUPLICATE_OUTPUT',
          severity: 'critical',
          title: `Duplicate write to "${symbol}" in ${writes.length} locations`,
          description: `"${symbol}" is written in ${writes.length} places. ` +
            `Only the last-executed write takes effect — earlier writes are silently overwritten.`,
          locations: writes,
          recommendation: `Verify this is intentional. If not, consolidate writes to a single location.`,
        });
      }
    }
    return findings;
  }

  // ─── RULE: Unused symbols ────────────────────────────────────────
  function checkUnusedSymbols(project) {
    const findings = [];
    const referenced = new Set(Object.keys(project.xref));

    project.symbols.forEach(sym => {
      if (!referenced.has(sym.name)) {
        findings.push({
          rule: 'UNUSED_SYMBOL',
          severity: 'info',
          title: `Unused: ${sym.name}`,
          description: `"${sym.name}" (${sym.type}) is declared but never referenced in any logic.`,
          recommendation: `Remove if not needed, or verify it's referenced externally.`,
        });
      }
    });
    return findings;
  }

  // ─── RULE: Unconditional writes ──────────────────────────────────
  function checkUnconditionalWrites(project) {
    const findings = [];
    // TODO: Implement for your format
    // Check for writes (state mutations) with no conditions/guards
    return findings;
  }

  return { analyze };
})();

if (typeof module !== 'undefined') module.exports = RuleEngine;
RULEEOF

sed -i "s|RULE_TITLE|$FORMAT_NAME|g" "$OUTPUT_DIR/rule-engine.js"

# --- Trace Engine ---
cat > "$OUTPUT_DIR/trace-engine.js" << 'TRACEEOF'
/**
 * TRACE_TITLE Trace Engine
 * Backward dependency tracer — answers "why won't X work?"
 */
const TraceEngine = (function() {
  'use strict';

  function trace(project, targetSymbol, maxDepth) {
    maxDepth = maxDepth || 10;
    const visited = new Set();
    return traceSymbol(project, targetSymbol, 0, maxDepth, visited);
  }

  function traceSymbol(project, symbol, depth, maxDepth, visited) {
    if (depth >= maxDepth || visited.has(symbol)) {
      return { symbol, type: visited.has(symbol) ? 'circular' : 'max-depth' };
    }
    visited.add(symbol);

    const refs = project.xref[symbol] || [];
    const writes = refs.filter(r => r.access === 'write');
    const reads = refs.filter(r => r.access === 'read');

    if (writes.length === 0) {
      // No logic writes this — it's an external input or constant
      return { symbol, type: 'input', locations: reads };
    }

    // For each write location, find what conditions (reads) are on the same scope
    const dependencies = [];
    writes.forEach(w => {
      const sameScopeReads = reads.filter(r =>
        r.section === w.section && r.item === w.item
      );
      // TODO: Find OTHER symbols read in the same scope as this write
      // These are the dependencies that must be true for this write to execute
    });

    return {
      symbol,
      type: 'logic',
      writtenAt: writes,
      dependencies: dependencies.map(dep =>
        traceSymbol(project, dep, depth + 1, maxDepth, visited)
      ),
    };
  }

  return { trace };
})();

if (typeof module !== 'undefined') module.exports = TraceEngine;
TRACEEOF

sed -i "s|TRACE_TITLE|$FORMAT_NAME|g" "$OUTPUT_DIR/trace-engine.js"

echo ""
echo "✅ Scaffolded $FORMAT_NAME analyzer in $OUTPUT_DIR/"
echo ""
echo "Files created:"
echo "  parser.js       — Format parser (${FORMAT_FAMILY}-based)"
echo "  rule-engine.js  — Rule engine (3 starter rules)"
echo "  trace-engine.js — Backward dependency tracer"
echo ""
echo "Next steps:"
echo "  1. Add sample files to test-files/"
echo "  2. Implement parser.js TODOs for your format"
echo "  3. Run: node -e \"const P = require('./parser.js'); console.log(P.parse(require('fs').readFileSync('test-files/sample.${FILE_EXT}','utf8')))\""
echo "  4. Add domain-specific rules to rule-engine.js"
echo "  5. Build test harness (see scaffold-test-harness.sh)"
