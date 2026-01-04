---
name: workflow
description: |
  Develop, test, and register PMC workflows.
  Workflows are JSON state machines for Claude CLI, shell, sub-workflows.

  WORKFLOW:
  1. DEFINE - Create workflow JSON with states, transitions
  2. VALIDATE - pmc validate <workflow.json>
  3. MOCK - Create mock scripts for each state
  4. TEST MOCK - pmc run --mock to test transitions
  5. TEST REAL - pmc run with real data
  6. REGISTER - Add to registry.json

  Use when:
  - User says "create workflow", "new workflow", "automate"
  - Automating repetitive multi-step processes
  - Building CI/CD or development pipelines
---

# Workflow Development

Develop, test, and register PMC workflows.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand KB structure.

## Overview

```
1. DEFINE
   └── Create .pmc/workflows/{name}/workflow.json

2. VALIDATE
   └── pmc validate .pmc/workflows/{name}/workflow.json

3. MOCK
   └── Create .pmc/workflows/{name}/mocks/mocks.json + *.py

4. TEST MOCK
   └── pmc run {name} --mock -i param=value

5. TEST REAL
   └── pmc run {name} -i param=value

6. REGISTER
   └── Add to .pmc/workflows/registry.json
```

---

## Design Strategy: Choose Your Approach

Before defining states, decide on your workflow architecture.

### Approach A: Continuous (Recommended for Most Cases)

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ Claude: Do Work  │ ──▶ │ Shell: Check │ ──▶ │   Terminal   │
│ (session: start) │     │  Artifacts   │     │              │
└──────────────────┘     └──────────────┘     └──────────────┘
                               │ fail
                               ▼
                         ┌──────────────┐
                         │ Claude: Fix  │ ─── loop back
                         │ (continue)   │
                         └──────────────┘
```

**When to use:**
- Claude can complete work in one flow
- Work is validated after completion, not at each step
- You want session continuity (Claude remembers context)
- Sequential work with clear end state

**Benefits:**
- Fewer states (2-3 vs 5-10)
- No JSON handoff ceremony between Claude states
- Prompts reference skills instead of duplicating content
- Simple validation gates
- Easy to maintain

**Example structure:**
```json
{
  "states": {
    "work": {
      "type": "claude",
      "prompt_file": "work.md",
      "session": "start",
      "transitions": [{"condition": {"type": "default"}, "target": "validate"}]
    },
    "validate": {
      "type": "shell",
      "command": "python scripts/validate.py",
      "transitions": [
        {"condition": {"type": "json", "path": "$.ok", "equals": true}, "target": "done"},
        {"condition": {"type": "default"}, "target": "fix"}
      ]
    },
    "fix": {
      "type": "claude",
      "prompt_file": "fix.md",
      "session": "continue",
      "transitions": [{"condition": {"type": "default"}, "target": "validate"}]
    },
    "done": {"type": "terminal", "status": "success"}
  }
}
```

### Approach B: Multi-State (Granular Control)

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
│ State 1 │ ──▶ │ State 2 │ ──▶ │ State 3 │ ──▶ │ Terminal │
└─────────┘     └─────────┘     └─────────┘     └──────────┘
     │               │               │
     ▼               ▼               ▼
  (branch)       (branch)        (branch)
```

**When to use:**
- Complex branching required mid-workflow
- Different human approvals at each step
- Parallel execution of independent steps
- Each step produces distinct artifacts to check

**Trade-offs:**
- More states = more complexity
- Need JSON outputs for transitions
- More mock scripts to maintain
- Claude loses context between states (unless session: continue)

### Prompt Design for Continuous Workflows

**Reference skills, don't duplicate:**

```markdown
## Task

Execute Step 2 (Scope Determination) from `/pmc:plan` skill.

## Context

Request: {request}
Related PRDs: {related_prds}

## Then Continue

Proceed to create artifacts based on your scope decision.
```

**Why this works:**
- Skill docs are source of truth
- Prompt is lightweight guide
- Claude already knows the skill content
- Updates to skill auto-propagate

### Validation Gates

Use shell states as boolean gates, not complex decision points:

```python
#!/usr/bin/env python3
"""Simple validation - check artifacts exist."""
import json
from pathlib import Path

docs_dir = Path(sys.argv[1])
ticket_dir = docs_dir / "tickets" / sys.argv[2]

issues = []
for f in ["1-definition.md", "2-plan.md", "3-spec.md"]:
    if not (ticket_dir / f).exists():
        issues.append(f"Missing {f}")

print(json.dumps({
    "ok": len(issues) == 0,
    "issues": issues
}))
```

### Session Continuity

For multi-Claude-state workflows, use session modes:

| First State | Subsequent States | Context |
|-------------|-------------------|---------|
| `session: start` | `session: continue` | Claude remembers all previous work |
| (none) | (none) | Each state is fresh, needs JSON handoff |

---

## Step 1: Define Workflow

### Directory Structure (Recommended)

Use a nested structure for each workflow:

```
.pmc/workflows/
├── registry.json
└── {name}/
    ├── workflow.json           # Workflow definition
    ├── prompts/                # Prompt files for Claude states
    │   └── {state-name}.md     # Prompt file (referenced by prompt_file)
    ├── mocks/                  # Mock scripts for testing
    │   ├── mocks.json          # Mock configuration (optional)
    │   └── {state-name}.py     # Mock script per state
    └── scripts/                # Real workflow scripts (optional)
        └── *.py
```

This structure ensures:
- **Isolation**: Each workflow is self-contained
- **Clear mock discovery**: Mocks are found in `{name}/mocks/`
- **Consistency**: Matches bundled workflow patterns

### Workflow JSON

Create `.pmc/workflows/{name}/workflow.json`:

```json
{
  "name": "workflow-name",
  "description": "What this workflow does",
  "initial_state": "first-state",
  "inputs": {
    "param": {"type": "string", "required": true}
  },
  "states": {
    "first-state": { ... },
    "done": {"type": "terminal", "status": "success"}
  }
}
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier |
| `initial_state` | Starting state name |
| `states` | State definitions |

### State Types

| Type | Purpose | Key Fields |
|------|---------|------------|
| `shell` | Run command | `command`, `outputs`, `transitions` |
| `claude` | Invoke Claude | `prompt`, `session`, `outputs`, `transitions` |
| `workflow` | Sub-workflow | `workflow`, `inputs`, `transitions` |
| `fan_out` | Parallel items | `items`, `item_var`, `state`, `transitions` |
| `parallel` | Spawn workflows | `spawn`, `transitions` |
| `checkpoint` | User approval | `message`, `options`, `transitions` |
| `sleep` | Wait duration | `duration`, `next` |
| `terminal` | End workflow | `status`, `message` |

---

## Step 2: Validate

```bash
pmc validate .pmc/workflows/{name}/workflow.json
```

Fix any schema errors before proceeding.

---

## Step 3: Create Mocks

Create `.pmc/workflows/{name}/mocks/` directory with mock scripts:

```
.pmc/workflows/{name}/
├── workflow.json
└── mocks/
    ├── mocks.json              # Optional: mock configuration
    ├── first-state.py          # Mock for "first-state"
    ├── second-state.py         # Mock for "second-state"
    └── ...
```

### Mock Discovery Order

When running with `--mock`, the system resolves mocks in this order:

1. **Check mocks.json** for explicit state configuration
2. **Convention-based discovery**: `mocks/{state-name}.py` then `.sh`
3. **Apply fallback behavior** (error, passthrough, or skip)

### mocks.json Configuration (Optional)

Create `mocks/mocks.json` for fine-grained control:

```json
{
  "description": "Mock configuration for my-workflow",
  "fallback": "error",
  "states": {
    "plan-step": {
      "type": "script",
      "script": "plan-step.py",
      "description": "Mock for planning state"
    },
    "simple-state": {
      "type": "inline",
      "output": {"status": "success", "value": 42}
    },
    "skip-state": {
      "type": "passthrough",
      "output": {}
    }
  }
}
```

**Mock Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| `script` | Run Python/shell script | Complex logic, file I/O |
| `inline` | Return static JSON output | Simple success responses |
| `passthrough` | Return empty `{}` | States that need no mock |

**Fallback Behavior:**

| Value | Description |
|-------|-------------|
| `error` | Fail if no mock found (default) |
| `passthrough` | Return `{}` for unmocked states |
| `skip` | Skip state, use default transition |

### Python Mock Template

```python
#!/usr/bin/env python3
"""Mock for {state-name} state."""
import os
import json

# Read context from environment
ticket_id = os.environ.get("PMC_VAR_ticket_id", "")
state_name = os.environ.get("PMC_STATE", "")
context = json.loads(os.environ.get("PMC_CONTEXT", "{}"))

# Simulate state logic
# ...

# Output JSON for transitions
output = {
    "status": "success",
    "data": "mock result"
}
print(json.dumps(output))

# Exit codes: 0=success, 1=failure, 2=blocked
```

### Mock for Shell State

```python
#!/usr/bin/env python3
"""Mock for check-exists state."""
import json

# Simulate file check
output = "EXISTS"  # or "NOT_FOUND"
print(output)
```

### Mock for Claude State

```python
#!/usr/bin/env python3
"""Mock for plan-ticket state."""
import json

# Simulate Claude response
output = {
    "status": "success",
    "test_mode": "script"
}
print(json.dumps(output))
```

---

## Step 4: Test Mock Mode

```bash
# With nested structure, mock-dir is auto-discovered
pmc run {name} --mock -i param=value -v

# Or with explicit path:
pmc run .pmc/workflows/{name}/workflow.json --mock -i param=value -v
```

**Note:** When using the nested structure, the mock directory is automatically discovered at `.pmc/workflows/{name}/mocks/`. The `--mock-dir` flag is only needed to override this default.

### Verify

- [ ] All states execute in expected order
- [ ] No "No mock found" errors
- [ ] Transitions follow expected paths
- [ ] Terminal state reached with correct status

### Debug Tips

**Mock not found:**
```
No mock found for state 'state-name'
```
→ Create `mocks/state-name.py`

**Wrong transition:**
```
Unexpected next state
```
→ Check mock output matches transition conditions

---

## Step 5: Test Real Mode

### Create Test Data

```
.pmc/workflows/test/mock-data/
├── tickets/T99001/
│   ├── 1-definition.md
│   └── ...
└── ...
```

### Run Real Test

```bash
pmc run {name} \
  -i ticket_id=T99001 \
  -i docs_dir=.pmc/workflows/test/mock-data \
  -v

# Or with explicit path:
pmc run .pmc/workflows/{name}/workflow.json \
  -i ticket_id=T99001 \
  -i docs_dir=.pmc/workflows/test/mock-data \
  -v
```

### Verify

- [ ] Real Claude calls work
- [ ] Shell commands execute correctly
- [ ] Outputs extracted properly
- [ ] Terminal state reached

---

## Step 6: Register Workflow

Add to `.pmc/workflows/registry.json`:

```json
{
  "version": "1.0",
  "workflows": {
    "existing.workflow": { ... },
    "{name}": {
      "path": "{name}/workflow.json",
      "description": "What this workflow does",
      "tags": ["category", "tag"],
      "entry_point": true
    }
  }
}
```

**Note:** The `path` is relative to the registry.json location. With the nested structure, use `{name}/workflow.json`.

### Registry Fields

| Field | Description |
|-------|-------------|
| `path` | Relative path to JSON |
| `description` | Human-readable description |
| `tags` | Categorization tags |
| `entry_point` | `true` if top-level runnable |

---

## State Reference

### Shell State

```json
"check-file": {
  "type": "shell",
  "command": "test -f {path} && echo 'EXISTS' || echo 'NOT_FOUND'",
  "timeout": "30s",
  "working_dir": "{project_root}",
  "outputs": {
    "file_status": "$.result"
  },
  "transitions": [
    {"condition": {"type": "pattern", "match": "EXISTS"}, "target": "next"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

### Claude State

```json
"create-plan": {
  "type": "claude",
  "prompt_file": "create-plan.md",
  "session": "start",
  "working_dir": "{project_root}",
  "transitions": [
    {"condition": {"type": "default"}, "target": "next"}
  ]
}
```

**Claude State Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"claude"` | Yes | State type |
| `prompt` | string | One of | Inline prompt template (supports variables) |
| `prompt_file` | string | One of | Path to prompt file in `prompts/` directory |
| `session` | string | No | `"start"` or `"continue"` |
| `working_dir` | string | No | Working directory for Claude |
| `outputs` | object | No | JSONPath extraction to context |
| `memory` | object | No | Memory injection config |
| `transitions` | array | No | Transition definitions |

**Prompt Options (choose one):**

| Option | Use Case |
|--------|----------|
| `prompt` | Short, inline prompts |
| `prompt_file` | Complex prompts, easier to maintain separately |

**prompt_file:**
- Path relative to `prompts/` directory in workflow folder
- Supports variable substitution: `{variable}`
- Validates all variables exist before execution
- Example: `"prompt_file": "analyze.md"` loads `prompts/analyze.md`

**Session Modes:**

| Mode | Description |
|------|-------------|
| `"start"` | Begin new Claude session, stores `_session_id` in context |
| `"continue"` | Resume existing session using `_session_id` from context |

**Session Example (multi-state conversation):**

```json
"states": {
  "start-session": {
    "type": "claude",
    "prompt": "Analyze {file} and identify issues.",
    "session": "start",
    "outputs": {"issues": "$.issues"},
    "transitions": [{"condition": {"type": "default"}, "target": "fix-issues"}]
  },
  "fix-issues": {
    "type": "claude",
    "prompt": "Fix the issues you identified.",
    "session": "continue",
    "outputs": {"status": "$.status"},
    "transitions": [{"condition": {"type": "default"}, "target": "done"}]
  }
}
```

**Note:** When using `session: "continue"`, the Claude instance retains context from all previous states in the same session.

### Workflow State

```json
"run-subtask": {
  "type": "workflow",
  "workflow": "subtask.handler",
  "inputs": {
    "param": "{value}"
  },
  "transitions": [
    {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "next"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

### Fan Out State

```json
"process-items": {
  "type": "fan_out",
  "items": "{item_list}",
  "item_var": "item",
  "concurrency": 3,
  "state": {
    "type": "workflow",
    "workflow": "item.handler",
    "inputs": {"item": "{item}"}
  },
  "transitions": [
    {"condition": {"type": "all_success"}, "target": "done"},
    {"condition": {"type": "any_failed"}, "target": "partial"}
  ]
}
```

### Terminal State

```json
"success": {
  "type": "terminal",
  "status": "success",
  "message": "Completed {ticket_id}"
}
```

---

## Transition Conditions

| Type | Description | Example |
|------|-------------|---------|
| `json` | JSONPath match | `{"type": "json", "path": "$.status", "equals": "success"}` |
| `pattern` | Regex match | `{"type": "pattern", "match": "EXISTS"}` |
| `exit_code` | Shell exit | `{"type": "exit_code", "equals": 0}` |
| `default` | Fallback | `{"type": "default"}` |
| `all_success` | Fan-out all pass | `{"type": "all_success"}` |
| `any_failed` | Fan-out any fail | `{"type": "any_failed"}` |

---

## References

For complete specifications, see:

- **[State Types](references/state-types.md)** - All 8 state types with full field tables
- **[Transitions](references/transitions.md)** - Condition types, JSONPath, output extraction
- **[Variables](references/variables.md)** - Input definitions, types, built-in context
- **[Error Handling](references/error-handling.md)** - Error actions, retry patterns, examples

---

## CLI Commands

```bash
# List registered workflows
pmc list

# Run workflow by registry name
pmc run <name> -i param=value

# Run workflow by path
pmc run .pmc/workflows/<name>/workflow.json -i param=value

# Validate workflow
pmc validate .pmc/workflows/<name>/workflow.json

# Dry run (no execution)
pmc run <name> --dry-run

# Mock mode (auto-discovers mocks/ in workflow directory)
pmc run <name> --mock -i param=value

# Mock mode with explicit mock directory
pmc run <name> --mock --mock-dir=<path>

# Verbose output
pmc run <name> -v
```

---

## Checklist

### Definition
- [ ] Workflow JSON created
- [ ] All states defined
- [ ] Transitions cover all paths
- [ ] Terminal states for success/failure
- [ ] Validation passes

### Mocks
- [ ] Mock for each non-terminal state
- [ ] Mocks output correct format
- [ ] Exit codes correct

### Testing
- [ ] Mock mode passes
- [ ] Real mode passes
- [ ] Edge cases handled

### Registration
- [ ] Added to registry.json
- [ ] Description accurate
- [ ] Tags assigned
- [ ] entry_point set correctly
