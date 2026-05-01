# Hallucination Guard v2.0

> ⚠️ **DRAFT — Pending personal review and explicit approval by Anton before publication.** Per CertainLogic Claim Verification Policy v1.0.

Catches hedging language before it reaches users. Flags "maybe," "I think," and "not sure" so you can review low-confidence responses.

---

## What This Is

A **confidence-pattern detector** for AI-generated text. It scans responses for uncertainty language and flags them for human review.

**Like a spell-checker for confidence** — it catches obvious hedging, not factual errors.

---

## What It Does vs. What It Doesn't

| ✅ It Does | ❌ It Does NOT |
|-----------|---------------|
| Flags "maybe", "I think", "not sure", "probably" | Verify if a statement is factually true |
| Catches speculation about future events | Detect confident falsehoods (e.g., "The moon is made of cheese" stated confidently) |
| Provides a quick quality check before shipping | Replace human review |
| Works offline, zero dependencies | Connect to external APIs or databases |

---

## What You Get

| Feature | What It Means |
|---------|-------------|
| 🚀 **Instant check** | Paste text, get result in milliseconds |
| 🎯 **Pattern-based** | Catches 18+ uncertainty and speculation patterns |
| 🔒 **Privacy-first** | Runs locally. No data leaves your machine |
| 📦 **Zero dependencies** | Pure Python. No pip install needed |
| 🔧 **Cache gate** | Integration helper: allows or blocks caching based on confidence |

---

## Honest Limitations

| Limitation | What That Means |
|------------|----------------|
| **Pattern-based only** | Only catches phrases in our list. Novel hedging (e.g., "I'm 60% certain") slips through |
| **Not a fact-checker** | "Toronto is Canada's capital" (confidently stated) would PASS. It checks confidence, not truth |
| **Best effort** | No guarantees. Useful for catching obvious issues, not subtle ones |
| **English only** | Patterns tuned for English text |

---

## Quick Start

### One-line install (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/v2.0.0/scripts/install.sh | bash
```

That's it. `hguard` is now in your PATH.

### Or download manually

```bash
curl -fsSL -o install.sh https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/v2.0.0/scripts/install.sh
bash install.sh
```

### Or drop in the single file

The entire tool is one self-contained Python file. Zero dependencies.

```bash
curl -fsSL -o hguard https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/v2.0.0/scripts/hguard.py
chmod +x hguard
python3 hguard "I think the answer is 42"
```

### Or install via ClawHub (when published)

```bash
clawhub install hallucination-guard
```

---

## Usage

### CLI

```bash
# After one-line install:
hguard "I think the answer is 42, but maybe not"
# → ⚠️ FLAGGED
# → Contains uncertainty: i think, maybe

hguard "The capital of France is Paris"
# → ✅ CLEAN
# → No uncertainty patterns detected. (Note: confident falsehoods still pass.)

# JSON output for automation
hguard --json "Possibly the best solution"

# Check a file
hguard --file response.txt
```

### Python API

```python
from hguard import HallucinationGuard

guard = HallucinationGuard()

# Basic check
result = guard.check("I think this might work")
print(result["clean"])        # False
print(result["uncertainty"])  # ['i think', 'might']

# Cache gate
result = guard.gate_cache("The answer is probably 5")
print(result["allow_cache"])  # False
print(result["warning"])      # ⚠️ Contains uncertainty...
```

---

## When to Use This

**Good for:**
- Pre-publication quality check on AI-generated content
- Preventing uncertain responses from entering your knowledge base/cache
- Building confidence-based routing (e.g., "flagged → send to human review")

**Not for:**
- Fact-checking critical medical, legal, or financial information
- Replacing domain-expert review
- Catching sophisticated misinformation stated confidently

---

## License

MIT-0 — use freely, no attribution required.

---

*CertainLogic builds honest tools. We tell you exactly what they do, what they don't do, and where the edges are.*
