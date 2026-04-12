---
summary: "\"Idea: EPLAN Lite — Lightweight Electrical Schematic Tool\""
read_when: ["["idea"]"]
---
# Idea: EPLAN Lite — Lightweight Electrical Schematic Tool

## The Gap
- EPLAN costs $5K-15K/yr per seat
- AutoCAD Electrical is $2K/yr
- Small integrators, maintenance engineers, and one-man shops can't justify that
- They draw schematics in Visio, PowerPoint, or by hand — seriously

## What We Already Have
- `schematic-generator.js` (20KB, 25 SVG drawing functions)
- Proper electrical symbols: contacts, coils, motors, VFDs, E-stops, fuses, contactors, sensors, solenoids, pushbuttons, indicator lights
- 3 page types: power distribution, control circuit, I/O wiring
- Dark theme SVG with title blocks
- Parts list parser (14 component types from free text)

## What It Would Take
- Web app (same Cloudflare Pages pattern as FaultTrace)
- Drag-and-drop schematic editor (the hard part — interactive SVG canvas)
- Wire numbering and auto-routing
- BOM/parts list export
- PDF export
- Template library (motor starter, VFD, safety relay, etc.)

## Target Customer
- Small integrators (1-5 people)
- Maintenance engineers who need to redline or create as-builts
- Controls engineers at companies too small for EPLAN
- Students / apprentices

## Pricing
- Free: limited pages, watermarked PDF
- $29/mo: unlimited pages, clean PDF, BOM export
- $99/mo: team, revision history, template library

## Moat
- First browser-based electrical schematic tool with real IEC/NFPA symbols
- No install, works on any device (including at the panel)
- Same privacy angle as FaultTrace — drawings stay in browser

## Risk
- The drag-and-drop editor is a serious engineering effort (months, not days)
- CAD is a solved problem — competing on price, not features
- EPLAN's real value is in the database (cross-referencing, terminal planning, cable routing) — hard to replicate

## Reality Check
- EPLAN already generates schematics from parts lists — this isn't a gap, it's a price gap
- Our Draft mode doesn't do anything EPLAN can't — it just does it free in a browser
- The only real differentiator is integration: schematics ↔ code analysis ↔ troubleshooting in one tool
- Standalone schematic tool without the FaultTrace ecosystem is a weak play

## Verdict
- **Don't build as standalone product.** EPLAN owns this space.
- Keep Draft mode as a FaultTrace feature where the value is the integration, not the schematics themselves
- The play: "Upload prints → FaultTrace understands your wiring AND your code" — that's what EPLAN can't do
