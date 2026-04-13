#!/bin/bash
# Seed the deterministic cache with project knowledge
API="http://127.0.0.1:8000/facts"
H="Content-Type: application/json"

post() { curl -s -X POST "$API" -H "$H" -d "$1" > /dev/null; }

# Products
post '{"key":"deterministic ai product 1","type":"string","value":"Agent/SMB tier: LLM responses pass hallucination filter then get cached. Future matching queries served from cache at zero token cost. Hallucination rate above 2% but acceptable for general use. Value prop: massive token savings as cache fills.","source":"anton/architecture"}'
post '{"key":"deterministic ai product 2","type":"string","value":"Regulated/compliance tier: Known facts database with pre-validated authoritative data. Queries validated against facts cache. Can run with zero LLM dependency. Targeting sub-2% hallucination rate. For regulated industries (medical, financial, industrial).","source":"anton/architecture"}'
post '{"key":"faulttrace product","type":"string","value":"FaultTrace: 3 modes - Troubleshoot (L5X + fault -> wire-level diagnosis), Build (parts list -> PLC program via L5X writer), Draft (parts list -> electrical schematics SVG). Client-side parsing, nothing leaves browser. Target: industrial automation, controls engineers.","source":"project docs"}'
post '{"key":"faulttrace domain","type":"string","value":"faulttrace.ai","source":"project docs"}'
post '{"key":"faulttrace architecture","type":"string","value":"Client-side browser app. L5X files parsed in browser via DOMParser. Zero network calls for analysis. AI features use extracted snippets only. Privacy: nothing leaves your browser.","source":"project docs"}'
post '{"key":"faulttrace test results","type":"string","value":"29/29 test files passed. Largest: 7.8MB java-parser-test.L5X (30 programs, 413 routines, 11995 rungs, 30716 cross-refs) parsed in 2.5s.","source":"memory/2026-03-22.md"}'

# Pricing
post '{"key":"faulttrace pricing","type":"string","value":"Not finalized. Discussion range: $99/mo Starter, $499/mo Professional, $2499/mo Enterprise ($30K/yr). Enterprise displaces $124K+ in headcount. Anton thinks $500/yr is too cheap - industrial software is $5K-15K/seat.","source":"anton/memory/2026-03-24.md"}'
post '{"key":"skills pricing","type":"string","value":"Individual premium skills: $19 each. Business Starter Bundle: $59 launch price (normally $76). Sold via Gumroad (blenderismai.gumroad.com) and own website (blenderism.github.io).","source":"memory/2026-03-22.md"}'

# Business
post '{"key":"clawhub account","type":"string","value":"@blenderism on ClawHub","source":"project docs"}'
post '{"key":"gumroad store","type":"string","value":"https://blenderismai.gumroad.com/","source":"memory/2026-03-22.md"}'
post '{"key":"website","type":"string","value":"blenderism.github.io - GitHub Pages hosted, Stripe for payments (2.9% vs Gumroad 10%)","source":"memory/2026-03-22.md"}'
post '{"key":"shopclawmart","type":"string","value":"ShopClawMart.com - premium skills sales platform","source":"project docs"}'
post '{"key":"certainlogic","type":"string","value":"CertainLogic.ai - brand for deterministic AI patent and products","source":"patent docs"}'
post '{"key":"competitor felix","type":"string","value":"Felix CEO persona ($99) - all-in-one persona product. We sell specialized working tools, not personas. Different market positioning.","source":"memory/2026-03-21.md"}'

# Patent
post '{"key":"patent status","type":"string","value":"Provisional patent drafted: Deterministic Query Processing System with Hash-Verified Local Execution and Hybrid LLM Routing. 10 claims. Filed under CertainLogic.ai. Core complete, needs drawings inserted for EFS-Web submission.","source":"patent_filings/"}'
post '{"key":"patent ip protection","type":"string","value":"No prior art posted for token reduction engine or deterministic layer. Trade secret protection maintained. Patent eligibility preserved. All implementation details confidential.","source":"memory/2026-03-31-no-prior-art.md"}'

# Technical
post '{"key":"deterministic ai hallucination rate","type":"numeric","value":"0.8","unit":"%","source":"patent_filings/validated_patent_application.md"}'
post '{"key":"deterministic ai token reduction","type":"numeric","value":"85","unit":"%","source":"patent_filings/validated_patent_application.md"}'
post '{"key":"deterministic ai cache hit rate","type":"numeric","value":"38","unit":"%","source":"patent_filings/validated_patent_application.md"}'
post '{"key":"token engine throughput","type":"string","value":"464,550 queries/sec on stress test. 20,000 queries in 0.04s. 99.9% cache hit rate on repeat queries.","source":"memory/2026-03-31.md"}'

# Skills built
post '{"key":"premium skills list","type":"string","value":"Skill Audit Pro ($19), Cold Outreach Pro ($19), Market Research Pro ($19), SEO Audit Pro ($19), AI Visibility Pro, X Monitor Pro, Domain Analyzer Pro. 25 total skills (6 premium Pro versions).","source":"memory/2026-03-22.md"}'

# Anton
post '{"key":"anton background","type":"string","value":"Controls engineering background. Builds and commissions industrial automation equipment. Familiar with Allen-Bradley, Studio 5000, ladder logic, structured text.","source":"conversations"}'
post '{"key":"anton timezone","type":"string","value":"CST","source":"USER.md"}'
post '{"key":"anton telegram","type":"string","value":"@ForCryptoClearly (ID: 1381429689)","source":"USER.md"}'

# Strategy
post '{"key":"business funnel","type":"string","value":"Agent tech (free/cheap, high volume) -> SMB market (same product, packaged for cost savings) -> Regulated industries (stricter validation, known-facts-only, higher price) -> Manufacturing/FaultTrace (domain-specific, highest margin). Track A: deterministic AI funnel. Track B: FaultTrace (parallel, ship now).","source":"anton/2026-04-13 discussion"}'
post '{"key":"faulttrace value prop","type":"string","value":"Stop paying $1,000/call to understand code someone else wrote badly. Get machines back online faster. Your newest guy can troubleshoot like your best guy.","source":"memory/2026-03-24.md"}'
post '{"key":"faulttrace beta testers","type":"string","value":"Beta tester #1: AB engineer at small company automating. Said unused tags feature is something hed pay for. Beta tester #2: Commissioning manager, signed up with ref=beta2.","source":"memory/2026-03-25.md"}'

echo "Done. $(curl -s http://127.0.0.1:8000/facts | python3 -c 'import sys,json; print(json.load(sys.stdin)["count"])') facts loaded."
