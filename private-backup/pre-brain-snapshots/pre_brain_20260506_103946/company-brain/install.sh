#!/usr/bin/env bash
set -e

echo "=== CertainLogic Deterministic Brain - Beta Install ==="

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 required"
    exit 1
fi

# Install dir
INSTALL_DIR="${CERTAINLOGIC_BRAIN:-$PWD/certainlogic-brain}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "Installing to: $PWD"

# Download latest
REPO="https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/cleanup_complete/company-brain"

curl -fsSL "$REPO/deterministic_brain.py" > deterministic_brain.py || {
    echo "ERROR: Could not download deterministic_brain.py"
    exit 1
}
curl -fsSL "$REPO/crypto_provenance.py" > crypto_provenance.py || {
    echo "ERROR: Could not download crypto_provenance.py"
    exit 1
}
curl -fsSL "$REPO/install.sh" > install.sh 2>/dev/null || true

# Data dir
mkdir -p data/intent

# .env
cat > .env << 'EOF'
CERTAINLOGIC_DATA=./data
CERTAINLOGIC_MASTER_KEY=
GBRAIN_PATH=
EOF

echo ""
echo "=== INSTALLED ==="
echo "Quick start:"
echo "  export CERTAINLOGIC_DATA=./data"
echo "  python3 -c \"import sys; sys.path.insert(0, '.'); from deterministic_brain import DeterministicBrain; print('Ready')\""
echo ""
echo "Next: Create an intent and start writing signed pages."
echo "Docs: https://github.com/CertainLogicAI/hallucination-guard/blob/cleanup_complete/docs/QUICKSTART.md"