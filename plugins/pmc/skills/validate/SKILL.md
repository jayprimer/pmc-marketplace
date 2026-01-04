---
name: validate
description: |
  Verify test execution by replaying trajectory and checking script coverage.
  Ensures tests actually happened as recorded and scripts cover all test cases.

  WHEN TO USE:
  - After tests claim to pass (verify they actually ran)
  - Before marking ticket complete (audit trail)
  - When reviewing someone else's work
  - User says "validate", "verify tests", "check coverage"
  - Periodic audit of test integrity

  CHECKS:
  1. TRAJECTORY - Steps match recorded actions
  2. EVIDENCE - Screenshots, logs, outputs exist
  3. COVERAGE - Scripts test all cases from 3-spec.md
  4. COMPLETENESS - All required tests have trajectory
---

# Validate Test Execution

Verify tests happened as claimed and scripts cover all test cases.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand test format.

## Why Validation Matters

1. **Accountability** - Claude may skip tests, infer success, or prematurely mark complete
2. **Evidence** - Trajectory provides verifiable audit trail
3. **Coverage** - Test scripts may not cover all cases in 3-spec.md
4. **Trust** - Second agent can verify first agent's work

---

## Validation Modes

| Mode | Scope | Use When |
|------|-------|----------|
| **Quick** | Check trajectory exists, evidence files present | Before commit |
| **Full** | Replay trajectory, verify each step | Before ticket completion |
| **Coverage** | Audit scripts against 3-spec.md | After writing tests |

---

## Step 1: Locate Test Artifacts

```
Read: .pmc/docs/tests/tickets/T0000N/tests.json
Read: .pmc/docs/tickets/T0000N/3-spec.md
Glob: .pmc/docs/tests/tickets/T0000N/screenshots/*.png
Glob: .pmc/docs/tests/tickets/T0000N/*.py  # Test scripts
```

---

## Step 2: Trajectory Validation

### Check Trajectory Exists

Every test with `status: passed` MUST have trajectory.

**Format:** See [kb/references/test-formats.md](../kb/references/test-formats.md) (trajectory section)

**Red Flags:**
- Empty trajectory with passed status
- Missing [RED] entry for TDD tickets
- Trajectory ends mid-test
- Generic entries like "All tests passed" without details

### Verify Trajectory Completeness

For each test, check:

| Check | Valid If |
|-------|----------|
| RED phase | Has `[RED]` entry with timestamp and failure reason |
| GREEN phase | Has `[GREEN]` entry and all `do:` and `verify:` entries |
| Steps match spec | Trajectory steps match tests.json steps |
| All verify recorded | Each `verify` in steps has trajectory entry |

### Report Issues

```markdown
## Trajectory Validation

| Test | Status | Issues |
|------|--------|--------|
| T00001-01 | VALID | - |
| T00001-02 | INVALID | Missing RED phase, 2 verify entries missing |
| T00001-03 | INVALID | Empty trajectory |
```

---

## Step 3: Evidence Validation

### Screenshots

For tests with `screenshot:` actions:

1. Check file exists: `.pmc/docs/tests/tickets/T0000N/screenshots/{name}.png`
2. Verify naming: `{test_id}_{step}_{description}.png`
3. Check timestamps align with trajectory

```
Glob: .pmc/docs/tests/tickets/T0000N/screenshots/*.png
```

**Expected vs Found:**
```markdown
## Screenshot Evidence

| Expected | Found | Status |
|----------|-------|--------|
| T00001-01_login-page.png | T00001-01_login-page.png | OK |
| T00001-01_dashboard.png | (missing) | MISSING |
```

### Script Outputs

For tests with `script:` or `cli:` actions:

1. Check if output was captured
2. Verify exit codes match expected

### Log Evidence

For tests with `log:` verification:

1. Check log file exists
2. Verify expected entries present

---

## Step 4: Coverage Validation

### Compare 3-spec.md to tests.json

Read 3-spec.md and extract test cases:

```markdown
## Test Cases (from 3-spec.md)

### Unit Tests
| Test | Input | Expected |
|------|-------|----------|
| test_login_valid | valid creds | success |
| test_login_invalid | bad password | error |
| test_login_empty | empty fields | validation error |

### Edge Cases
| Case | Input | Expected |
|------|-------|----------|
| empty email | "" | validation error |
| SQL injection | "'; DROP" | sanitized |
```

### Check tests.json Coverage

Map each 3-spec.md case to tests.json:

```markdown
## Coverage Analysis

| 3-spec.md Case | tests.json Test | Status |
|----------------|-----------------|--------|
| test_login_valid | T00001-01 | COVERED |
| test_login_invalid | T00001-02 | COVERED |
| test_login_empty | (none) | MISSING |
| edge: empty email | (none) | MISSING |
| edge: SQL injection | (none) | MISSING |
```

### Check Script Coverage

For script-based tests, read the test file:

```python
# tests/test_auth.py
def test_login_valid(): ...
def test_login_invalid(): ...
# Missing: test_login_empty, edge cases
```

Compare to 3-spec.md:

```markdown
## Script Coverage

File: tests/test_auth.py

| 3-spec.md Case | Function | Status |
|----------------|----------|--------|
| test_login_valid | test_login_valid() | COVERED |
| test_login_invalid | test_login_invalid() | COVERED |
| test_login_empty | (none) | MISSING |
| edge: empty email | (none) | MISSING |
| edge: SQL injection | (none) | MISSING |

Coverage: 2/5 (40%)
```

---

## Step 5: Replay Verification (Full Mode)

For critical validations, actually replay the trajectory:

### Replay Steps

1. Set up same environment (config from tests.json)
2. Execute each `do:` action
3. Verify each `verify:` check
4. Compare results to recorded trajectory

### Discrepancy Report

```markdown
## Replay Results

| Step | Recorded | Actual | Match |
|------|----------|--------|-------|
| browser:navigate:/login | OK | OK | YES |
| element:#login-form exists | PASS | PASS | YES |
| browser:fill:#email | OK | OK | YES |
| url contains /dashboard | PASS | FAIL | NO |

Discrepancy at step 4: URL is /login, not /dashboard
Possible causes:
- Implementation changed since test
- Test was recorded incorrectly
- Environment difference
```

---

## Step 6: Generate Report

### Quick Validation Report

```markdown
## Quick Validation: T00001

| Check | Status |
|-------|--------|
| tests.json exists | OK |
| All required tests have trajectory | OK |
| Screenshots present | 1 missing |
| TDD markers present | OK |

Result: WARNINGS (1 missing screenshot)
```

### Full Validation Report

```markdown
## Full Validation: T00001

### Trajectory
| Test | RED | GREEN | Complete |
|------|-----|-------|----------|
| T00001-01 | OK | OK | YES |
| T00001-02 | OK | OK | YES |

### Evidence
| Type | Expected | Found | Status |
|------|----------|-------|--------|
| Screenshots | 4 | 3 | 1 MISSING |
| Logs | 2 | 2 | OK |

### Coverage
| Source | Cases | Covered | % |
|--------|-------|---------|---|
| 3-spec.md | 8 | 6 | 75% |
| Edge cases | 5 | 2 | 40% |

### Issues
1. Missing screenshot: T00001-01_dashboard.png
2. Missing test coverage for: test_login_empty, edge cases

Result: INCOMPLETE (75% coverage, missing evidence)
```

---

## Checklist

### Trajectory Validation
- [ ] All passed tests have trajectory
- [ ] [RED] markers for TDD tickets
- [ ] [GREEN] markers with timestamps
- [ ] All `do:` and `verify:` entries present
- [ ] No suspiciously generic entries

### Evidence Validation
- [ ] Screenshots exist for visual tests
- [ ] Screenshot names follow convention
- [ ] Log evidence present
- [ ] Script outputs captured

### Coverage Validation
- [ ] 3-spec.md test cases mapped
- [ ] Edge cases covered
- [ ] Script functions match spec cases
- [ ] Coverage percentage acceptable (aim for >80%)

### Replay (if full mode)
- [ ] Environment matches config
- [ ] Steps produce same results
- [ ] No discrepancies

---

## Example Run

```
$ /pmc:validate T00001

## Validating T00001: User Authentication

### Trajectory Check
| Test | Trajectory | TDD Markers | Status |
|------|------------|-------------|--------|
| T00001-01 | 12 entries | RED, GREEN | VALID |
| T00001-02 | 8 entries | RED, GREEN | VALID |
| T00001-03 | (empty) | - | INVALID |

### Evidence Check
| Expected | Status |
|----------|--------|
| login-page.png | FOUND |
| dashboard.png | FOUND |
| error-state.png | MISSING |

### Coverage Check
| 3-spec.md Cases | Covered |
|-----------------|---------|
| Unit tests (5) | 5/5 |
| Integration (3) | 2/3 |
| Edge cases (4) | 2/4 |

Total: 9/12 (75%)

### Issues Found
1. T00001-03 has no trajectory but status=passed
2. Missing screenshot: error-state.png
3. Missing coverage:
   - integration: concurrent_login
   - edge: unicode_email
   - edge: max_length_password

### Recommendation
- Re-run T00001-03 and record trajectory
- Add missing screenshot
- Add tests for uncovered cases

Result: NEEDS ATTENTION
```

---

## Auto-Fix Options

Some issues can be auto-fixed:

| Issue | Fix |
|-------|-----|
| status=passed, empty trajectory | Reset status to "pending" |
| Missing screenshots | Run test again with screenshot capture |
| Low coverage | Generate stub tests for missing cases |

```
/pmc:validate T00001 --fix

Auto-fixing:
- Reset T00001-03 status to pending
- Generated test stubs for 3 uncovered cases

Remaining manual fixes needed:
- Run T00001-03 with proper trajectory recording
- Add error-state.png screenshot
```
