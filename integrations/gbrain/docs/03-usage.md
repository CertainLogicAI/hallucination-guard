# Usage Examples

## Example 1: Verifying a News Article

**Scenario:** User shares a TechCrunch article about a Series B raise.

### Without CYL-verify

```
User: "Did you see Acme AI raised $50M?"
Agent: "Yes, according to the article you shared, Acme AI raised $50M
         from Sequoia Capital. [Source: article you shared]"

# Problem: The article might be wrong, outdated, or from a low-credibility source.
# GBrain writes this to compiled truth as-is.
```

### With CYL-verify

```
User: "Did you see Acme AI raised $50M?"
Agent: "Let me verify that claim before adding it to your brain."

Agent (internal):
  → cyl-verify: "Did Acme AI raise $50M?"
  → brain_api_query: { answer: "Yes, $50M Series B",
                         confident: true, method: "facts" }
  → Fact validated with high confidence.

Agent: "Confirmed. Acme AI raised $50M Series B from Sequoia Capital
         according to multiple sources [Source: CertainLogic validated,
         TechCrunch 2026-03-15, SEC filing 2026-03-18]."

# GBrain writes this to compiled truth with validation badge.
# Audit log records: task_id=..., entity="Acme AI", result="validated",
# method="facts", source="TechCrunch/SEC"
```

## Example 2: Catching a Hallucination During Enrich

**Scenario:** Enriching a person page, AI claims they worked at Google.

### Without CYL-verify

```
Brain page (compiled truth):
"Sarah Chen is a partner at Sequoia Capital. Previously worked at
 Google and Stanford. [Source: LinkedIn]"

# Problem: LinkedIn might list Google if the person briefly interned there,
# but this is misleading for a partner-level VC. The AI might hallucinate
# "Stanford" if the person went to UC Berkeley.
```

### With CYL-verify

```
Agent (internal):
  → extract: "Sarah Chen worked at Google"
  → cyl-verify: "Did Sarah Chen work at Google?"
  → brain_api_query: { answer: "No public record of Google employment",
                         confident: false, method: "uncertain" }
  → guard: "LinkedIn shows no Google in employment history"
  → Decision: UNCERTAIN

Agent (internal):
  → extract: "Sarah Chen attended Stanford"
  → cyl-verify: "Did Sarah Chen attend Stanford University?"
  → brain_api_query: { answer: "Attended UC Berkeley for undergrad",
                         confident: true, method: "facts" }
  → Decision: REJECTED (contradicts fact)

Brain page (compiled truth):
"Sarah Chen is a partner at Sequoia Capital. [Source: Sequoia website]
 Education: UC Berkeley (undergraduate). [Source: CertainLogic validated]"

Timeline entry:
"2026-04-21 | AI enrichment attempted:
  - [UNVERIFIED] Google employment
  - [REJECTED] Stanford attendance (attended UC Berkeley instead)"

Audit log:
  task_id=xyz, entity="Sarah Chen", claim="worked at Google",
  result="uncertain", reason="no source found"
  task_id=xyz, entity="Sarah Chen", claim="attended Stanford",
  result="rejected", correct_fact="UC Berkeley", method="facts"
```

## Example 3: Monthly Maintenance Sweep

**Scenario:** Running the maintain skill to catch stale compiled truth.

### Without CYL-verify

```
maintain skill:
  → find stale pages (>90 days since last update)
  → check for broken backlinks
  → done

# Problem: A fact written 3 months ago might now be wrong.
# "Acme AI has 50 employees" was true in Jan 2026, but now they have 200.
# GBrain has no way to detect this.
```

### With CYL-verify

```
maintain skill:
  → find stale facts in compiled truth (>90 days old)
  → for each: cyl_verify(fact)

  Example:
  → Fact: "Acme AI has 50 employees" (written 2026-01-15)
  → cyl-verify: "How many employees does Acme AI have?"
  → brain_api_query: { answer: "Acme AI reported 200 employees in
                                March 2026 SEC filing",
                         confident: true, method: "facts" }
  → Old fact STALE → update compiled truth
  → New fact: "Acme AI has 200 employees as of March 2026
               [Source: CertainLogic validated, SEC filing S-1]"
  → Audit log: task_id=..., entity="Acme AI", old_claim="50 employees",
    new_claim="200 employees", result="updated", reason="stale fact"

  → 12 facts updated, 3 facts unchanged, 1 fact removed
    (company acquired, no longer exists)
```

## Example 4: Investment Due Diligence

**Scenario:** Using gbrain for startup research before a pitch meeting.

### Without CYL-verify

```
User: "Remind me about Acme AI before my meeting."
Agent: "Acme AI — founded 2022, $50M raised, 10x performance over GPT-4,
         founded by ex-Google researchers. [Source: compiled truth]"

# Problem: The "10x over GPT-4" claim might be marketing fluff.
# The "ex-Google" claim might be overstated.
# You walk into the meeting with inflated expectations.
```

### With CYL-verify

```
User: "Remind me about Acme AI before my meeting."
Agent: "Acme AI — verified facts and open questions:

  ✅ Confirmed:
     - Founded 2022, San Francisco [Source: CertainLogic validated, SEC]
     - Raised $50M Series B led by Sequoia [Source: CertainLogic validated, TechCrunch]
     - Team includes former Google Brain researchers [Source: CertainLogic validated]

  ⚠️ UNVERIFIED (flagged in timeline):
     - '10x performance over GPT-4' — no independent benchmark found.
       Acme's own blog claims this, but no third-party verification.
       [See: timeline entry 2026-03-01]

  ❌ CORRECTED (was in compiled truth, now flagged):
     - Previously listed 'co-founded by Sarah Chen' — Sarah Chen is
       the Sequoia partner who led the round, not a co-founder.
       [Corrected: 2026-04-21]

  💡 Recommend asking: independent benchmark results, burn rate, team size."

# You walk into the meeting with calibrated expectations.
```

## Example 5: Fact-Checking a Quote

**Scenario:** User claims "Sam Altman said AGI by 2027."

### Without CYL-verify

```
User: "Sam Altman said AGI by 2027, right?"
Agent: "Yes, Sam Altman has mentioned AGI timelines around 2027."

# Problem: Sam Altman never said "by 2027." He said "sometime in the
# 2030s" or "hard to predict." The user's claim is wrong.
# GBrain confirms the user's bias.
```

### With CYL-verify

```
User: "Sam Altman said AGI by 2027, right?"
Agent: "Let me check that exact claim."

Agent (internal):
  → cyl-verify: "Did Sam Altman say AGI will arrive by 2027?"
  → brain_api_query: { answer: "No. In November 2025, Altman said
                                'I'm not confident in any specific year.
                                 I think the 2030s is a reasonable guess
                                 for when things get really interesting.'",
                         confident: true, method: "facts" }
  → Decision: REJECTED (user's claim is false)

Agent: "Actually, that's incorrect. Sam Altman has NOT said AGI by 2027.
        In November 2025, he said: 'I'm not confident in any specific
        year. I think the 2030s is a reasonable guess.' [Source:
        CertainLogic validated, Interview with Lex Fridman, 2025-11-12]

        Would you like me to update your brain to correct this?"

# GBrain catches the error. User's brain stays accurate.
# Audit log: claim rejected, corrected_fact provided.
```

## Example 6: Batch Import with Validation

**Scenario:** Importing 50 articles from an RSS feed.

### Without CYL-verify

```
User: "Import my AI news folder."
Agent: "Processing 50 articles... Done. 47 pages created."

# Problem: Hundreds of unverified claims now in compiled truth.
# "Google launched Gemini 2.5" (maybe true)
# "OpenAI revenue hit $5B" (maybe outdated)
# "Mistral raised $640M" (maybe wrong amount)
```

### With CYL-verify

```
User: "Import my AI news folder."
Agent: "Processing 50 articles with fact validation... Done.

  📊 Results:
     - 47 pages created
     - 312 facts extracted
     - ✅ 189 facts validated (CertainLogic confirmed)
        → written to compiled truth
     - ⚠️ 67 facts uncertain (no source found)
        → written to timeline as UNVERIFIED
     - ❌ 56 facts rejected (contradicted existing knowledge)
        → flagged for review

  🔄 Next: Review 56 rejected facts + uncertain claims?"

Audit log: 312 entries written, all with timestamps and fact hashes.
```

## Example 7: Handling Contradictions

**Scenario:** Two sources give different revenue numbers.

### Without CYL-verify

```
Article 1 (Jan): "Acme AI revenue: $10M ARR"
Article 2 (Apr): "Acme AI revenue: $50M ARR"

Brain compiled truth: "$50M ARR" (last write wins)
# Problem: The $50M might be cumulative lifetime, not ARR.
# Or Article 2 might be wrong.
```

### With CYL-verify

```
Article 1 (Jan): "Acme AI revenue: $10M ARR"
→ cyl-verify: "$10M ARR" → validated, source=Bloomberg

Article 2 (Apr): "Acme AI revenue: $50M ARR"
→ cyl-verify: "$50M ARR" → uncertain (no source)
  → guard: "Article 2 says 'total revenue since founding' not 'ARR'"
  → Decision: REJECTED for compiled truth, but noted in timeline

Brain compiled truth:
"$10M ARR as of Jan 2026 [Source: CertainLogic validated, Bloomberg]
 Timeline: 2026-04-10 | Article claims $50M total revenue — context
 unclear, possibly cumulative. [UNVERIFIED]"

Audit log:
  task_id=abc, claim="$10M ARR", result="validated"
  task_id=abc, claim="$50M ARR", result="rejected",
  reason="context mismatch — cumulative vs ARR"
```

## Workflow Summary

| User Action | GBrain Skill | CYL-verify | Result |
|---|---|---|---|
| Share article | idea-ingest | Extract + validate facts | Verified facts → compiled truth |
| Mention person | enrich | Check claims | Accurate person page |
| Ask question | query | Validate before answering | Confident answer with sources |
| Import batch | ingest | Batch validation | Stats: validated/uncertain/rejected |
| Run maintenance | maintain | Re-validate old facts | Stale facts updated |

## Anti-Patterns to Avoid

1. **Don't validate everything** — personal opinions, subjective judgments, and "best practices" don't need CYL-verify. Use it for objective facts.

2. **Don't block on uncertain** — if a fact can't be validated, write it to the timeline as UNVERIFIED. The brain still captures it.

3. **Don't trust "Guard validated" blindly** — Guard catches hallucinations but can still be wrong. Always prefer `facts` method over `llm` method.

4. **Don't skip audit logging** — even "validated" facts should be logged. The audit trail is your proof of due diligence.
