# CertainLogic Deterministic Brain — Beta Program

## Quick Start (5 minutes)

```bash
# 1. Clone the installer
curl -fsSL https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/cleanup_complete/company-brain/install.sh | bash

# 2. Set up
cd certainlogic-brain
export CERTAINLOGIC_DATA=./data

# 3. Test import
python3 -c "import sys; sys.path.insert(0, '.'); from deterministic_brain import DeterministicBrain; print('Ready')"
```

## Your First Signed Page

```python
from deterministic_brain import DeterministicBrain, create_intent

# 1. Create intent (security policy)
create_intent(
    domain="myapp",
    allowed=["brain.put_page", "brain.get_page"],
    forbidden=["brain.sync"],
    required=["source"]
)

# 2. Initialize brain
brain = DeterministicBrain(domain="myapp")

# 3. Write (HMAC-signed automatically)
result = brain.command("brain.put_page", {
    "slug": "mydata/note-1",
    "content": "Important knowledge",
    "frontmatter": {"author": "you"},
    "source": "myapp"
})

print(result["hmac_signature"])  # Hex signature

# 4. Verify (hash + HMAC)
v = brain.verify("mydata/note-1")
print(v["hash_verified"])   # True
print(v["hmac_verified"])   # True
```

## What You Get

- ✅ Every write HMAC-signed (tamper-evident)
- ✅ SHA-256 hash verification (content integrity)
- ✅ Intent-based access control (security policy)
- ✅ Append-only audit trail (non-repudiation)
- ✅ Works with GBrain or standalone

## Beta Feedback

Open an issue or email: [beta@certainlogic.ai]

## License

MIT
