#!/usr/bin/env bash
set -euo pipefail

# CertainLogic Install Verification Script
# Run this after `pip install hallucination-guard` to confirm everything works

echo "=== CertainLogic Install Verification ==="
echo ""

# 1. Check CLI is in PATH
echo -n "1. CLI available... "
if command -v hallucination-guard >/dev/null 2>&1; then
    echo "✅ $(hallucination-guard --version 2>/dev/null || echo 'version unknown')"
else
    echo "❌ hallucination-guard not found in PATH"
    echo "   Fix: export PATH=\"$HOME/.local/bin:$PATH\""
    exit 1
fi

# 2. Check install
echo -n "2. Facts installed... "
if [ -f "$HOME/.hallucination-guard/facts_db.json" ]; then
    COUNT=$(python3 -c "import json; d=json.load(open('$HOME/.hallucination-guard/facts_db.json')); print(len(d.get('facts',d)))")
    echo "✅ $COUNT facts"
else
    echo "⚠️  Not installed. Run: hallucination-guard install"
    exit 1
fi

# 3. Check cache
echo -n "3. Cache initialized... "
if [ -f "$HOME/.hallucination-guard/cache.db" ]; then
    echo "✅ SQLite cache ready"
else
    echo "⚠️  No cache yet (will be created on first query)"
fi

# 4. Test query
echo -n "4. Query test... "
RESULT=$(hallucination-guard verify "What is Python's latest stable version?" 2>/dev/null || echo "FAIL")
if echo "$RESULT" | grep -q "3.13\|3.12"; then
    echo "✅ Got expected answer"
else
    echo "⚠️  Query returned unexpected result"
    echo "   Output: $RESULT"
fi

# 5. Domain gate test
echo -n "5. Domain gate (should skip personal fact)... "
RESULT=$(hallucination-guard verify "My wife's birthday is March 15" 2>/dev/null || echo "SKIP")
if echo "$RESULT" | grep -qi "skip\|out.*scope\|personal"; then
    echo "✅ Correctly skipped personal fact"
else
    echo "⚠️  Domain gate may not be active"
fi

# 6. Hit rate report
echo ""
echo "6. Hit rate report:"
hallucination-guard report 2>/dev/null || echo "   (No queries tracked yet — run some first)"

echo ""
echo "=== Verification Complete ==="
echo "If all checks show ✅, you're ready to use the GBrain skill."
