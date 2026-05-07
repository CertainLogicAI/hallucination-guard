# X Posting Gap — Strategic YC Risk

**Date:** 2026-05-07  
**Identified by:** Anton  
**Status:** Active gap, requires decision  
**Severity:** Medium-High for YC credibility

---

## The Gap

**Pipeline built:** Content engine generates posts daily at 6 AM CST.  
**Pipeline broken:** Content stored locally, never published to X.  
**Result:** Dormant @CertainLogicAI account.

| Component | Status | Detail |
|-----------|--------|--------|
| Content engine | ✅ `content-engine-daily` runs | Generates posts |
| X API | ✅ Tested 2026-05-06 | Successfully posted + deleted test |
| Credential file | ❌ `.x-api.json` not in workspace | May be in `skills/x-api/scripts/` or `/data/.openclaw/secrets/` |
| Posting scripts | ✅ `skills/x-api/scripts/x-post-file.mjs` | Works when executed |
| Cron execution | ✅ X posting crons run (lastRunStatus: ok) | But `delivery.mode: "none"` = reports only, no actual post |
| Anton approval | ⚠️ Gate exists but unused | Content generated, never reviewed by Anton |
| Public output | ❌ Zero posts | Account appears dormant |

## Why YC Cares

YC application lists @CertainLogicAI. Evaluators will check it.

| What YC Sees | What YC Thinks |
|--------------|----------------|
| Active posting | "Founder is engaged, building in public, getting feedback" |
| Sparse but intentional posting | "Founder is focused, not wasting time on social" |
| **Dormant account** | **"This might not be active. Are they really working on this?"** |
| Deleted/missing account | "Red flag" |

**Current state = dormant account = possible credibility hit.**

## What Content Exists (Unposted)

| File | Date | Status |
|------|------|--------|
| `content/x-post-today.txt` | 2026-05-06 | Generated, not posted |
| `content/x-teaser-may-06.md` | 2026-05-06 | Generated, not posted |
| (previous days) | Unknown | Likely exist unposted |

## The Fix Options

### Option A: Manual Cryptic Teaser Batch (Anton, ~15 min)
**Post 3-5 cryptic teasers immediately. Then pause.**
- Copy from generated content or write new
- "Day 5 of building the Company Brain in public" (already written, just post it)
- "Not all agent actions are created equal. Some need proof."
- "Deterministic agents don't hallucinate. They also don't disobey."
- "Your agent should say 'no' to you sometimes."

**Pros:** Shows signs of life, respects cryptic teaser strategy, no automation risk  
**Cons:** Manual effort, not sustainable without habit

### Option B: Enable Auto-Post for Teasers Only (Low-Risk Automation)
**Configure pipeline to auto-post ONLY content tagged `[TEASER]` or under certain character count/claim threshold.**
- Cryptic = no specific metrics, no "we shipped X on date", no URLs that might 404
- Everything else stays in `content/` awaiting Anton approval

**Pros:** Sustainable, shows consistent activity, filters for low-risk only  
**Cons:** Requires tagging logic, occasional misfire possible

### Option C: Weekly Manual Batch (Anton, ~10 min Sunday)
**Every Sunday, review the week's generated content. Pick 2-3. Approve. Agent posts them spread across the week.**
- Anton maintains control
- No daily pressure
- Content bank grows between reviews

**Pros:** Balanced control vs. output, respects Anton's schedule  
**Cons:** Batch might feel stale if news breaks

### Option D: Status Quo (Do Nothing)
**Accept dormant account risk. Focus on YC application strength in other areas.**

**Pros:** Zero risk of bad posts, zero time investment  
**Cons:** YC may interpret as low engagement; missed chance to build audience before beta

## Recommended Path

**Hybrid: Option A + C**
1. **Today:** Anton manually posts the May 6 "Day 5" content (already written, brain-captured). Shows immediate signs of life.
2. **Going forward:** Weekly Sunday batch review. Anton picks 2-3 from the week. Agent schedules them across the next 7 days.
3. **Exception:** If major milestone happens (self-alignment event, beta launch), Anton tweets manually with approval but fast.

This respects:
- Brain capture policy (all drafted content already stored)
- Anton's approval gate (he picks what goes public)
- Cryptic teaser strategy (teasers are low-risk, don't need verification)
- Training period (no daily firehose, manageable commitment)

## Action Required

| Step | Owner | When |
|------|-------|------|
| Confirm X API credential location | Alex | Immediate |
| Anton manually posts 1-2 existing teasers | Anton | When ready |
| Agent stores "teaser" vs "claim" tagging in content pipeline | Alex | Next session |
| Set weekly Sunday review reminder | Alex | After Anton confirms schedule |

---

**Bottom line:** The pipeline works. The content exists. The API is tested. The only missing step is Anton pressing "post" — or giving Alex permission to auto-post low-risk teasers.
