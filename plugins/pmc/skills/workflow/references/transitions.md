---
Summary: Workflow transition conditions including JSON path matching, pattern matching, and default transitions.
---

# Transitions Reference

Complete reference for workflow state transitions and conditions.

## Transition Structure

```json
"transitions": [
  {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "next"},
  {"condition": {"type": "pattern", "match": "ERROR"}, "target": "error"},
  {"condition": {"type": "exit_code", "equals": 0}, "target": "success"},
  {"condition": {"type": "default"}, "target": "fallback"}
]
```

Transitions are evaluated in order. First matching condition wins.

---

## Condition Types

### JSON Condition

Match against JSONPath in state output.

```json
// Exact match
{"type": "json", "path": "$.status", "equals": "success"}
{"type": "json", "path": "$.count", "equals": 5}
{"type": "json", "path": "$.enabled", "equals": true}

// Substring match
{"type": "json", "path": "$.message", "contains": "completed"}

// Existence check
{"type": "json", "path": "$.error", "exists": false}
{"type": "json", "path": "$.data", "exists": true}
```

| Operation | Description |
|-----------|-------------|
| `equals` | Exact value match |
| `contains` | Substring match (strings) |
| `exists` | Check if path exists |

### Pattern Condition

Regex match against output text.

```json
{"type": "pattern", "match": "EXISTS"}
{"type": "pattern", "match": "ERROR.*failed"}
{"type": "pattern", "match": "^SUCCESS$"}
```

### Exit Code Condition

Match shell command exit code.

```json
{"type": "exit_code", "equals": 0}
{"type": "exit_code", "equals": 1}
```

### Default Condition

Fallback when no other condition matches. Must be last.

```json
{"type": "default"}
```

---

## Fan-Out Conditions

For `fan_out` state transitions.

| Type | Description |
|------|-------------|
| `all_success` | All items succeeded |
| `any_failed` | At least one item failed |
| `none_failed` | No items failed |

```json
"transitions": [
  {"condition": {"type": "all_success"}, "target": "done"},
  {"condition": {"type": "any_failed"}, "target": "partial"},
  {"condition": {"type": "default"}, "target": "error"}
]
```

---

## Parallel Conditions

For `parallel` state transitions.

| Type | Description |
|------|-------------|
| `all_complete` | All spawned workflows finished |
| `any_blocked` | At least one workflow blocked |

```json
"transitions": [
  {"condition": {"type": "all_complete"}, "target": "done"},
  {"condition": {"type": "any_blocked"}, "target": "blocked"},
  {"condition": {"type": "default"}, "target": "error"}
]
```

---

## Output Extraction

Extract values from state output to context using JSONPath.

```json
"outputs": {
  "status": "$.status",
  "test_mode": "$.test_mode",
  "results": "$.data.results",
  "first_item": "$.items[0]"
}
```

Extracted values become available as `{status}`, `{test_mode}`, `{results}`, `{first_item}` in subsequent states.

### JSONPath Examples

| Pattern | Description |
|---------|-------------|
| `$.status` | Root level field |
| `$.data.results` | Nested field |
| `$.items[0]` | First array element |
| `$.items[*].name` | All name fields in array |
| `$..error` | All error fields (recursive) |

---

## Transition Examples

### Shell Command Result

```json
"check-file": {
  "type": "shell",
  "command": "test -f {path} && echo 'EXISTS' || echo 'NOT_FOUND'",
  "transitions": [
    {"condition": {"type": "pattern", "match": "EXISTS"}, "target": "process-file"},
    {"condition": {"type": "pattern", "match": "NOT_FOUND"}, "target": "create-file"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

### Claude JSON Response

```json
"analyze": {
  "type": "claude",
  "prompt": "Analyze and respond: {\"status\": \"success|failure\", \"action\": \"continue|stop\"}",
  "outputs": {"status": "$.status", "action": "$.action"},
  "transitions": [
    {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "next"},
    {"condition": {"type": "json", "path": "$.action", "equals": "stop"}, "target": "done"},
    {"condition": {"type": "default"}, "target": "retry"}
  ]
}
```

### Exit Code Based

```json
"run-tests": {
  "type": "shell",
  "command": "pytest tests/",
  "transitions": [
    {"condition": {"type": "exit_code", "equals": 0}, "target": "tests-passed"},
    {"condition": {"type": "exit_code", "equals": 1}, "target": "tests-failed"},
    {"condition": {"type": "default"}, "target": "error"}
  ]
}
```

### Combined Conditions

```json
"process": {
  "type": "claude",
  "prompt": "Process {item}.\n\nOutput: {\"status\": \"success|failure|blocked\", \"reason\": \"...\"}",
  "outputs": {"status": "$.status", "reason": "$.reason"},
  "transitions": [
    {"condition": {"type": "json", "path": "$.status", "equals": "success"}, "target": "next"},
    {"condition": {"type": "json", "path": "$.status", "equals": "blocked"}, "target": "blocked"},
    {"condition": {"type": "json", "path": "$.reason", "contains": "retry"}, "target": "retry"},
    {"condition": {"type": "default"}, "target": "failed"}
  ]
}
```
