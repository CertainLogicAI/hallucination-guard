# AgentPathfinder — How Users Actually Use It

**Date:** 2026-04-25

---

## Two Workflows

| | CLI (Quick) | Python SDK (Production) |
|--|-------------|------------------------|
| **Who** | Demo, testing, one-off tasks | Real automation, agents, CI/CD |
| **How** | Type commands | Write Python scripts |
| **Steps** | Named strings | Python functions |
| **Execution** | Simulated (marks complete) | Real functions run |
| **Binding** | None — just names | Function maps to step name |

---

## CLI Workflow (Free Tier)

### 1. Create a Task
```bash
pf create "deploy_api" "run_tests" "build_docker" "push_registry" "restart_service"
```
Output:
```
✅ Task created: a7f3d2e1-...
   ℹ️ Name: deploy_api
   ℹ️ Steps: 5
```

You define:
- **Task name:** `deploy_api`
- **Step names:** `run_tests`, `build_docker`, etc.

Step names are labels. The CLI doesn't know what "run_tests" means — it just creates the sharded task structure.

### 2. Run the Task (Simulation Mode)
```bash
pf run a7f3d2e1-...
```
Output:
```
⏳ Running task a7f3d2e1-...
✅ deploy_api is complete! ID: a7f3d2e1-...
   Progress: 5/5
   ✅ Step 1 complete: run_tests (token: tok_abc123...)
   ✅ Step 2 complete: build_docker (token: tok_def456...)
   ...
```

**Important:** `pf run` simulates step completion. It marks all steps done and issues tokens. No real code runs. This is for:
- Demoing the sharding
- Testing crash recovery
- Verifying audit trails

### 3. Check Status Anytime
```bash
pf status a7f3d2e1-...
```
Shows live status with ✅/❌/⏳ icons.

### 4. View Audit Trail
```bash
pf audit a7f3d2e1-...
```
Shows HMAC-signed events. If someone tampers with the files, you'll see `🚨 Tampered`.

### 5. Reconstruct Key
```bash
pf reconstruct a7f3d2e1-...
```
Only works if all steps are complete. Fails if any step is pending/failed.

---

## Python SDK Workflow (Real Execution)

For actual automation, you write a Python script:

```python
from pathfinder_client import PathfinderClient

pf = PathfinderClient()

# Create task (same as CLI)
tid = pf.create("deploy_api", ["run_tests", "build_docker", "push_registry", "restart_service"])

# Bind REAL functions to step names
def run_tests():
    import subprocess
    result = subprocess.run(["pytest", "-v"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Tests failed: {result.stderr}")
    return "All tests passed"

def build_docker():
    subprocess.run(["docker", "build", "-t", "myapp:latest", "."], check=True)
    return "myapp:latest"

def push_registry():
    subprocess.run(["docker", "push", "myapp:latest"], check=True)
    return "Pushed to registry"

def restart_service():
    subprocess.run(["kubectl", "rollout", "restart", "deployment/myapp"], check=True)
    return "Service restarted"

# Execute with real functions
from agentpathfinder import AgentRuntime, TaskEngine, IssuingLayer

engine = TaskEngine()
issuing = IssuingLayer(engine)
runtime = AgentRuntime(engine, issuing)

step_functions = {
    "run_tests": run_tests,
    "build_docker": build_docker,
    "push_registry": push_registry,
    "restart_service": restart_service,
}

# Run all steps
result = runtime.execute_task(tid, step_functions)
print(result)
```

### What Happens

1. **Step 1** (`run_tests`): Runs `pytest`. If it fails → step marked `❌ failed`, task pauses.
2. **Step 2** (`build_docker`): Only runs if step 1 passed.
3. **Step 3** (`push_registry`): Only runs if step 2 passed.
4. **Step 4** (`restart_service`): Only runs if step 3 passed.
5. **Reconstruction**: After step 4, master key is reconstructed.

If any step fails:
- Task state: `⏸️ paused`
- Failed step shows error
- Audit trail records everything
- You can retry:

```python
# Retry the failed step
runtime.retry_step(tid, step_number, step_functions["run_tests"])
```

Or from CLI:
```bash
pf status <task_id>  # See which step failed
# Fix the issue, then retry via SDK
```

---

## Hermes / Agent Integration

When Hermes (or any agent) uses Pathfinder:

```python
# Hermes creates a task for a complex job
tid = pf.create("refactor_module", [
    "analyze_code",
    "write_tests",
    "refactor_functions",
    "run_tests",
    "commit_changes"
])

# Hermes defines each step as a tool call
def analyze_code():
    return hermes.read_file("/src/module.py")

def write_tests():
    return hermes.write_file("/tests/test_module.py", test_code)

# ... etc

# Execute
runtime.execute_task(tid, {
    "analyze_code": analyze_code,
    "write_tests": write_tests,
    "refactor_functions": refactor_functions,
    "run_tests": run_tests,
    "commit_changes": commit_changes,
})
```

**Key insight:** The agent doesn't need to track state. Pathfinder does. If the agent crashes mid-task, restart it, load the task ID, and resume:

```python
# After crash — resume from where we left off
runtime.resume_task(tid, step_functions)
```

---

## File-Based Task Specs (CI/CD)

For CI/CD pipelines, define tasks in YAML:

```yaml
# deploy.yaml
name: deploy_api
steps:
  - run_tests
  - build_docker
  - push_registry
  - restart_service
```

Then:
```bash
pf create --file deploy.yaml
pf run <task_id>
```

---

## Summary: When to Use What

| Use Case | Tool |
|----------|------|
| "Let me see how this works" | CLI `pf create` + `pf run` |
| "Demo the sharding to my team" | CLI + `pf audit` |
| "Automate my deployment" | Python SDK with real functions |
| "Hermes agent runs complex task" | Python SDK + `AgentRuntime` |
| "CI/CD pipeline" | YAML spec + CLI |
| "Track 50 agents across my team" | Pro dashboard ($29) |

---

## The "Aha" Moment

Run this yourself:

```bash
# 1. Create a 5-step task
pf create "hackathon_project" "plan" "code" "test" "deploy" "present"

# 2. Run it
pf run <task_id>

# 3. See the visual confirmation
pf status <task_id>

# 4. Verify nothing was tampered
pf audit <task_id>

# 5. See the key that only exists because all 5 steps completed
pf reconstruct <task_id>
```

That's the free product. It works. It's real. Upgrade when you want dashboards and team coordination.
