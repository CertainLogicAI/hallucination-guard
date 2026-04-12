# API Authentication — Best Practices

For REST APIs serving programmatic clients:

## Method: Bearer Token (API Key)

```
Authorization: Bearer <key>
```

Simplest, widely supported, works with curl and CI/CD.

## Key Management

- **Generation:** Random 32-char hex or base64
- **Storage:** Hashed in database (bcrypt/argon2) — never plaintext
- **Rotation:** Allow users to create new keys, revoke old ones
- **Per-user quota:** Track usage by API key (not IP)

## Rate Limiting

- **Unauthenticated:** By IP, strict (10 req/15min)
- **Authenticated:** By API key, generous (100–1000 req/15min depending on tier)

## Security

- Always use HTTPS
- Set short token lifetimes? (usually not — keys are long-lived until revoked)
- Log key usage (timestamp, endpoint, IP) for audit
- Alert on anomalies (sudden spike, foreign IP)

## Error Responses

- `401 Unauthorized` — missing or invalid key
- `429 Too Many Requests` — rate limit exceeded, include `Retry-After` header

## Implementation

OpenClaw agent uses `ALLOWED_API_KEYS` env or `api_keys.txt` for simple setups. For production, integrate with a user database and key management UI.

---
*Canonical reference. Do not edit without updating dependents.*
