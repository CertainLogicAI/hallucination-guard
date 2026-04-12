---
summary: "\"Rule Pattern Library\""
read_when: ["["skill"]"]
---
# Rule Pattern Library

Common detection patterns that apply across many file formats and domains. Adapt these to your specific format.

## Structural Rules

### DUPLICATE_OUTPUT
Two locations write to the same symbol. Last-scanned wins, earlier writes silently ignored.
- **Applies to:** PLC rungs, config files, state machines, CSS selectors, env vars
- **False positive:** Intentional overrides (default → specific). Exclude if in different scopes/namespaces.

### UNREACHABLE_CODE
Code exists but can never execute (dead branches, impossible conditions, orphan functions).
- **Applies to:** Any language with branching or conditional logic
- **Detection:** Trace all entry points → mark reachable → flag unmarked

### CIRCULAR_DEPENDENCY
A depends on B depends on A. Result is undefined or order-dependent.
- **Applies to:** PLC logic, module imports, config references, database triggers
- **False positive:** Intentional interlock patterns (lock/unlock pairs). Only flag when both sides use the same write-type.

### UNUSED_SYMBOL
Declared but never referenced anywhere in the project.
- **Applies to:** Variables, tags, config keys, CSS classes, DB columns
- **False positive:** Externally-referenced symbols (APIs, HMI bindings). Exclude prefixes/patterns known to be external.

## Safety/Integrity Rules

### UNCONDITIONAL_WRITE
An output/state is set with no conditions — executes every cycle/request/run.
- **Applies to:** PLC outputs, cron jobs, auto-responders, state mutations
- **False positive:** Initialization sequences, heartbeats, constants. Exclude: literal assignments, known init patterns, timer/heartbeat naming patterns.

### WRITE_WITHOUT_FEEDBACK
A command is issued but the result is never checked.
- **Applies to:** Motor run commands, API calls, file writes, DB transactions, deploy scripts
- **Detection:** Find all write/command symbols → check if corresponding status/feedback symbol is read anywhere
- **Key insight:** Match command→feedback pairs by naming convention (e.g., `Run`→`Running`, `Send`→`Ack`, `Write`→`Success`)

### FAULT_NOT_HANDLED
An error/fault status exists but is never read in logic.
- **Applies to:** Device faults, API error responses, exception handling, return codes
- **Detection:** Find all fault/error/status symbols → check if any logic reads them

### RESET_WITHOUT_DELAY
An error recovery action fires continuously instead of once.
- **Applies to:** Fault resets, retry loops, reconnection logic, cache invalidation
- **Detection:** Find reset/clear/retry actions → check for one-shot/debounce/backoff logic

### NO_SAFETY_CHECK
A critical action has no guard/validation/authorization check.
- **Applies to:** Motor starts without guard checks, API deletes without auth, deployments without approval
- **Detection:** Find critical output actions → check for safety/guard/auth conditions on same execution path

## Data Quality Rules

### MISSING_REQUIRED_FIELD
A record/config is missing a field that other similar records have.
- **Applies to:** Config files, database records, API payloads, form data
- **Detection:** Find all instances of a type → intersect their fields → flag outliers missing common fields

### INCONSISTENT_NAMING
Similar items use different naming conventions.
- **Applies to:** Variables, files, API endpoints, database columns
- **Detection:** Cluster names by pattern → flag outliers (e.g., `motor_1_run` vs `Motor2Run` vs `m3-run`)

### REDUNDANT_ENTRIES
Identical content appears multiple times.
- **Applies to:** Config blocks, CSS rules, PLC rungs, cron entries, firewall rules
- **Detection:** Hash or normalize content → group by hash → flag groups with count > 1

## Cross-Reference Rules

### REFERENCE_TO_MISSING
Logic references a symbol/resource that doesn't exist in the project.
- **Applies to:** I/O modules, imports, config references, foreign keys, file paths
- **False positive:** External/runtime-provided resources. Check if the reference type supports external resolution.

### SINGLE_POINT_OF_FAILURE
A critical output depends on a single input with no redundancy.
- **Applies to:** Safety circuits, load balancers, auth providers, DNS, power feeds
- **Detection:** Trace engine → find inputs that appear only once in the dependency chain of critical outputs

## Template: Adding a New Rule

```javascript
function checkYourRule(project) {
  const findings = [];

  // 1. Iterate over the relevant scope
  project.sections.forEach(section => {
    section.items.forEach(item => {

      // 2. Detect the pattern
      const hasIssue = /* your detection logic */;
      if (!hasIssue) return;

      // 3. Check for known-good exclusions
      if (isKnownGoodPattern(item)) return;

      // 4. Build the finding
      findings.push({
        rule: 'YOUR_RULE_ID',
        severity: 'warning',
        title: `Descriptive title: ${item.name}`,
        description: `Domain-language explanation of what this means and why it matters.`,
        locations: [{ file: section.name, line: item.line }],
        recommendation: `Specific action: check X, add Y, verify Z.`,
      });
    });
  });

  return findings;
}
```
