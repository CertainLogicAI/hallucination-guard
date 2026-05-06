# Beta Infrastructure — CertainLogic

## Overview
Reusable beta program infrastructure. Not just for the Deterministic Brain — this system handles any product beta.

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Landing Page | `site/beta/landing.html` | Signup form (deployed to Cloudflare Pages) |
| Signup API | `scripts/beta_signup.py` | POST endpoint + validation |
| Onboarding | `scripts/beta_onboard.py` | Auto-send welcome + instructions |
| Tracking | `data/beta/signups.jsonl` | Append-only signup database |
| Analytics | `scripts/beta_metrics.py` | Daily/weekly beta stats |
| Docs | `docs/BETA_INFRASTRUCTURE.md` | This file |

## Data Model

```json
{
  "_id": "uuid",
  "product": "deterministic-brain",
  "email": "user@example.com",
  "name": "John Doe",
  "company": "Acme Inc",
  "use_case": "medical compliance",
  "submitted_at": 1778047200,
  "status": "pending|approved|onboarded|active|churned",
  "onboarded_at": null,
  "feedback_count": 0,
  "plan": "free|paid",
  "github_username": "johndoe",
  "notes": ""
}
```

## Flow

1. **User visits** `beta.certainlogic.ai` → fills form
2. **Form POSTs** to `/api/beta/signup` → validated → stored in `data/beta/signups.jsonl`
3. **Onboarding cron** runs hourly → sends welcome email to `pending` signups
4. **Admin dashboard** (`/beta/admin`) → view/manage signups
5. **Metrics** → weekly report on signups, activations, feedback

## Email Setup (External)

**beta@certainlogic.ai** → forward to anton@ (or a Notion/CRM integration)

Options:
- Google Workspace: $6/mo → admin.google.com
- Cloudflare Email Routing: FREE → cloudflare.com → Email → Email Routing
- ForwardEmail: $3/mo → forwardemail.net

**Recommendation:** Cloudflare Email Routing (free, already using Cloudflare for DNS)

Steps:
1. Add MX records in Cloudflare DNS
2. Create routing rule: beta@certainlogic.ai → your personal email
3. Done

## API Endpoints

### POST /api/beta/signup
```bash
curl -X POST https://certainlogic.ai/api/beta/signup \
  -H "Content-Type: application/json" \
  -d '{
    "product": "deterministic-brain",
    "email": "user@example.com",
    "name": "John Doe",
    "use_case": "enterprise compliance",
    "github_username": "johndoe"
  }'
```

Response:
```json
{"success": true, "id": "uuid", "message": "Thanks! Check your email."}
```

### GET /api/beta/stats
Admin only (API key required). Returns signup counts by status.

## Security

- Rate limit: 5 signups per IP per hour
- Email validation: MX record check
- Spam detection: honeypot field + timestamp analysis
- Admin endpoints: API key auth

## Future Products

To launch a new beta:
1. Update landing page: change product name + description
2. `scripts/beta_signup.py` → change `product` field
3. `scripts/beta_onboard.py` → customize welcome email per product
4. Same infrastructure, different content

## Files

```
data/beta/
  signups.jsonl          # All signup records
  signups_by_email.json  # Index: email → latest signup
  metrics/
    weekly_2026-05.json
    
scripts/
  beta_signup.py         # POST endpoint (Flask/FastAPI)
  beta_onboard.py        # Onboarding automation
  beta_metrics.py        # Weekly stats report
  
site/beta/
  landing.html           # Signup form
  admin.html             # Admin dashboard
  style.css
  
docs/
  BETA_INFRASTRUCTURE.md # This file
  BETA_QUICKSTART.md     # User-facing quickstart
```
