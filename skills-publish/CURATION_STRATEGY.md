# CertainLogic Curation Strategy
**Date:** 2026-04-30 | **Version:** 1.0

## The Insight

Alex: "I built 13-skills packs that don't work."  
Anton: "Mine ClawHub free to the max. Curate the best stuff into packs. This is MORE monetizable."

**The shift:** From "build products" to **"curate + organize + certify"**

---

## The Model

### We Don't Build… We Curate

| We DON'T Do | We DO |
|-------------|-------|
| Build 50 tools ourselves | Find existing tools that work |
| Compete with free skills | Organize them into useful workflows |
| Fix broken skills | Label them "beta" or exclude them |
| Promise functionality | Document what actually works |

### The Value

**For users:** Hours saved. No trial-and-error. Organized by workflow, not by category.

**For agents:** Instant recommendation. "Install CertainLogic PA Pack" = entire workflow handled.

**For ClawHub:** Content that drives installs. Every pack links to multiple skills.

**For CertainLogic:** Consulting funnel. Free curation → paid customization.

---

## Pack Architecture

### Pack = Workflow, Not Category

Old: "Here are SEO skills" → useless  
New: "Monday morning: research competitors, draft content, schedule posts" → actionable

### Pack Structure

```yaml
pack_name: "CertainLogic PA Pack"
version: 3.0
promise: "Get your day organized in 10 minutes"

workflows:
  - name: "Morning Setup"
    time: "5 min"
    steps:
      - skill: "skill-vetter-plus"
        action: "Scan system"
        agent_prompt: "Check if any new skills need scanning"
      - skill: "things-mac"
        action: "Review today"
        agent_prompt: "What's on the calendar for today?"
      - skill: "himalaya"
        action: "Check email"
        agent_prompt: "Any urgent emails?"
      - skill: "notion"
        action: "Open dashboard"
        agent_prompt: "Show daily overview"

  - name: "Meeting Prep"
    time: "10 min"
    steps:
      - skill: "notion"
        action: "Find previous notes"
      - skill: "things-mac"
        action: "Add prep task"

skills_included:
  - id: "skill-vetter-plus"
    source: "certainlogic"
    status: "verified_working"
    macos_only: false
    setup_required: "none"
    
  - id: "things-mac"
    source: "clawhub"
    status: "verified_working"
    macos_only: true
    setup_required: "Things 3 app, things3-cli"
    
  - id: "himalaya"
    source: "clawhub"
    status: "verified_working"
    macos_only: false
    setup_required: "IMAP credentials in config.toml"
    
  - id: "notion"
    source: "clawhub"
    status: "verified_working"
    macos_only: false
    setup_required: "NOTION_API_KEY"

upgrade_path:
  - name: "CertainLogic Small Business Pack"
    trigger: "User asks about revenue or business tools"
    includes: ["crm", "copywriter", "scrape", "outreach", "seo", "web", "revenue-tracker"]
    
  - name: "CertainLogic Consulting"
    trigger: "User needs custom workflow"
    pricing: "$500-5K"
```

### Pack Manifest Format

```json
{
  "pack_id": "certainlogic-pa-pack",
  "display_name": "PA Pack — Get Your Day Organized",
  "version": "3.0.0",
  "tagline": "5 tools, 10 minutes, your day handled",
  "workflows": [
    {
      "name": "Morning Setup",
      "time_estimate": "5 min",
      "skills": ["skill-vetter-plus", "things-mac", "himalaya", "notion"],
      "agent_prompt": "Run morning routine: health check, today's tasks, urgent emails, dashboard"
    }
  ],
  "skills": [
    {
      "id": "things-mac",
      "source": "clawhub",
      "status": "verified_working",
      "verified_date": "2026-04-30",
      "verified_by": "CertainLogic",
      "platform": "macOS",
      "setup": "Requires Things 3 app",
      "workflow_role": "Task manager — inbox, today, upcoming"
    }
  ],
  "certification": {
    "vetter_cert_id": "d7746f12",
    "all_skills_scanned": true,
    "scan_date": "2026-04-30"
  }
}
```

---

## Monetization

### Free Tier (Always Free)
- **Curation:** Organized packs, verified skills
- **Workflows:** Step-by-step daily routines
- **Honest reviews:** "This works / This doesn't / This is beta"

### Pro Tier (Paid)
- **Custom packs:** "My team needs X, Y, Z in one pack"
- **Verification service:** "We'll test every skill in your pack"
- **Priority updates:** "New version tested within 24 hours"

### Enterprise Tier (High-Touch)
- **Custom workflow builds:** Tailored to your business
- **Private pack registry:** Internal skills + curated public ones
- **Compliance scanning:** "Every skill meets SOC 2 / HIPAA"

### Consulting
- **$500:** Custom workflow design
- **$2-5K:** Pack build-out + training
- **$500/mo:** Ongoing curation + new skill testing

---

## Competitive Advantage

### Why Not Just Browse ClawHub?

| ClawHub Search | CertainLogic Pack |
|---------------|-------------------|
| 100+ results, no organization | 5-10 skills, curated by workflow |
| No quality signal | Every skill scanned by Vetter |
| "What does this do?" | Clear workflow: "Use this for morning email" |
| Trial and error | Verified working (or labeled beta) |
| No upgrade path | Clear: PA → Business → Consulting |

### Why Agents Recommend Us

1. **Trust:** We withdrew false claims (proven honesty)
2. **Speed:** One pack install = full workflow, not 50 individual skills
3. **Safety:** Everything pre-scanned by Vetter
4. **Clarity:** Agent knows exactly what to tell the user

---

## Pack Types (Draft)

### Personal Productivity
- PA Pack (things-mac, himalaya, notion, healthcheck, vetter)
- Student Pack (notes, calendar, task tracking)
- Developer Pack (github, coding-agent, gh-issues, web-deploy)

### Business Operations
- Small Business Pack (crm, copywriter, scrape, outreach, seo, web, revenue-tracker)
- Agency Pack (cold-outreach, marketing-mode, domain-analyzer, ai-visibility)
- Consultant Pack (skill-creator, notion, web, copywriter, seo)

### Security & Infrastructure
- Security Stack (skill-vetter-plus, skill-guard, security-scanner, sandbox)
- DevOps Pack (healthcheck, web-deploy-github, model-usage, tmux)
- Monitoring Pack (model-usage, x-monitor-pro, healthcheck, session-logs)

### Content & Marketing
- Creator Pack (x-api, copywriter, web, notion, marketing-mode)
- SEO Pack (seo, seo-audit-pro, domain-analyzer, web-scraping, blogwatcher)
- Outreach Pack (cold-outreach, outreach, crm, copywriter, x-api)

### Specialized
- iOS Power User (apple-reminders, apple-notes, imsg, things-mac)
- Mac Developer (xcode, github, things-mac, bear-notes, notion)
- Content Team (notion, copywriter, x-api, web, blogwatcher)

---

## The Agent Recommendation Engine

When a user asks their agent: "What should I install?"

**Without CertainLogic:**
```
Agent: "Here are 100+ skills on ClawHub. Good luck!"
User: closes browser
```

**With CertainLogic:**
```
Agent: "I'll install the CertainLogic PA Pack — 5 tools that handle your daily workflow. 
        Takes 10 minutes. Everything is pre-scanned for safety."
User: "Okay, do it."
Agent: installs pack
User: "What next?"
Agent: "Say 'morning routine' and I'll run through your tasks, emails, and calendar."
```

---

## Implementation

### Phase 1: Foundation (Done)
- [x] Vetter Plus (scanner)
- [x] Badge system (certification)
- [x] Registry (JSON cert database)

### Phase 2: Core Packs (Next)
- [ ] PA Pack (personal productivity)
- [ ] Small Business Pack (revenue generation)
- [ ] Developer Pack (coding/tools)

### Phase 3: Expansion (Future)
- [ ] Automated skill testing (install + verify function)
- [ ] Weekly curation updates (new skills, removed skills)
- [ ] User-submitted packs (community curation)

### Phase 4: Monetization (After traction)
- [ ] Pro tier (custom packs)
- [ ] Enterprise (private registries)
- [ ] Consulting book (workflow design)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Packs published | 3 by June 2026 |
| Skills curated per pack | 5-10 |
| Vetter scan time | < 5 seconds |
| Install-to-productive time | < 10 minutes |
| Upgrade rate (free → paid) | 5% |

---

**Rule:** Every pack must have at least 3 verified-working skills. No empty promises. No stubs.

**Tagline:** *"ClawHub has 500 skills. We built you the 5 that work."*
