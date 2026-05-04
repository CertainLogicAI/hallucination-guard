# AgentPathfinder Cost of Execution

**Date:** 2026-04-25
**Status:** Pre-launch cost analysis

---

## Monthly Operational Costs (Real)

### Infrastructure

| Item | Provider | Cost | Notes |
|------|----------|------|-------|
| Web server (landing + dashboard) | Hetzner CX31 (4 vCPU/16GB) | **$13.60/mo** | Runs everything: site, dashboard, API proxy |
| Object storage (backups) | Backblaze B2 | **$0.10/mo** | 20GB @ $0.005/GB + download fees |
| Domain (certainlogic.ai) | Cloudflare | **$1/mo** | $12/year |
| CDN + DDoS | Cloudflare Free | **$0** | Unlimited bandwidth |
| SSL certificates | Let's Encrypt | **$0** | Auto-renewing |
| Email (notifications) | Resend free tier | **$0** | 3K emails/mo |
| **Infrastructure Total** | | **~$15/mo** | |

### Payment Processing

| Item | Rate | Impact |
|------|------|--------|
| Stripe fees | 2.9% + $0.30/transaction | On every paid signup/renewal |
| Example: $29 Pro signup | $1.14 | Net revenue: $27.86 |
| Example: $79 Business signup | $2.59 | Net revenue: $76.41 |
| Churn protection (dunning) | Stripe built-in | $0 extra |
| **Payment Total** | Variable | ~$1-3 per transaction |

### Development / Maintenance

| Item | Cost | Notes |
|------|------|-------|
| Your time | $0 cash | You're building, not hiring |
| CI/CD (GitHub Actions) | **$0** | Public repo = unlimited free minutes |
| Monitoring (UptimeRobot) | **$0** | Free tier: 50 monitors |
| Error tracking (Sentry) | **$0** | Free tier: 5K errors/mo |
| Analytics (Plausible self-host) | **$0** | Runs on same Hetzner box |
| **DevOps Total** | **$0** | |

---

## Cost Per User Tier

### Free Users (500+)
| Resource | Per User | 500 Users | Cost |
|----------|----------|-----------|------|
| Storage (task JSON + audit) | ~50KB | 25MB | Negligible |
| Compute | Local only | N/A | $0 |
| Bandwidth | Site only | Cached by CDN | $0 |
| **Total per user** | | | **~$0.0003/mo** |

### Pro Users ($29/mo)
| Resource | Per User | 40 Users (mo 12) | Cost |
|----------|----------|------------------|------|
| Dashboard storage | ~100KB | 4MB | Negligible |
| Report generation | CPU burst | Shared server | Included |
| Audit retention (90 days) | ~200KB/user | 8MB | Negligible |
| **Total per user** | | | **~$0.02/mo** |
| **Margin** | | | **$27.84/user net** |

### Business Users ($79/mo)
| Resource | Per User | 12 Users (mo 12) | Cost |
|----------|----------|------------------|------|
| Remote vault (S3/B2) | ~500KB | 6MB | Negligible |
| Webhook delivery | ~1K requests | 12K/mo | Negligible |
| Team sync | Minimal | Shared server | Included |
| **Total per user** | | | **~$0.15/mo** |
| **Margin** | | | **$76.26/user net** |

### Enterprise Users ($299+/mo)
| Resource | Cost |
|----------|------|
| On-prem deployment | $0 (their infrastructure) |
| Custom support | Your time |
| **Margin** | **~95%+** |

---

## Breakeven Analysis

| Scenario | MRR needed | Users needed | Months to break even |
|----------|-----------|--------------|---------------------|
| Server costs only ($15/mo) | $15 | 1 Pro user | Immediate |
| Server + 10 hrs dev/mo @ $50/hr | $515 | 18 Pro users | ~3 months |
| Server + 20 hrs dev/mo @ $50/hr | $1,015 | 35 Pro users | ~4 months |
| Full-time (160 hrs) @ $50/hr | $8,015 | 287 Pro users | ~12 months |

**Reality check:** At $15/mo infrastructure, you need **1 Pro user** to be profitable. Everything else is your time.

---

## Scaling Costs (What If It Grows)

| Milestone | Users | Infrastructure Change | Monthly Cost |
|-----------|-------|----------------------|--------------|
| 100 Pro users | 100 | Same Hetzner box | $15 |
| 500 Pro users | 500 | Upgrade to CPX31 ($26) | $26 |
| 1000 Pro users | 1000 | CPX51 ($52) or 2× CPX31 | $52 |
| 5000 Pro users | 5000 | Dedicated server ($100) + load balancer | $100 |
| 10K+ Pro users | 10K+ | Kubernetes cluster ($200+) | $200+ |

**Key insight:** This is a compute-light product. Filesystem sharding + JSONL audit trails are almost free to store and process. You could serve 10K users on a $100/mo server.

---

## Hidden Costs (Don't Forget)

| Item | Cost | Mitigation |
|------|------|------------|
| Chargebacks | $15/dispute + $0.30 | Clear refund policy, good docs |
| Tax collection (VAT/GST) | Stripe Tax auto-handles | 0.5% fee on transactions |
| Accountant (year-end) | $500/year | Use Stripe reports, simple structure |
| Trademark filing | $350-500 | Do it only after $1K MRR |
| **Hidden Total** | Minimal | |

---

## Summary

| | Monthly Cost |
|--|-------------|
| **Bare minimum** (server + domain) | **$15** |
| **Comfortable** (server + domain + email + monitoring) | **$20** |
| **Scaling** (upgraded server + analytics + backup) | **$50** |

**To cover costs:** 1 Pro user = profitable.
**To quit your day job:** ~287 Pro users = $8K/mo net.
**To build a real business:** 1,000 Pro users = $27K/mo net.

This is a **high-margin, low-overhead** product. The main cost is your time building and marketing it.
