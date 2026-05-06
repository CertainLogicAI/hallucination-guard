# Beta Email Setup

## Goal
Set up `beta@certainlogic.ai` to receive signup notifications and support requests.

## Option 1: Cloudflare Email Routing (FREE - Recommended)

Already using Cloudflare for DNS. This is the easiest path.

### Steps

1. Log in to Cloudflare dashboard → certainlogic.ai
2. Go to **Email → Email Routing**
3. Enable Email Routing
4. Add destination addresses:
   - Add forwarding address (your personal email)
5. Create routing rule:
   - **Custom address:** `beta@certainlogic.ai`
   - **Action:** Forward to `anton@yourpersonalemail.com`

### DNS Records Needed (Cloudflare auto-adds these)
```
Type: MX
Name: @
Value: route1.mx.cloudflare.net (priority 13)
Value: route2.mx.cloudflare.net (priority 47)
Value: route3.mx.cloudflare.net (priority 71)
```

### SPF Record (prevents spam)
```
Type: TXT
Name: @
Value: "v=spf1 include:_spf.mx.cloudflare.net ~all"
```

**Done.** All emails to `beta@certainlogic.ai` forward to your inbox.

---

## Option 2: Google Workspace ($6/month)

More professional, full email management for *@certainlogic.ai.

### Steps
1. Go to workspace.google.com
2. Sign up for Business Starter ($6/user/month)
3. Verify domain ownership (add TXT record in Cloudflare)
4. Set up user: `anton@certainlogic.ai`, `beta@certainlogic.ai`
5. Add MX records (Google provides them)

**Pros:** Full Gmail, shared inboxes, calendar, docs
**Cons:** $6/month

---

## Option 3: ForwardEmail ($3/month)

Simple forwarding service with better deliverability than basic Cloudflare.

### Steps
1. Sign up at forwardemail.net
2. Add domain: certainlogic.ai
3. Add forwarding rule: `beta@certainlogic.ai` → your personal email
4. Update MX records in Cloudflare to ForwardEmail's servers

**Pros:** Better deliverability, supports multiple aliases
**Cons:** $3/month, another vendor to manage

---

## Recommendation

**For now: Option 1 (Cloudflare Email Routing - FREE)**

- Zero cost
- Already on Cloudflare
- Good enough for beta notifications
- Upgrade to Google Workspace later when revenue justifies it

**Next step:** Go to Cloudflare dashboard → Email → Email Routing → Enable

## Testing

After setup, test:
```bash
# Send test email
echo "Test" | mail -s "Beta Test" beta@certainlogic.ai

# Or use curl with our API
python3 scripts/beta_signup.py &
curl -X POST http://localhost:8001/api/beta/signup \
  -H "Content-Type: application/json" \
  -d '{"product":"deterministic-brain","email":"test@example.com"}'
```

## Future: SMTP for Outbound

When you want to SEND emails from `beta@certainlogic.ai` (welcome emails, etc.):

**Option A:** Use Cloudflare Workers + Resend.com (free tier: 100 emails/day)
**Option B:** Use Google Workspace SMTP (if on Option 2)
**Option C:** Use SendGrid/Mailgun (free tier usually 100-300 emails/day)

**For beta welcome emails:** Start with Resend.com (free, developer-friendly, good deliverability):
1. Sign up at resend.com
2. Verify domain: certainlogic.ai
3. Get API key
4. Update `BETA_EMAIL_SETUP.md` with API key location

Current placeholder in `beta_onboard.py` uses env vars for SMTP. Resend has a simple Python API:
```python
from resend import Resend
client = Resend(api_key="re_xxx")
client.emails.send({
    "from": "beta@certainlogic.ai",
    "to": "user@example.com",
    "subject": "Welcome to Beta",
    "text": "..."
})
```
