# MVP Safety Checklist

## ⚠️ Avoid Using Deterministic AI Layer for Code Generation

- **Do NOT** use this system for critical code generation, multi‑file debugging, or security‑sensitive programming tasks.
- The 200‑token input summarisation can discard essential variables, imports, or control‑flow information, leading to inaccurate or unsafe code suggestions.
- Even with a 1,500‑token output window, garbage‑in → garbage‑out still applies; always verify any code produced by the MVP system before integration.
- Preferred use‑cases: triage, pattern explanation, documentation assistance, and simple boilerplate snippets where the context fits within the summarised token budget.
