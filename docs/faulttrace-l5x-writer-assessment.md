# FaultTrace L5X Writer — Assessment (2026-04-13)

## Current State

### What Exists
- **L5X Parser** (`projects/plc-analyzer/app/l5x-parser.js`) — browser-side, parses full controller exports: programs, tags, modules, routines (RLL/ST/FBD), AOIs, UDTs, cross-references
- **L5X Writer** (`projects/plc-analyzer/prototype/index.html` → `generateL5XFromComponents()`) — generates valid RSLogix5000Content XML from a parts list
- **Schematic Generator** (`projects/plc-analyzer/prototype/schematic-generator.js`) — SVG electrical drawings from parts list

### What the Writer Generates
- 5 organized routines: MainRoutine, Motor_Control, Process_Logic, Safety_Interlocks, HMI_Interface
- Proper AB instruction syntax (XIC, OTE, OTL, OTU, TON, SCP, MOV, JSR, ONS, LES, GRT)
- Tag definitions with correct data types (BOOL, REAL, TIMER)
- Module definitions (processor, ENET, DI, DO, AI)
- Component-to-tag mapping from user input
- Comments on every rung

### What's Correct
- Seal-in circuits with one-shot starts
- Timer-based fault detection (VFD fault, feedback timeout, valve position)
- Analog scaling with SCP (4-20mA → engineering units)
- Safety interlocks (E-stop latching, guard interlock, overload, master permissive chain)
- Auto/Manual mode selection
- HMI status mapping
- Tag naming follows AB conventions

## What Needs Work

### Priority 1 — Import-Ready Output
1. **I/O alias mapping** — tags reference DI/DO/AI but no alias to physical slots (e.g., `Local:1:I.Data.0`). Engineer must manually map every tag.
2. **Dynamic modules** — always generates 1756-IB32/B, 1756-OB32/B, etc. Should match actual parts list.
3. **Program-scoped tags** — all tags are controller-scoped. Some (internal timers, one-shots) should be program-scoped.

### Priority 2 — Input Methods
4. **CSV/Excel BOM import** — paste or upload a parts list instead of manual form
5. **PDF electrical print parsing** — extract components from schematic PDFs (longer term)

### Priority 3 — Completeness
6. **TODO markers** — clearly mark where engineer needs to add custom sequence logic
7. **Safety controller support** — GuardLogix (1756-L8xES) safety tasks/programs are separate L5X structure
8. **Structured Text option** — some users prefer ST over ladder for process logic

### Not Recommended (Yet)
- Auto-generated sequence logic from natural language scope — too risky, liability for wrong logic
- Safety-rated logic generation (SIL/PLd) — needs certification

## Strategic Position
- **Sell as scaffolding tool**: "Your project template in minutes, not weeks"
- **60-70% of boilerplate automated**, engineer fills in sequence-specific logic
- **ROI**: typical machine program = 40-160 hours ($6K-40K). Even 60% savings = obvious ROI at $499/mo
- **Keep "nothing leaves your browser" architecture** — strongest trust signal for industrial buyers
