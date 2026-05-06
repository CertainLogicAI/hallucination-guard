# Beta Landing Page Deployment Guide

## What Was Built

### Files Added

| File | Purpose |
|------|---------|
| `src/pages/beta.astro` | Astro page for beta signup |
| `public/api/beta/signup` | Static fallback (returns success message) |
| `functions/api/beta/signup.js` | Cloudflare Worker for real signup handling |

### Features

- **Landing page** at `/beta` with:
  - Hero section with value prop
  - 4 feature cards (HMAC, Hash, Intent, Audit)
  - Signup form (email, name, company, product, use case, GitHub)
  - Form validation + success state
  - Footer with links

- **API endpoint** at `/api/beta/signup`:
  - Stores signups to Cloudflare KV
  - Sends email notification via Resend
  - Rate limiting (planned)
  - CORS enabled

## Deployment Steps

### Step 1: Build the Site

```bash
cd certainlogic-site
npm run build
```

Creates `dist/` with all static files.

### Step 2: Deploy to Cloudflare Pages

**Option A: Git Integration (Recommended)**
1. Push to GitHub
2. In Cloudflare dashboard: Pages → Create project
3. Connect GitHub repo
4. Build settings:
   - Framework preset: Astro
   - Build command: `npm run build`
   - Build output: `dist`
5. Add environment variables:
   - `RESEND_API_KEY` (optional — for email notifications)
6. Deploy

**Option B: Direct Upload**
1. Cloudflare dashboard → Pages → Create project
2. Choose "Direct upload"
3. Upload `dist/` folder
4. Set environment variables in dashboard

### Step 3: Configure KV Store

1. Cloudflare dashboard → KV
2. Create namespace: `beta_signups`
3. In Pages project settings → Functions → KV namespace bindings
4. Add binding:
   - Variable name: `BETA_KV`
   - KV namespace: `beta_signups`

### Step 4: Set Up Resend (Optional)

For email notifications:

1. Sign up at resend.com
2. Verify domain: certainlogic.ai
3. Get API key
4. Add to Cloudflare Pages environment variables:
   - Name: `RESEND_API_KEY`
   - Value: `re_...`

### Step 5: Set Up Email

1. Cloudflare dashboard → Email → Email Routing
2. Enable Email Routing
3. Add route: `beta@certainlogic.ai` → your personal email
4. Update DNS MX records (Cloudflare auto-adds them)

### Step 6: DNS Record

Add `beta.certainlogic.ai` as a CNAME or A record pointing to your Cloudflare Pages deployment.

In Cloudflare DNS:
```
Type: CNAME
Name: beta
Target: your-pages-project.pages.dev
```

## Testing

After deployment, test the full flow:

```bash
# Test API directly
curl -X POST https://beta.certainlogic.ai/api/beta/signup \
  -H "Content-Type: application/json" \
  -d '{
    "product": "deterministic-brain",
    "email": "test@example.com",
    "name": "Test User",
    "company": "Test Co",
    "use_case": "Medical compliance",
    "github_username": "testuser"
  }'

# Expected response:
# {"success": true, "id": "uuid", "message": "Thanks! Check your email..."}
```

## Monitoring

Check signups in Cloudflare dashboard:
- KV namespace "beta_signups"
- Or run local script to fetch:

```bash
# TBD: Add script to export KV data
```

## Next Steps

1. [ ] Deploy to Cloudflare Pages
2. [ ] Configure KV namespace
3. [ ] Set up Resend API key
4. [ ] Add DNS record for beta.certainlogic.ai
5. [ ] Test end-to-end signup flow
6. [ ] Add beta page link to main nav (`src/components/Header.astro`)
7. [ ] Monitor signups via KV dashboard

## Future Enhancements

- [ ] Admin dashboard at `/beta/admin`
- [ ] Auto-onboarding email sequence
- [ ] Signup analytics (weekly reports)
- [ ] A/B test landing page copy
- [ ] Add testimonials/social proof
