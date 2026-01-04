---
Summary: Workflow variable syntax, input parameters, state outputs, and variable sources.
---

# Variables Reference

Complete reference for variable substitution and inputs.

## Variable Syntax

Variables use `{variable_name}` syntax in prompts, commands, and inputs.

```json
"command": "echo 'Processing {ticket_id}'"
"prompt": "Read {docs_dir}/tickets/{ticket_id}/1-definition.md"
```

### Features

| Feature | Syntax | Description |
|---------|--------|-------------|
| Simple | `{var}` | Direct substitution |
| Nested | `{output.status}` | Dot notation for nested access |
| Escape | `{{literal}}` | Outputs `{literal}` |

---

## Input Definitions

Define workflow inputs in the `inputs` field:

```json
"inputs": {
  "ticket_id": {
    "type": "string",
    "required": true,
    "description": "Ticket ID (e.g., T00004)"
  },
  "max_retries": {
    "type": "number",
    "required": false,
    "default": 3
  },
  "docs_dir": {
    "type": "path",
    "default": ".pmc/docs"
  },
  "dry_run": {
    "type": "boolean",
    "default": false
  }
}
```

### Input Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"T00001"` |
| `number` | Numeric value | `3`, `1.5` |
| `boolean` | true/false | `true` |
| `path` | File system path | `".pmc/docs"` |
| `array` | List of values | `["a", "b"]` |
| `object` | Nested object | `{"key": "value"}` |

### Input Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Data type (default: `string`) |
| `required` | boolean | Must be provided (default: `false`) |
| `default` | any | Default value if not provided |
| `description` | string | Human-readable description |
| `pattern` | string | Regex for validation (string inputs) |
| `validate` | string | Custom validation expression |

### Validation Example

```json
"inputs": {
  "ticket_id": {
    "type": "string",
    "required": true,
    "pattern": "^T\\d{5}$",
    "description": "Ticket ID in format T00001"
  },
  "priority": {
    "type": "number",
    "validate": "value >= 1 && value <= 5",
    "default": 3
  }
}
```

---

## Built-in Context Variables

These variables are automatically available:

| Variable | Description |
|----------|-------------|
| `_workflow_dir` | Directory containing workflow JSON |
| `_current_state_name` | Name of currently executing state |
| `_session_id` | Claude session ID (when using session mode) |
| `_verbose` | Verbose mode flag |
| `working_dir` | Working directory for execution |

---

## Context Variables

Set initial context in the `context` field:

```json
"context": {
  "project_name": "my-project",
  "environment": "development"
}
```

Context is inherited and can be overwritten by state outputs.

---

## Output Variables

States can extract values to context via `outputs`:

```json
"outputs": {
  "status": "$.status",
  "test_mode": "$.test_mode"
}
```

These become available as `{status}` and `{test_mode}` in subsequent states.

---

## Variable Inheritance

```
inputs → context → state outputs → next state context
```

1. Workflow inputs initialize context
2. Initial context adds/overwrites
3. Each state's outputs add/overwrite
4. Next state receives accumulated context

---

## Examples

### Passing Through States

```json
{
  "inputs": {
    "ticket_id": {"type": "string", "required": true}
  },
  "states": {
    "read-definition": {
      "type": "shell",
      "command": "cat .pmc/docs/tickets/{ticket_id}/1-definition.md",
      "outputs": {"definition": "$.result"},
      "transitions": [{"condition": {"type": "default"}, "target": "analyze"}]
    },
    "analyze": {
      "type": "claude",
      "prompt": "Analyze this definition for {ticket_id}:\n\n{definition}",
      "outputs": {"analysis": "$.analysis"},
      "transitions": [{"condition": {"type": "default"}, "target": "report"}]
    },
    "report": {
      "type": "terminal",
      "status": "success",
      "message": "Analysis of {ticket_id}: {analysis}"
    }
  }
}
```

### Nested Variable Access

```json
"outputs": {
  "status": "$.result.status",
  "first_error": "$.result.errors[0].message",
  "count": "$.result.metadata.count"
}
```

Then use as `{status}`, `{first_error}`, `{count}`.

### CLI Input

```bash
pmc run workflow.json -i ticket_id=T00001 -i max_retries=5 -i dry_run=true
```
