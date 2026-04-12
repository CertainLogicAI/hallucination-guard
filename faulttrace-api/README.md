---
summary: "\"FaultTrace API — Quickstart\""
read_when: ["["faulttrace", "api"]"]
---
# FaultTrace API — Quickstart

## Setup

```bash
cd /data/.openclaw/workspace/faulttrace-api
npm install
```

## Configuration

Create `.env` (from example):

```bash
cp .env.example .env
# Edit .env: set ALLOWED_API_KEYS, FAULTRACE_PORT, etc.
```

Key environment variables:
- `FAULTRACE_PORT` — server port (default 9876)
- `ALLOWED_API_KEYS` — comma-separated API keys (or use `api_keys.txt`)
- `CORS_ORIGIN` — allowed CORS origins (default `*`)
- `REDIS_URL` — Redis connection string (for caching)
- `NODE_ENV` — `development` enables mock analyzer; `production` requires real analyzer
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` — for billing (optional)

## Run (Local)

```bash
# Development (with auto-reload - requires nodemon or similar)
npm run dev

# Production (no auto-reload)
npm start
```

## Docker (Recommended for Production)

```bash
# Build and run with Docker Compose (includes Redis)
docker-compose up -d

# View logs
docker-compose logs -f faulttrace-api

# Stop
docker-compose down
```

The stack includes:
- `faulttrace-api` (your service)
- `redis` (caching)
- Health checks and restart policies

**Note:** The container entrypoint waits for Redis to be ready before starting.

## Test

### Using curl

```bash
# Without auth (should be 401)
curl -X POST http://localhost:9876/api/v1/analyze \
  -F "file=@test/fixtures/sample.l5x"

# With valid API key (200 + JSON)
curl -X POST http://localhost:9876/api/v1/analyze \
  -H "Authorization: Bearer dev-test-key-123" \
  -F "file=@test/fixtures/sample.l5x" | jq .
```

### Using the test script

```bash
# Make sure server is running, then:
node test-integration.js
```

Tests: health, no auth, invalid key, valid key, rate limiting.

## Health Check

```bash
curl http://localhost:9876/health
```

## API Specification

**Endpoint:** `POST /api/v1/analyze`

**Content-Type:** `multipart/form-data` with field `file` (must be `.l5x`)

**Headers:** `Authorization: Bearer <api-key>`

**Response:** JSON

```json
{
  "metadata": {
    "fileName": "program.l5x",
    "fileSize": 12345,
    "analyzerVersion": "0.1.0",
    "analyzedAt": "2025-03-27T12:34:56.789Z",
    "requestId": null,
    "ip": "127.0.0.1"
  },
  "summary": {
    "totalRungs": 42,
    "totalTags": 15,
    "warnings": 3,
    "errors": 0,
    "info": 0
  },
  "issues": [
    {
      "id": "unused-tag-001",
      "severity": "warning",
      "rule": "UnusedTag",
      "message": "Tag Motor_Start is declared but never used",
      "location": { "rung": 1, "instructionIndex": 3 },
      "suggestion": "Remove declaration or use in logic"
    }
  ],
  "ioMap": {
    "inputs": [],
    "outputs": []
  },
  "tags": [
    { "name": "Motor_Start", "type": "BOOL", "used": false },
    { "name": "Motor_Run", "type": "BOOL", "used": true }
  ]
}
```

## Rate Limits

- **Unauthenticated (by IP):** 10 requests per 15 minutes
- **Authenticated (by API key):** 100 requests per 15 minutes

Configure via `RATE_LIMIT_TRIAL` and `RATE_LIMIT_AUTHED` env vars (e.g., `15m`, `1h`).

## Caching

- Enabled in production (`NODE_ENV=production`) with Redis
- Cache key: SHA256 hash of L5X file
- TTL: 24 hours
- Bypass with query `?force=1` on `/analyze`

## Next Steps

### Immediate (Week 1)
1. **Port FaultTrace analyzer** from browser to Node (see `PORTING.md`)
2. Test with real L5X files (goal: <5s for 4k-rung files)
3. Remove mock data from `src/analyzer.js` (currently throws in production)

### Phase 2 (Week 2-3)
- [x] API key authentication (done)
- [x] Rate limiting (done)
- [x] Docker + Redis (done)
- [ ] Deploy to VPS (Hostinger)
- [ ] Set up HTTPS (Nginx + Let's Encrypt)

### Phase 3 (Week 4+)
- Stripe integration (webhook handler already scaffolded)
- Usage metering (track per-API-key counts)
- Customer portal (manage keys, view usage)
- Web dashboard (upload + visualize reports)
- Team features (multiple keys, shared quota)

---
**Important:** The current `analyzeL5XBuffer` uses a mock in development and throws in production. You must port the real analyzer before deploying to production. See `PORTING.md`.

*API spec: `/api/v1/analyze` (multipart/form-data, field `file`)*
*Webhooks: `/webhooks/stripe` (raw JSON, Stripe-Signature header)*
