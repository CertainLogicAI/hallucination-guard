# SERVICE AGREEMENT

This Service Agreement ("Agreement") is between **Deterministic AI** ("Provider") and **<Client Name>** ("Client").

## 1. Services

Provider will deliver the services described in the attached **Statement of Work** ("SOW"), including:
- Reference Curation
- Agent Build (deterministic AI)
- Validation & Go‑Live
- Ongoing Support (if selected)

## 2. Deliverables

Provider will deliver:
- `workspace-cache.json` (reference corpus)
- Custom AI agent (Docker image or deployed service)
- `TEST_REPORT.json` (validation test results)
- Documentation and training materials

## 3. Payment

Client agrees to pay the fees specified in the SOW:
- 50% upfront upon signing
- 50% upon successful validation and go‑live

Ongoing Support is billed annually in advance (15% of base build fee).

## 4. Intellectual Property

- **Client owns** all source documents, content, and any data provided.
- **Client owns** the final agent deployment package once paid in full.
- **Provider retains** IP in the underlying deterministic AI stack (workspace cache client, guardrail logic).
- Provider grants Client a perpetual, worldwide license to use the stack as part of the delivered agent.

## 5. Warranties

Provider warrants:
- Agent will operate as described: responses are validated against the provided reference corpus.
- No hallucination will occur for queries that have sufficient reference coverage (as measured by the validation test plan).
- Agent will respect the token budget and not exceed configured limits.
- Delivery timeline met, or Provider will credit 5% of fee per week of delay (max 25%).

**Exclusions:** Provider is not responsible for:
- Inaccurate or incomplete reference documents supplied by Client.
- Queries outside the reference corpus (agent will respond with refusal).
- Third‑party infrastructure failures (e.g., client's Redis instance).

## 6. Confidentiality

Both parties agree to protect each other's confidential information. Provider will not exfiltrate Client's documents; all processing occurs on infrastructure controlled by Client (or Provider's secure env with Client approval).

## 7. Support & Maintenance

If Ongoing Support is purchased, Provider will:
- Apply security patches to agent stack (within 30 days of release)
- Assist with reference updates (up to 4 hours/month)
- Provide monthly uptime report
- Respond to critical issues within 4 business hours

## 8. Limitation of Liability

Provider's total liability under this Agreement shall not exceed the total fees paid by Client. Provider shall not be liable for indirect, incidental, or consequential damages.

## 9. Termination

- Either party may terminate for material breach with 30 days notice.
- Upon termination, Client must cease using the agent; Provider may revoke license to the stack.
- Client retains ownership of their reference corpus and may redeploy with another vendor.

## 10. Governing Law

This Agreement is governed by the laws of <State/Country>.

---

**Signatures**

___________________________  
Deterministic AI (Provider)  
Date: _______________

___________________________  
<Client Name> (Client)  
Date: _______________

---

## Attachment A: Statement of Work

**Project Name:** ____________________  
**Scope:** As described in sections 1–4 above.  
**Fees:** $____________________  
**Timeline:** ____________________

**Exclusions:**  
- Provision of client documents (Client responsibility)  
- Infrastructure hosting costs (unless part of deployment)  
- Third‑party LLM API costs (billed to Client's account)  
- Client‑side support (training end users)

**Change Orders:** Any scope change >20% requires written change order with adjusted fee and timeline.
