---
summary: "\"FaultTrace Agent Stack — Upgradeable PoC Architecture\""
read_when: ["["idea", "agent"]"]
---
# FaultTrace Agent Stack — Upgradeable PoC Architecture

**Goal:** 2-week MVP that is trivial to extend with new skills, models, and optimizations.

---

## Core Modules

```
src/
├── agent/
│   ├── AgentRuntime.ts       # Orchestrates tool calls, manages turns
│   ├── IAgent.ts             # Interface: { name, tools, execute(input) }
│   ├── SkillRegistry.ts      # Maps skill names → agent instances
│   └── agents/
│       ├── TestGenerator.ts  # PoC skill
│       ├── StaticAnalyzer.ts # Wraps FaultTrace rules
│       └── Summarizer.ts     # Plain-English summary
├── tools/
│   ├── ITool.ts              # Interface: { name, params, execute(args) }
│   ├── L5XParser.ts          # Parse L5X → AST
│   ├── FileSystem.ts         # read/write L5X
│   └── FaultTraceRules.ts    # Run static analysis
├── models/
│   ├── IModelRouter.ts       # Interface: chooseModel(task) → modelId
│   ├── DefaultRouter.ts      # Static mapping (Haiku=simple, Sonnet=default)
│   └── OpenRouterClient.ts   # Thin wrapper around OpenRouter API
├── cache/
│   ├── ICache.ts             # Interface: get(key), set(key, value)
│   ├── RedisCache.ts         # Redis implementation
│   └── NoopCache.ts          # Disabled cache (dev)
├── context/
│   ├── ContextBuilder.ts     # Build context from history + tools
│   └── Compressor.ts         # Summarize old turns (future: use agent)
├── api/
│   ├── Server.ts             # Express/FastAPI server
│   └── AnalyzeHandler.ts     # POST /analyze → AgentRuntime
├── config/
│   ├── skills.yaml           # Skill enablement, model overrides
│   └── cache.yaml            # TTLs, max size
└── types/
    └── common.ts             # Shared types (AnalysisRequest, SkillResult)
```

---

## Key Interfaces

### `IAgent`
```typescript
interface IAgent {
  name: string;
  tools: ITool[];              // Tools this agent can use
  execute(input: AgentInput): Promise<AgentOutput>;
}
```
**Extensibility:** New skills → new file in `agents/`, register in `SkillRegistry`. No core changes.

### `ITool`
```typescript
interface ITool {
  name: string;
  description: string;         // Shown to agent in system prompt
  params: ZodSchema;           // Input validation
  execute(args: any): Promise<ToolResult>;
}
```
**Extensibility:** New capabilities (e.g., SymbolTable lookup) → new file in `tools/`. Auto-discovered by `SkillRegistry`.

### `IModelRouter`
```typescript
interface IModelRouter {
  chooseModel(skillName: string, inputSize: number): ModelConfig;
}
```
**Extensibility:** Swap routing strategy (cost-based, latency-based) by implementing interface. Production: add `CachingModelRouter` that checks cache hit before routing.

---

## Data Flow

```
HTTP Request → AnalyzeHandler
  ↓
AgentRuntime.selectAgent(skillName)
  ↓
ContextBuilder.build(history, tools)
  ↓
ModelRouter.chooseModel() → modelId
  ↓
OpenRouterClient.chat(messages, modelId)
  ↓
[Agent may call tools via tool_call → ITool.execute()]
  ↓
AgentRuntime.collectFinalOutput()
  ↓
Cache.set(inputHash, output)   // if enabled
  ↓
HTTP Response
```

---

## Extension Points (What you'll change later)

| What | Where | Change |
|------|-------|--------|
| Add new skill | `src/agents/NewSkill.ts` + `skills.yaml` | New file, config entry |
| Add new tool | `src/tools/NewTool.ts` | New file; agents auto-see it |
| Change model routing | `src/models/CostBasedRouter.ts` | New class, config switch |
| Add cache backend | `src/cache/MemcachedCache.ts` | New class, config switch |
| Add streaming responses | `OpenRouterClient.stream()` + API upgrade | Minimal core impact |
| Multi-agent collaboration | `AgentOrchestrator.ts` (new) | New module; reuse existing agents |

---

## Upgrade Path Examples

### 1. Add "Compliance Checker" Skill (Week 8)
- Create `src/agents/ComplianceChecker.ts` implementing `IAgent`
- Uses `FaultTraceRules` tool + new `RegulationDB` tool
- Register in `skills.yaml`
- **No changes to runtime, API, caching**

### 2. Switch to Haiku for simple fixes (Week 6)
- Implement `HybridRouter.ts` that checks `inputSize` and `skillName`
- Set `model_router: hybrid` in `config.yaml`
- **No changes to agents or tools**

### 3. Add Redis caching (Week 4)
- `RedisCache` already exists; just set `cache.enabled: true`
- **No changes to agents or API**

### 4. Add cross-file analysis (Week 10)
- New tool: `DependencyGraph.ts` that loads related files
- `Summarizer` and `TestGenerator` add this tool to their `tools[]`
- **No changes to runtime**

---

## Configuration‑Driven Behavior

**`skills.yaml`:**
```yaml
skills:
  test-generator:
    model: sonnet
    max_turns: 5
    tools: [l5x-parser, file-system, faulttrace-rules]
  static-analyzer:
    model: haiku
    tools: [faulttrace-rules]
```

**`cache.yaml`:**
```yaml
enabled: true
ttl_seconds: 86400
max_size_mb: 100
```

Changing behavior = edit YAML, restart.

---

## What the PoC Will Have (Week 2)

- `TestGenerator` agent with 3 tools
- `DefaultRouter` (Sonnet always)
- `NoopCache` (caching disabled)
- `FileSystem` and `L5XParser` tools
- Simple Express server with `/analyze`
- Config files: `skills.yaml` with one entry

All interfaces defined and implemented. Adding a second skill next week is a copy‑paste‑modify operation.

---

## Interfaces You Must Not Break

- `IAgent.execute()` signature
- `ITool.execute()` signature
- Request/response JSON shapes
- Cache key format (input hash)

If these stay stable, you can refactor *internals* freely forever.

---

**Bottom line:** The architecture separates *what* from *how*. Skills = what; runtime = how. That's the upgradeability guarantee.

Want me to generate the actual TypeScript interfaces and a sample `TestGenerator` skeleton to start coding immediately? I can scaffold the entire PoC in one go.
