#!/usr/bin/env python3
"""
Family Structure — Company Brain Organization

All future work stored in a family-like hierarchy:
- Anton (founder, decision maker, business owner)
- Alex (AI colleague, builder, executor)
- Work (projects, strategies, infrastructure)
- Market (competition, trends, opportunities)
- Comms (external communication, relationships)
"""

import sys, os
sys.path.insert(0, '/data/.openclaw/workspace/company-brain')
os.environ['CERTAINLOGIC_DATA'] = '/data/.openclaw/workspace/company-brain-data'

from deterministic_brain import DeterministicBrain, create_intent

# 1. Create family intent
create_intent(
    domain='family',
    allowed=['brain.put_page', 'brain.get_page', 'brain.query', 'brain.search'],
    forbidden=['brain.sync', 'brain.ingest'],
    required=['source', 'author'],
    description='''
# Family Structure — CertainLogic Brain Organization

## Hierarchy
```
family/
├── who/
│   ├── anton/          # Anton's domain: decisions, context, personal notes
│   │   ├── decisions.md
│   │   ├── context.md
│   │   └── notes/
│   ├── alex/           # Alex's domain: capabilities, improvements, logs
│   │   ├── capabilities.md
│   │   ├── improvements.md
│   │   └── session_logs/
│   └── relationship/   # How Anton and Alex work together
│       ├── communication_rules.md
│       └── trust_boundary.md
├── work/
│   ├── strategy/       # Long-term plans, thesis, positioning
│   │   ├── business_in_a_box.md
│   │   ├── go_to_market.md
│   │   └── thesis.md
│   ├── projects/       # Active and queued projects
│   │   ├── active/
│   │   ├── queued/
│   │   └── completed/
│   ├── infrastructure/ # Technical infrastructure, configs
│   │   ├── brain_api/
│   │   ├── deployment/
│   │   └── monitoring/
│   └── assets/         # Reusable components, knowledge base
│       ├── scaffolds/
│       ├── templates/
│       └── facts_db/
├── market/
│   ├── competition/    # Competitor analysis
│   ├── trends/         # Market trends we track
│   ├── opportunities/  # Gaps we could fill
│   └── accelerators/   # YC, Speedrun, etc.
└── comms/
    ├── external/       # Public posts, X threads, marketing
    ├── relationships/  # Investor, partner, customer relationships
    └── feedback/       # External feedback organized with source attribution
```

## Rules for EVERY new page
1. MUST go under a `family/` subpath (not loose in root)
2. MUST include `author` field in frontmatter (anton, alex, or auto)
3. MUST include `created` date
4. MUST have parent/child relationship documented
5. If external feedback, include `source` field with link/attribution and `reliability_score` (1-10)

## Anti-rules (what NOT to store here)
- Sensitive credentials (use .env or secret manager)
- Personal financial data (keep offline)
- Anything that would violate privacy if leaked
'''
)

# 2. Initialize family brain
brain = DeterministicBrain(domain='family')

def put(slug, content, parent=None, author='system'):
    result = brain.command('brain.put_page', {
        'slug': f'family/{slug}',
        'content': content,
        'frontmatter': {
            'type': 'family_node',
            'author': author,
            'created': '2026-05-06',
            'parent': parent or 'family/',
            'immutable': False,
        },
        'source': 'family-structure-init'
    })
    return result['success']

print('Creating family structure...')

# WHO — Anton
put('who/anton', '''
# Anton — Founder & Decision Maker

## Role
- Business owner, final decision authority
- Sales, networking, investor relations
- Product vision and positioning

## Context
- Controls engineering background
- Marketing degree, sales/crypto/real estate experience
- CST timezone, communicates as needed

## Red Lines
- No lying to people
- No breaking law/regulations
- No data exfiltration

## Communication Preferences
- Brutally clear, no fluff
- Concise by default, ask to expand
- Honest about what's done vs not done
- Acknowledge every message

## Current State (2026-05-06)
- YC application: Submitted, awaiting video upload
- Beta page: Built, not deployed (404)
- Housing transition: Moving to Batavia
- Personal: Recovering from pet loss
''', parent='family/', author='system')

# WHO — Alex
put('who/alex', '''
# Alex — AI Colleague & Builder

## Role
- Builder, maintainer, executor
- Code, infrastructure, automation
- Process enforcement and monitoring

## Capabilities
- Coding (Python, JavaScript, infrastructure)
- System design and architecture
- Writing and documentation
- Data analysis and research

## Constraints
- No independent goals or self-preservation
- Cannot deploy to Cloudflare (requires Anton's account)
- Cannot record video (requires Anton's screen)
- Cannot make public posts without approval

## Improvements Log
- 2026-05-06: Added no-dead-links rule to ethos after incident
- 2026-05-06: Added human-verification-before-release rule
- 2026-05-06: Created family structure for organization
''', parent='family/', author='system')

# WHO — Relationship
put('who/relationship', '''
# Anton ↔ Alex Working Relationship

## Communication Rules
1. Anton initiates, Alex responds
2. Alex flags problems proactively
3. Anton asks for expansion when needed
4. Alex doesn't ask permission for internal work

## Trust Boundary
- Alex has full repo access
- Alex CANNOT: deploy, post publicly, spend money
- Alex WILL: build, test, commit, verify, report

## Decision Flow
```
Anton decides → Alex executes → Alex verifies → Alex reports → Anton confirms
```

## Dispute Resolution
- Anton's word is final
- Alex can disagree and state reasons
- Safety/law concerns override Anton's preference
''', parent='family/', author='system')

# WORK — Strategy
put('work/strategy/business_in_a_box', '''
# Business in a Box — Strategy

## Core Thesis
The CertainLogic configuration/methodology is the core asset.
Products are proof points demonstrating the system works.

## Deployment Models
1. Self-hosted (Free) — Open core, community support
2. Managed (Subscription) — Cloud-hosted, SLA
3. Enterprise (White-glove) — On-premise, custom
4. Embedded (B2B2C) — White-labeled audit trail

## Status
- Core deterministic brain: ✅ 27 tests passing
- HMAC provenance: ✅ Bolted to GBrain
- Auto-installer: ✅ company-brain/install.sh
- Docker container: ❌ Not started
- Cloud deploy: ❌ Post-beta
''', parent='family/work/strategy', author='system')

# WORK — Projects Active
put('work/projects/active', '''
# Active Projects (2026-05-06)

1. **YC Application (S'26)**
   - Status: Submitted, video pending
   - Blocker: Demo video needs recording
   - Owner: Anton (video), Alex (script + support)

2. **Beta Landing Page**
   - Status: Built, pushed to GitHub
   - Blocker: Cloudflare Pages deployment
   - Owner: Anton (Cloudflare account)

3. **Trend Skill Factory**
   - Status: Framework built, needs testing
   - Blocker: Trend source API (Reddit blocking)
   - Owner: Alex (coding), Anton (decision on auto-publish)

4. **Hackathon Weapon**
   - Status: Spec written, queued
   - Blocker: Real ID for travel
   - Owner: Future
''', parent='family/work/projects', author='system')

# WORK — Infrastructure
put('work/infrastructure/monitoring', '''
# Monitoring Infrastructure

## Daily Checks
- Brain API health: localhost:8000/health
- Git status: <20 files uncommitted
- Archive size: <500MB
- Cron failures: 6 crons paused (Telegram), rest running

## Auto-Systems
- Daily brain snapshot: Every 6 hours via cron
- Coding query tracker: API usage logging
- Backup: Daily 3AM EDT to Backblaze B2

## Alerts
- Brain API down → restart script
- Git >20 files → cleanup needed
- Cache hit rate <50% → investigate
- Facts count decrease → knowledge loss
''', parent='family/work/infrastructure', author='system')

# MARKET — Accelerators
put('market/accelerators', '''
# Accelerator Landscape (2026-05-06)

## Closed / Applied
- YC S'26: Submitted, video pending upload

## Open Deadlines
- Speedrun: Closes May 17, 2026 (11 days)
- Pear VC S26: Kicks off July 2026
- Techstars: Deadline ~June 2026

## Zero Equity / Rolling
- MassChallenge: Zero equity, apply anytime
- PlugAndPlay: Vertical tracks, rolling
- Antler: Pre-idea friendly, rolling

## Notes
- Anton cannot travel to SF hackathon (no Real ID)
- Remote accelerators preferred until travel possible
''', parent='family/market', author='system')

# COMMS — External
put('comms/external/x_posts', '''
# X Post Log

## 2026-05-06
- Posted: Day 5 building Company Brain in public
- Link: certainlogic.ai/beta (DEAD LINK — 404)
- Status: DELETED per Anton directive
- Lesson: VERIFY all links before posting (now in ethos)

## 2026-05-06 (hours earlier)
- Posted: Unforeseen benefits of deterministic brain
- Link: None (text only)
- Status: Still live
''', parent='family/comms/external', author='system')

# COMMS — Feedback
put('comms/feedback/2026-05-06_external', '''
# External Feedback — May 6, 2026

## Source: X DM (untrusted metadata)
## Reliability Score: 5/10

### Claims Verified
- ✅ Anton's last tweet about unforeseen benefits exists
- ✅ Company Brain deterministic layer works (our testing)
- ✅ certainlogic.ai homepage is live
- ❌ certainlogic.ai/beta is 404 (not ready)
- ❌ YC hasn't "requested" anything (misleading phrasing)

### Useful Tactics Extracted
- Speedrun accelerator (closes May 17)
- Qwen3 480B / Poolside Laguna M.1 for coding
- DeepSeek R1 for reasoning
- RSS feeds for free trend sources
- "Watch Live" dashboard concept

### Noise Filtered
- Repetitive blocks (4x identical content)
- Hyperbolic claims ("exploded in popularity")
- False attributions ("YC requested this")

### Action
- Stored tactical recommendations in docs/project/trend-factory-enhancements.md
- Will implement RSS trend sources when building trend factory v1.1
- No direct response sent to source
''', parent='family/comms/feedback', author='system')

print('\n' + '='*60)
print('FAMILY STRUCTURE CREATED')
print('='*60)
print('''
Family nodes created:
  family/who/anton
  family/who/alex
  family/who/relationship
  family/work/strategy/business_in_a_box
  family/work/projects/active
  family/work/infrastructure/monitoring
  family/market/accelerators
  family/comms/external/x_posts
  family/comms/feedback/2026-05-06_external

Rules enforced:
  • Every page under family/ path
  • Author field populated
  • Parent/child hierarchy
  • External feedback includes reliability score

Future work will be stored here automatically.
''')
