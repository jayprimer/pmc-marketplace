---
Summary: Test JSON format for TDD with trajectory tracking, RED verification, and programmatic status checking.
---

# Test Format

Test definitions for programmatic verification of implementation progress.

## Design Principles

### Why This Format Exists

1. **Accountability** - I (Claude) tend to skip tests, infer success, or prematurely abort. This format forces explicit verification with recorded trajectory.

2. **Programmatic Verification** - JSON format allows external scripts to:
   - Track test status across sessions
   - Determine ticket completion automatically
   - Detect when human input is needed (blocked tests)

3. **Dual Execution** - tests.json is a spec that can be executed by:
   - **External runner** - Automated tooling that parses and executes tests
   - **Claude manually** - Interpreting JSON and performing steps using available tools (browser MCP, API calls, etc.)

   Both approaches are valid. The format serves as common contract.

4. **Multi-Source Verification** - Real tests need multiple verification sources:
   - Script output (pytest, unit tests)
   - API responses
   - Browser DOM state
   - Screenshots (visual feedback)
   - Logs (application behavior)
   - Database (persisted state)
   - Debug endpoints (native app internal state)

5. **Worktree Isolation** - Support parallel development with isolated test environments per git worktree.

### Ticket Completion Algorithm

```python
def is_ticket_complete(tests):
    required_tests = [t for t in tests if t.required]
    return all(t.status == "passed" for t in required_tests)

def needs_human_input(tests):
    return any(t.status == "blocked" for t in tests)

def get_blocked_issues(tests):
    return [t.blocked_reason for t in tests if t.status == "blocked"]
```

A ticket is complete when ALL `required: true` tests have `status: passed`.
Human input is needed when ANY test has `status: blocked`.

### Status Flow

```
pending → running → passed
              ↓
           failed
              ↓
           running (retry with fix)
              ↓
           ... (repeat until pass or blocked)
              ↓
           blocked (needs human)
```

> **Note:** Retry logic and `max_attempts` are external runner configuration. When Claude executes manually, use judgment on when to retry vs mark blocked.

## Location

```
.pmc/docs/tests/
├── smoke/{app}/tests.json           # Health checks
├── core/{feature}/tests.json        # Feature tests
└── tickets/T0000N/
    ├── tests.json                   # Test definitions
    ├── {scripts}                    # Custom scripts (any language)
    └── screenshots/                 # Visual test captures
```

### Screenshots

**Required** for any test involving visual feedback (GUI, web pages, etc.).

| Aspect | Rule |
|--------|------|
| **Location** | `.pmc/docs/tests/tickets/T0000N/screenshots/` (alongside tests.json) |
| **Naming** | `{test_id}_{step}_{description}.png` (e.g., `T00001-01_03_dashboard-after-login.png`) |
| **Cleanup** | After ticket completion (archive includes screenshots) |
| **When** | Required for tests with visual elements |

Screenshots tie directly to test case and step for traceability.

## JSON Format

```json
{
  "ticket": "T00001",
  "title": "User Authentication",
  "config": {
    "env": "${WORKTREE_NAME:-main}",
    "app_url": "http://localhost:${APP_PORT:-3000}",
    "debug_endpoint": "http://localhost:${DEBUG_PORT:-9900}/debug",
    "db": "sqlite:///./data/test_${WORKTREE_NAME:-main}.db",
    "log_path": "./logs/${WORKTREE_NAME:-main}/app.log",
    "screenshot_dir": "./screenshots/${WORKTREE_NAME:-main}",
    "isolation": {
      "cleanup_before": true,
      "cleanup_after": false
    }
  },
  "setup": [
    "db:DELETE FROM users WHERE email LIKE 'test_%'"
  ],
  "teardown": [
    "cli:./scripts/cleanup.sh"
  ],
  "tests": [
    {
      "id": "T00001-01",
      "name": "Login flow",
      "required": true,
      "steps": [
        {
          "do": "browser:navigate:/login",
          "expect": "Login form visible",
          "verify": [
            "browser:element:#login-form exists",
            "screenshot:login-page"
          ]
        },
        {
          "do": "browser:fill:#email=test@example.com",
          "expect": "Email entered"
        },
        {
          "do": "browser:click:#submit",
          "expect": "Login successful, redirect to dashboard",
          "verify": [
            "browser:url contains /dashboard",
            "db:SELECT id FROM sessions WHERE user_email='test@example.com' rows > 0",
            "log:contains:Login successful",
            "screenshot:dashboard"
          ]
        }
      ],
      "status": "pending",
      "red_verified": "2024-01-15T09:00:00Z",
      "attempts": 0,
      "max_attempts": 3,
      "trajectory": [],
      "blocked_reason": null
    }
  ]
}
```

## Field Reference

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket` | string | Yes | Ticket ID or category (`T00001`, `smoke-backend`) |
| `title` | string | No | Human-readable title |
| `config` | object | No | Environment configuration |
| `setup` | array | No | Actions to run before tests |
| `teardown` | array | No | Actions to run after tests |
| `tests` | array | Yes | Test definitions |

### Config Fields

| Field | Description |
|-------|-------------|
| `env` | Environment/worktree identifier |
| `app_url` | Application base URL |
| `debug_endpoint` | Native app debug API URL |
| `db` | Database connection string |
| `log_path` | Application log file path |
| `screenshot_dir` | Where to save screenshots |
| `isolation.cleanup_before` | Clean test data before running |
| `isolation.cleanup_after` | Clean test data after running |

All config values support `${VAR:-default}` syntax for environment variables.

### Test Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID: `{ticket}-{seq}` |
| `name` | string | Yes | What this test verifies |
| `required` | boolean | Yes | `true` = must pass for ticket completion |
| `steps` | array | Yes | Test steps |
| `status` | string | Yes | `pending`/`running`/`passed`/`failed`/`blocked` |
| `red_verified` | string | TDD | ISO timestamp when test was confirmed to fail before implementation |
| `attempts` | number | Runner | Current attempt count (external runner only) |
| `max_attempts` | number | Runner | Max retries before blocking (external runner only) |
| `trajectory` | array | Yes | Recorded actions and results |
| `blocked_reason` | string | No | Why test is blocked (for human) |

> **TDD Note:** `red_verified` is required for TDD tickets. Confirms the test fails before implementation exists. Skip only for trivial tickets with `TDD: no` in definition.

> **Note:** `attempts` and `max_attempts` are for external runner configuration. When Claude executes manually, these fields are optional.

### Step Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `do` | string | Yes | Action to execute |
| `expect` | string | Yes | Expected outcome (human readable) |
| `verify` | array | No | Verification checks (if omitted, step passes if action succeeds) |

## Action Patterns (`do` field)

### Browser Actions
```
browser:navigate:{path}              # Go to URL
browser:click:{selector}             # Click element
browser:fill:{selector}={value}      # Enter text
browser:select:{selector}={value}    # Select dropdown
browser:key:{key}                    # Press key
browser:wait:{ms}                    # Wait
```

### Native App Debug Actions
```
debug:click:{component_id}           # Click via debug endpoint
debug:input:{component_id}={value}   # Set input value
debug:key:{key}                      # Send key to app
debug:call:{method}:{args}           # Call custom method
debug:state:{path}                   # Get internal state
```

### API Actions
```
api:GET:{path}                       # HTTP GET
api:POST:{path}:{json_body}          # HTTP POST
api:PUT:{path}:{json_body}           # HTTP PUT
api:DELETE:{path}                    # HTTP DELETE
```

### CLI Actions
```
cli:{command}                        # Run shell command
```

### Script Actions
```
script:{path}                        # Run test script (pytest, etc.)
```

### General Actions
```
screenshot:{name}                    # Capture screenshot
wait:{ms}                            # Wait milliseconds
db:{SQL}                             # Execute SQL
```

## Verify Patterns (`verify` array)

Multiple verification sources can be combined. All must pass.

### Browser
```
browser:url contains {text}          # URL check
browser:url equals {path}            # Exact URL
browser:element:{selector} exists    # Element present
browser:element:{selector} text={v}  # Element text
browser:element:{selector} visible   # Element visible
browser:console contains {text}      # Console log
browser:network:{url} status={code}  # Network request
```

### Debug Endpoint (Native Apps)
```
debug:state:{path} == {value}        # State equals
debug:state:{path} != {value}        # State not equals
debug:state:{path} exists            # State exists
debug:state:{path} > {value}         # State comparison
```

### Screenshot
```
screenshot:{name}                    # Save screenshot (always passes, for record)
screenshot:{name} matches {baseline} # Compare to baseline image
```

### Log
```
log:contains:{text}                  # Log contains text
log:match:{regex}                    # Log matches regex
log:not contains:{text}              # Log doesn't contain
```

### Database
```
db:{SQL} → {expected}                # Query returns value
db:{SQL} rows > 0                    # Query has results
db:{SQL} rows == {n}                 # Query returns n rows
```

### CLI/Script
```
exit:{code}                          # Exit code (0 = success)
output contains {text}               # Stdout contains
output match:{regex}                 # Stdout matches regex
```

### API Response (after api: action)
```
status:{code}                        # HTTP status
body.{field} == {value}              # JSON field equals
body.{field} exists                  # JSON field present
body.{field} contains {text}         # JSON field contains
```

## Trajectory Recording

Every action and verification is recorded in trajectory:

```json
"trajectory": [
  "[RED] 2024-01-15T09:00:00 - Verified test fails: login form not implemented",
  "[GREEN] 2024-01-15T10:30:00 - Implementation started",
  "do: browser:navigate:/login → OK",
  "verify: browser:element:#login-form exists → PASS",
  "verify: screenshot:login-page → SAVED",
  "do: browser:fill:#email=test@example.com → OK",
  "do: browser:click:#submit → OK",
  "verify: browser:url contains /dashboard → FAIL (url=/login, error shown)",
  "[Attempt 2] 2024-01-15T10:32:00",
  "Analysis: Login failed due to missing password field",
  "Fix: Added password input step",
  "do: browser:navigate:/login → OK",
  "... (continued)",
  "[REFACTOR] 2024-01-15T11:00:00 - Extracted validation to separate function"
]
```

Trajectory serves two purposes:
1. **Verification replay** - Another agent can verify by following trajectory
2. **Debug history** - Understand what was tried and why it failed

## Worktree Isolation

### Problem
Git worktrees enable parallel development, but E2E tests conflict:
- Ports: Can't run two servers on same port
- Database: Test data conflicts
- Files: Logs, screenshots overwrite

### Solution

**Port Allocation Convention:**
```
Worktree    APP_PORT    DEBUG_PORT    DB
main        3000        9900          test_main.db
feature-a   3001        9901          test_feature-a.db
feature-b   3002        9902          test_feature-b.db
```

**Per-Worktree Environment (.env.local):**
```bash
WORKTREE_NAME=feature-a
APP_PORT=3001
DEBUG_PORT=9901
DB_URL=sqlite:///./data/test_feature-a.db
LOG_PATH=./logs/feature-a/app.log
```

**Config uses variables:**
```json
"config": {
  "app_url": "http://localhost:${APP_PORT:-3000}",
  "db": "${DB_URL:-sqlite:///./data/test_main.db}"
}
```

### Unit Tests
No isolation needed - run directly in worktree.

### Integration/E2E Tests
Must set environment variables before running.

## Examples

### Script-Based Test (pytest)

```json
{
  "id": "T00001-01",
  "name": "Auth unit tests",
  "required": true,
  "steps": [
    {
      "do": "script:pytest tests/test_auth.py -v",
      "expect": "All tests pass",
      "verify": ["exit:0"]
    }
  ],
  "status": "pending",
  "attempts": 0,
  "max_attempts": 3,
  "trajectory": [],
  "blocked_reason": null
}
```

### Browser E2E Test

```json
{
  "id": "T00001-02",
  "name": "Login UI flow",
  "required": true,
  "steps": [
    {
      "do": "browser:navigate:/login",
      "expect": "Login page loads",
      "verify": ["browser:element:#login-form exists"]
    },
    {
      "do": "browser:fill:#email=test@example.com",
      "expect": "Email entered"
    },
    {
      "do": "browser:fill:#password=testpass123",
      "expect": "Password entered"
    },
    {
      "do": "browser:click:#submit",
      "expect": "Redirected to dashboard",
      "verify": [
        "browser:url contains /dashboard",
        "screenshot:dashboard-after-login"
      ]
    }
  ],
  "status": "pending",
  "attempts": 0,
  "max_attempts": 3,
  "trajectory": [],
  "blocked_reason": null
}
```

### Native App Test (Debug Endpoint)

```json
{
  "id": "T00001-03",
  "name": "Settings save to database",
  "required": true,
  "steps": [
    {
      "do": "debug:click:btn_settings",
      "expect": "Settings dialog opens",
      "verify": [
        "debug:state:dialog.settings.visible == true",
        "screenshot:settings-open"
      ]
    },
    {
      "do": "debug:input:txt_username=NewUser",
      "expect": "Username field updated"
    },
    {
      "do": "debug:click:btn_save",
      "expect": "Settings persisted",
      "verify": [
        "debug:state:dialog.settings.visible == false",
        "db:SELECT username FROM settings WHERE id=1 → NewUser",
        "log:contains:Settings saved"
      ]
    }
  ],
  "status": "pending",
  "attempts": 0,
  "max_attempts": 3,
  "trajectory": [],
  "blocked_reason": null
}
```

### API Test

```json
{
  "id": "T00001-04",
  "name": "Create user API",
  "required": true,
  "steps": [
    {
      "do": "api:POST:/api/users:{\"email\":\"new@test.com\",\"name\":\"Test\"}",
      "expect": "User created",
      "verify": [
        "status:201",
        "body.id exists",
        "body.email == new@test.com"
      ]
    },
    {
      "do": "api:GET:/api/users/${response.id}",
      "expect": "User retrievable",
      "verify": [
        "status:200",
        "body.name == Test"
      ]
    }
  ],
  "status": "pending",
  "attempts": 0,
  "max_attempts": 3,
  "trajectory": [],
  "blocked_reason": null
}
```

## Discovery

```
Glob: .pmc/docs/tests/**/*.json
Glob: .pmc/docs/tests/tickets/T00001/*.json
```

## IMPORTANT: Test Maintenance

After ANY implementation change:
1. Run affected tests
2. Update test definitions if behavior changed
3. Keep trajectory clean for future verification
