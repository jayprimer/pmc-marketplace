---
Summary: Workflow error handling with on_error actions (stop, goto, retry) and global error policies.
---

# Error Handling Reference

Complete reference for workflow error handling.

## State-Level Error Handling

Configure error handling per state with `on_error`:

```json
"implement": {
  "type": "claude",
  "prompt": "Implement feature...",
  "on_error": {
    "action": "retry",
    "max_retries": 3,
    "delay": "5s",
    "backoff_multiplier": 2.0,
    "fallback": "error-state"
  }
}
```

---

## Workflow-Level Error Handling

Configure default error handling for all states:

```json
{
  "name": "my-workflow",
  "error_handling": {
    "action": "goto",
    "fallback": "global-error-handler"
  },
  "states": { ... }
}
```

State-level `on_error` overrides workflow-level.

---

## Error Actions

| Action | Description |
|--------|-------------|
| `stop` | Stop workflow execution (default) |
| `retry` | Retry with backoff |
| `goto` | Go to fallback state |
| `skip` | Skip failed state and continue |
| `escalate` | Propagate error to parent workflow |

---

## Error Config Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | string | `"stop"` | Error action |
| `max_retries` | number | 3 | Retry attempts |
| `delay` | duration | `"5s"` | Initial delay between retries |
| `backoff_multiplier` | number | 1.0 | Exponential backoff multiplier |
| `fallback` | string | - | Target state for `goto` action |

---

## Retry with Backoff

```json
"on_error": {
  "action": "retry",
  "max_retries": 3,
  "delay": "5s",
  "backoff_multiplier": 2.0
}
```

Retry sequence:
1. First retry: wait 5s
2. Second retry: wait 10s (5s × 2.0)
3. Third retry: wait 20s (10s × 2.0)
4. If still fails: stop workflow

---

## Goto Fallback

```json
"on_error": {
  "action": "goto",
  "fallback": "handle-error"
}
```

On error, transition to `handle-error` state instead of stopping.

---

## Skip and Continue

```json
"on_error": {
  "action": "skip"
}
```

Skip the failed state and continue to the default transition target.

---

## Escalate to Parent

For sub-workflows:

```json
"on_error": {
  "action": "escalate"
}
```

Propagate error to parent workflow's error handling.

---

## Duration Format

Durations use format: `{hours}h{minutes}m{seconds}s`

| Example | Duration |
|---------|----------|
| `"5s"` | 5 seconds |
| `"2m"` | 2 minutes |
| `"1h"` | 1 hour |
| `"1h30m"` | 1 hour 30 minutes |
| `"2m30s"` | 2 minutes 30 seconds |

---

## Error Handler State Pattern

```json
"states": {
  "process": {
    "type": "claude",
    "prompt": "Process {item}...",
    "on_error": {
      "action": "goto",
      "fallback": "handle-error"
    },
    "transitions": [
      {"condition": {"type": "default"}, "target": "done"}
    ]
  },

  "handle-error": {
    "type": "claude",
    "prompt": "An error occurred. Analyze and decide:\n\nOutput: {\"action\": \"retry|skip|abort\"}",
    "outputs": {"error_action": "$.action"},
    "transitions": [
      {"condition": {"type": "json", "path": "$.action", "equals": "retry"}, "target": "process"},
      {"condition": {"type": "json", "path": "$.action", "equals": "skip"}, "target": "done"},
      {"condition": {"type": "default"}, "target": "failed"}
    ]
  },

  "done": {
    "type": "terminal",
    "status": "success"
  },

  "failed": {
    "type": "terminal",
    "status": "failure",
    "message": "Processing failed after error handling"
  }
}
```

---

## Complete Example

```json
{
  "name": "robust-workflow",
  "initial_state": "start",

  "error_handling": {
    "action": "goto",
    "fallback": "global-error"
  },

  "states": {
    "start": {
      "type": "shell",
      "command": "echo 'Starting...'",
      "transitions": [{"condition": {"type": "default"}, "target": "critical-step"}]
    },

    "critical-step": {
      "type": "claude",
      "prompt": "Perform critical operation...",
      "on_error": {
        "action": "retry",
        "max_retries": 5,
        "delay": "10s",
        "backoff_multiplier": 1.5,
        "fallback": "critical-failed"
      },
      "transitions": [{"condition": {"type": "default"}, "target": "optional-step"}]
    },

    "optional-step": {
      "type": "shell",
      "command": "optional-command",
      "on_error": {
        "action": "skip"
      },
      "transitions": [{"condition": {"type": "default"}, "target": "done"}]
    },

    "done": {
      "type": "terminal",
      "status": "success"
    },

    "critical-failed": {
      "type": "terminal",
      "status": "failure",
      "message": "Critical step failed after 5 retries"
    },

    "global-error": {
      "type": "terminal",
      "status": "failure",
      "message": "Unexpected error occurred"
    }
  }
}
```
