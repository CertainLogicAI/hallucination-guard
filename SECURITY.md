# Security Policy

## Supported Versions

Only the latest major release receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in hallucination‑guard, please report it privately:

- **Email**: ops@certainlogic.ai
- **PGP Key**: Not yet available; we will provide on request.

**Do not disclose the vulnerability publicly until we have fixed it and released a patch.**

We will acknowledge receipt within 48 hours and provide a timeline for assessment and patch.

## Security Practices

- All code contributions are reviewed for security implications.
- The project uses deterministic verification and does not execute arbitrary user‑supplied code.
- The facts database (`facts_db.json`) is read‑only and can be inspected before deployment.
- SQLite cache (token‑reduction engine) is isolated per instance and can be purged via `/cache` endpoint.

## Dependencies

We keep dependencies minimal and regularly audit them using `safety` and `pip-audit`. Known vulnerabilities are patched within 7 days of disclosure.

## Security Updates

Security patches are released as patch versions (e.g., `0.1.1`). Users are encouraged to upgrade promptly.