# Compliance & Security

CertainLogic Verifier is designed for regulated environments from the ground up.

## Audit Trail

Every validation is logged to append-only JSONL with **SHA-256 hash chaining**:

```json
{
  "timestamp": "2026-04-21T10:30:00Z",
  "query_hash": "sha256:abc123...",
  "result": "valid",
  "confidence": 1.0,
  "previous_hash": "sha256:def456...",
  "chain_hash": "sha256:789ghi..."
}
```

Each entry references the previous entry's hash, creating a tamper-evident chain. Any modification to historical records breaks the chain and is immediately detectable.

## Data Residency

- **Zero data exfiltration** — no external API calls after deployment
- Runs entirely in your VPC, private cloud, or air-gapped network
- No telemetry, no analytics, no phone-home
- All data stays on your infrastructure

## Regulatory Frameworks

### HIPAA

- No PHI leaves your network
- Audit logging with immutable hash chain
- Access controls via API key authentication
- Cache clearing supports data lifecycle management

### GDPR

- Full data locality (EU hosting supported)
- Right to erasure: `DELETE /cache` clears all cached data
- Transparency: deterministic rules are inspectable
- No third-party data processors

### SOC2

- Security: self-hosted, no external dependencies
- Availability: Kubernetes deployment with health checks and replicas
- Processing integrity: deterministic validation, same input → same output
- Audit trail: SHA-256 chained logs

### FedRAMP

- Air-gapped deployment supported
- No external network dependencies
- SBOM provided for supply chain transparency
- Network policies block all egress

## Software Bill of Materials (SBOM)

Generate an SBOM for your deployment:

```bash
pip install cyclonedx-bom
cyclonedx-py environment -o sbom.json --format json
```

## Security Reporting

Found a vulnerability? See [SECURITY.md](https://github.com/CertainLogicAI/hallucination-guard/blob/main/SECURITY.md) for responsible disclosure.
