---
Summary: PMC workflow state types including shell, claude, input, output, branch, and loop states.
---

# State Types Reference

Complete reference for all PMC workflow state types.

## Shell State

Execute shell commands.

```json
"check-exists": {
  "type": "shell",
  "command": "test -f {file_path} && echo 'EXISTS' || echo 'NOT_FOUND'",
  "timeout": "30s",
  "working_dir": "{project_root}",
  "outputs": {
    "file_status": "$.result"
  },
  "transitions": [
    {"condition": {"type": "pattern", "match": "EXISTS"}, "target": "process"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"shell"` | Yes | State type |
| `command` | string | One of | Inline shell command |
| `script` | string | One of | Script file path (relative to workflow) |
| `timeout` | duration | No | Max execution time (default: 60s) |
| `working_dir` | string | No | Working directory |
| `outputs` | object | No | JSONPath extraction to context |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

**Note:** `command` and `script` are mutually exclusive.

---

## Claude State

Invoke Claude CLI.

```json
"plan-ticket": {
  "type": "claude",
  "prompt": "Read {docs_dir}/tickets/{ticket_id}/1-definition.md and create a plan.\n\nOutput: {\"status\": \"success\", \"test_mode\": \"script\"}",
  "working_dir": "{project_root}",
  "session": "start",
  "outputs": {
    "status": "$.status",
    "test_mode": "$.test_mode"
  },
  "transitions": [
    {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "implement"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"claude"` | Yes | State type |
| `prompt` | string | Yes | Prompt template for Claude |
| `working_dir` | string | No | Working directory for Claude |
| `session` | `"start"` \| `"continue"` | No | Session handling mode |
| `outputs` | object | No | JSONPath extraction to context |
| `memory` | object | No | Memory injection config |
| `memory_capture` | object | No | Output capture config |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

### Session Modes

| Mode | Description |
|------|-------------|
| `"start"` | Begin new Claude session, stores `_session_id` in context |
| `"continue"` | Resume existing session using `_session_id` from context |

### Session Example

```json
"states": {
  "analyze": {
    "type": "claude",
    "prompt": "Analyze the codebase and identify issues.",
    "session": "start",
    "outputs": {"issues": "$.issues"},
    "transitions": [{"condition": {"type": "default"}, "target": "fix"}]
  },
  "fix": {
    "type": "claude",
    "prompt": "Fix the issues you identified. You have full context from the analysis.",
    "session": "continue",
    "outputs": {"status": "$.status"},
    "transitions": [{"condition": {"type": "default"}, "target": "verify"}]
  },
  "verify": {
    "type": "claude",
    "prompt": "Verify the fixes are correct.",
    "session": "continue",
    "transitions": [{"condition": {"type": "default"}, "target": "done"}]
  }
}
```

When using `session: "continue"`, Claude retains full conversation context from all previous states in the session.

---

## Workflow State

Invoke sub-workflow.

```json
"run-tests": {
  "type": "workflow",
  "workflow": "test.runner",
  "inputs": {
    "project_root": "{project_root}",
    "test_pattern": "tests/unit/**/*.py"
  },
  "transitions": [
    {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "done"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"workflow"` | Yes | State type |
| `workflow` | string | Yes | Registry name of sub-workflow |
| `inputs` | object | No | Input variables for sub-workflow |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

---

## Fan Out State

Parallel item processing.

```json
"process-tickets": {
  "type": "fan_out",
  "items": ["T00001", "T00002", "T00003"],
  "item_var": "ticket_id",
  "concurrency": 3,
  "retry": {
    "max_attempts": 2,
    "delay_seconds": 5
  },
  "state": {
    "type": "workflow",
    "workflow": "ticket.handler",
    "inputs": {
      "ticket_id": "{ticket_id}"
    }
  },
  "transitions": [
    {"condition": {"type": "all_success"}, "target": "done"},
    {"condition": {"type": "any_failed"}, "target": "partial-failure"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"fan_out"` | Yes | State type |
| `items` | string \| array | Yes | Items list or variable ref `"{var}"` |
| `item_var` | string | Yes | Variable name for current item |
| `concurrency` | number | No | Max parallel executions (default: 3) |
| `retry` | object | No | Retry config for failed items |
| `state` | object | Yes | Inner state (`claude`, `shell`, or `workflow`) |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

### Output Structure

```json
{
  "item1": {"status": "success", "output": "...", "attempts": 1},
  "item2": {"status": "failure", "error": "...", "attempts": 2},
  "_meta": {
    "total": 2,
    "succeeded": 1,
    "failed": 1,
    "failed_items": ["item2"]
  }
}
```

---

## Parallel State

Spawn multiple workflows.

```json
"spawn-workers": {
  "type": "parallel",
  "spawn": [
    {
      "id": "worker-1",
      "workflow": "worker.process",
      "inputs": {"batch": "A"},
      "background": false
    },
    {
      "id": "worker-2",
      "workflow": "worker.process",
      "inputs": {"batch": "B"},
      "background": true
    }
  ],
  "transitions": [
    {"condition": {"type": "all_complete"}, "target": "done"},
    {"condition": {"type": "any_blocked"}, "target": "blocked"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"parallel"` | Yes | State type |
| `spawn` | array | Yes | List of spawn configurations |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

### Spawn Config

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier |
| `workflow` | string | Yes | Registry name of workflow |
| `inputs` | object | No | Input variables |
| `background` | boolean | No | Run without blocking (default: false) |

---

## Checkpoint State

User approval.

```json
"approve-deploy": {
  "type": "checkpoint",
  "message": "Ready to deploy {version} to production?",
  "context": ["version", "changes"],
  "options": ["approve", "reject", "defer"],
  "timeout": "30m",
  "on_timeout": "defer",
  "transitions": [
    {"condition": {"type": "pattern", "match": "approve"}, "target": "deploy"},
    {"condition": {"type": "pattern", "match": "reject"}, "target": "cancelled"},
    {"condition": {"type": "default"}, "target": "deferred"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"checkpoint"` | Yes | State type |
| `message` | string | Yes | Message to display |
| `context` | array | No | Variables to include in display |
| `options` | array | No | Response options (default: `["approve", "reject"]`) |
| `timeout` | duration | No | Max wait time |
| `on_timeout` | string | No | Option or state on timeout |
| `transitions` | array | No | Transition definitions |
| `on_error` | object | No | Error handling config |

---

## Sleep State

Wait duration.

```json
"wait-cooldown": {
  "type": "sleep",
  "duration": "30s",
  "next": "continue-state"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"sleep"` | Yes | State type |
| `duration` | duration | Yes | Wait duration |
| `next` | string | Yes | Next state after sleep |

**Note:** Sleep uses `next` instead of `transitions`.

---

## Terminal State

End workflow.

```json
"success": {
  "type": "terminal",
  "status": "success",
  "message": "Ticket {ticket_id} completed"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"terminal"` | Yes | State type |
| `status` | string | Yes | `success`, `failure`, `blocked`, `denied` |
| `message` | string | No | Final message (supports variables) |
