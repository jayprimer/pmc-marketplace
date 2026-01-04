---
name: test
description: |
  Execute tests following TDD cycle: RED (verify test fails) → GREEN (implement to pass) → REFACTOR.
  Interprets tests.json and performs steps using available tools (browser MCP, API, CLI, etc.).

  WHEN TO USE:
  - Starting implementation of a ticket with TDD: yes
  - After writing test spec (3-spec.md) and tests.json
  - When user says "run tests", "test this", "TDD cycle"
  - After fixing a failing test

  REQUIRES:
  - Ticket with 3-spec.md
  - tests.json in .pmc/docs/tests/tickets/T0000N/
---

# Test Execution

Execute tests following TDD methodology with trajectory recording.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand test format and TDD workflow.

## TDD Cycle

```
1. RED (required for TDD tickets)
   └── Run test BEFORE implementation
   └── Verify it fails (expected behavior)
   └── Record red_verified timestamp

2. GREEN
   └── Implement minimal code to pass
   └── Run test again
   └── Record trajectory

3. REFACTOR
   └── Clean up code (keep tests green)
   └── Run tests to confirm still passing
   └── Record refactor notes in trajectory
```

---

## Step 1: Locate Tests

```
Read: .pmc/docs/tests/tickets/T0000N/tests.json
```

If no tests.json exists:
1. Check 3-spec.md for test cases
2. Create tests.json from 3-spec.md

---

## Step 2: Environment Setup

**Format:** See [kb/references/test-formats.md](../kb/references/test-formats.md) (config and setup sections)

Check `config` section for app_url, db settings. Execute `setup` array before tests.

---

## Step 3: Execute Test (TDD Flow)

### RED Phase (Before Implementation)

**Purpose:** Confirm test fails because feature doesn't exist yet.

1. Run test steps
2. Expect FAILURE
3. Record in trajectory:
   ```
   [RED] 2024-01-15T09:00:00 - Verified test fails: {reason}
   ```
4. Set `red_verified` timestamp in tests.json
5. Update `4-progress.md` with RED status

**If test PASSES in RED phase:**
- Either test is wrong OR feature already exists
- Investigate before proceeding

### GREEN Phase (Implementation)

1. Implement minimal code to make test pass
2. Run test again
3. Record trajectory:
   ```
   [GREEN] 2024-01-15T10:30:00 - Implementation started
   do: browser:navigate:/login → OK
   verify: browser:element:#login-form exists → PASS
   ```
4. Update status: `"status": "passed"` or `"status": "failed"`
5. Update `4-progress.md` with GREEN status

### REFACTOR Phase (Optional)

1. Clean up implementation (readability, DRY)
2. Run tests to confirm still passing
3. Record in trajectory:
   ```
   [REFACTOR] 2024-01-15T11:00:00 - Extracted validation logic
   ```

---

## Step 4: Execute Actions

### Browser Actions (use Chrome DevTools MCP)

| Action | Tool Call |
|--------|-----------|
| `browser:navigate:{path}` | `mcp__chrome-devtools__navigate_page` |
| `browser:click:{selector}` | `mcp__chrome-devtools__click` |
| `browser:fill:{selector}={value}` | `mcp__chrome-devtools__fill` |
| `browser:wait:{ms}` | Wait or `mcp__chrome-devtools__wait_for` |

### API Actions (use Bash with curl)

| Action | Command |
|--------|---------|
| `api:GET:{path}` | `curl -s {app_url}{path}` |
| `api:POST:{path}:{body}` | `curl -s -X POST -d '{body}' {app_url}{path}` |

### CLI/Script Actions

| Action | Command |
|--------|---------|
| `cli:{command}` | `Bash: {command}` |
| `script:{path}` | `Bash: uv run python {path}` or appropriate runner |

### Database Actions

| Action | Implementation |
|--------|----------------|
| `db:{SQL}` | Execute via CLI or API depending on setup |

---

## Step 5: Verify Results

Execute each item in `verify` array:

### Browser Verification

| Pattern | How to Check |
|---------|--------------|
| `browser:url contains {text}` | `mcp__chrome-devtools__take_snapshot` → check URL |
| `browser:element:{sel} exists` | `mcp__chrome-devtools__take_snapshot` → find element |
| `browser:element:{sel} text={v}` | Snapshot → check text content |

### Screenshot Verification

| Pattern | How |
|---------|-----|
| `screenshot:{name}` | `mcp__chrome-devtools__take_screenshot` → save to screenshots/ |

### Script/CLI Verification

| Pattern | How |
|---------|-----|
| `exit:0` | Check command exit code |
| `output contains {text}` | Check stdout |

### API Response Verification

| Pattern | How |
|---------|-----|
| `status:{code}` | Check HTTP status |
| `body.{field} == {value}` | Parse JSON response |

---

## Step 6: Record Trajectory

**Critical:** Every action and result must be recorded.

**Format:** See [kb/references/test-formats.md](../kb/references/test-formats.md) (trajectory section)

Quick reference:
```
do: {action} → OK | FAIL ({reason})
verify: {check} → PASS | FAIL ({actual vs expected})
```

---

## Step 7: Update Status

**Format:** See [kb/references/test-formats.md](../kb/references/test-formats.md) (status section)

### On Pass
- Set `status: "passed"` with full trajectory
- Update `4-progress.md` with TDD cycles (RED/GREEN/REFACTOR dates)

### On Fail
- Set `status: "failed"` with failure details in trajectory
- Analyze failure, fix implementation, retry

### On Block
- Set `status: "blocked"` with `blocked_reason`
- Mark when: external dependency unavailable, requires human decision, environment issue

---

## Step 8: Teardown

Execute `teardown` array from tests.json after tests complete.

---

## Running Multiple Tests

For ticket with multiple tests:

1. Run all `required: true` tests
2. Record each separately
3. Ticket complete when ALL required tests pass

```markdown
## Test Summary

| Test | Status | Notes |
|------|--------|-------|
| T00001-01 | passed | Login flow |
| T00001-02 | passed | Logout flow |
| T00001-03 | blocked | Needs OAuth setup |
```

---

## Checklist

### Before Testing
- [ ] tests.json exists
- [ ] Config values set (ports, URLs)
- [ ] Environment ready (services running)
- [ ] Setup actions executed

### RED Phase
- [ ] Test executed before implementation
- [ ] Verified test fails (expected)
- [ ] `red_verified` timestamp set
- [ ] Trajectory recorded

### GREEN Phase
- [ ] Implementation complete
- [ ] Test passes
- [ ] All verify checks pass
- [ ] Trajectory recorded
- [ ] Screenshots saved (if visual)

### REFACTOR Phase
- [ ] Code cleaned up
- [ ] Tests still pass
- [ ] Trajectory updated

### After Testing
- [ ] Status updated in tests.json
- [ ] 4-progress.md updated
- [ ] Teardown executed

---

## Example Run

```
$ /pmc:test T00001

## Test: T00001 - User Authentication

### T00001-01: Login flow

**RED Phase**
Running test before implementation...
- do: browser:navigate:/login → OK
- verify: browser:element:#login-form exists → FAIL (expected)
RED verified at 2024-01-15T09:00:00

**GREEN Phase**
Implementation complete. Running test...
- do: browser:navigate:/login → OK
- verify: browser:element:#login-form exists → PASS
- do: browser:fill:#email=test@example.com → OK
- do: browser:click:#submit → OK
- verify: browser:url contains /dashboard → PASS
- verify: screenshot:dashboard → SAVED

Status: PASSED

### Summary
| Test | Status |
|------|--------|
| T00001-01 | passed |

Ticket T00001: 1/1 required tests passed
```
