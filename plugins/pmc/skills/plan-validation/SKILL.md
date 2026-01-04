---
name: plan-validation
description: |
  Validate planning documents before implementation begins.
  Checks ambiguity resolution, prerequisites, and testing methods.

  Use when:
  - Before starting implementation of a ticket
  - User says "validate plan", "check plan", "ready to implement?"
  - After completing 2-plan.md and 3-spec.md
  - Before TDD cycle begins
---

# Plan Validation

Validate planning documents are complete and actionable before implementation.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand KB structure.

## Quick Start

```bash
# Validate ticket plan
python scripts/validate_plan.py T00021

# Human-readable output
python scripts/validate_plan.py T00021 --format text
```

## What Gets Validated

### 1. Ambiguity Resolution

| Check | Source | What |
|-------|--------|------|
| TBD/TODO markers | 2-plan.md, 3-spec.md | No unresolved placeholders |
| Open Questions | 3-spec.md | All questions marked RESOLVED |
| Technical Decisions | 2-plan.md | Decisions table exists |

### 2. Prerequisites

| Check | Source | What |
|-------|--------|------|
| Required docs | ticket/ | 1-definition, 2-plan, 3-spec exist |
| Test Environment | 3-spec.md | Setup section with prerequisites |
| Environment Variables | 3-spec.md | Documented or marked "none" |
| Mock Data | 3-spec.md | Table or "none needed" |
| Dependencies | 1-definition.md | Listed or marked "none" |
| Files to Modify | 2-plan.md | Table of affected files |
| Roadmap entry | 3-plan/roadmap.md | Ticket listed |

### 3. Testing Methods

| Check | Source | What |
|-------|--------|------|
| Unit Tests | 3-spec.md | Table with Input/Expected |
| Integration Tests | 3-spec.md | Setup/Action/Verify pattern |
| E2E Procedure | 3-spec.md | Setup + Execution + Verification |
| Verification checks | 3-spec.md | Specific checklist (table/list) |
| Manual inspection | 3-spec.md | Clear capture/save instructions |
| Edge Cases | 3-spec.md | Table format |

## Output

```json
{
  "ticket_id": "T00021",
  "status": "issues",
  "summary": {
    "errors": 2,
    "warnings": 3,
    "passed": 12,
    "failed": 2
  },
  "checks_passed": ["3-spec.md exists", "E2E has Setup subsection", ...],
  "checks_failed": ["Missing E2E Verification subsection", ...],
  "issues": [
    {
      "severity": "error",
      "category": "testing",
      "message": "E2E Test Procedure missing 'Verification' subsection",
      "file": "3-spec.md",
      "line": 0
    }
  ]
}
```

## Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | valid | Plan ready for implementation |
| 1 | issues | Has warnings/errors but can proceed |
| 2 | blocked | Missing critical sections |
| 3 | not_found | Ticket not found |

## Validation Categories

### Ambiguity Checks

Detects unresolved planning items:

```markdown
# BAD - Will flag as error
## Steps
1. Configure the thing TBD
2. TODO: figure out auth

# GOOD - Resolved
## Steps
1. Configure OAuth2 with client_credentials flow
2. Auth handled by existing middleware (see 5-code-maps/auth.md)
```

Open Questions section must have all items resolved:

```markdown
# BAD
## Open Questions
1. Which database driver to use?
2. How to handle rate limiting?

# GOOD
## Open Questions
1. Which database driver to use? - RESOLVED: asyncpg for performance
2. How to handle rate limiting? - RESOLVED: Use existing RateLimiter class
```

### Prerequisites Checks

Test Environment Setup must be actionable:

```markdown
# BAD - Vague
## Test Environment Setup
Set up the test environment.

# GOOD - Specific
## Test Environment Setup

### Prerequisites
- Python 3.11+
- Docker running
- `pmc` installed from source

### Environment Variables
```bash
export TEST_DB_URL=sqlite:///test.db
export LOG_LEVEL=DEBUG
```

### Database Setup
```bash
pmc db migrate --test
```
```

### Testing Method Checks

E2E Test Procedure must have clear verification:

```markdown
# BAD - No verification specifics
## E2E Test Procedure
Run the workflow and check it works.

# GOOD - Specific verification
## E2E Test Procedure

### Setup
1. Create test directory: `mkdir /tmp/test-T00021`
2. Initialize: `cd /tmp/test-T00021 && pmc init`

### Execution
1. Run: `pmc run workflow.json -i ticket_id=T99990`
2. Wait for completion

### Verification

| Check | Expected |
|-------|----------|
| Exit code | 0 |
| Output contains | "Workflow completed successfully" |
| File created | `.pmc/docs/tickets/T99990/5-final.md` |
| Screenshot | Save terminal output to `evidence/T00021-e2e.png` |

### Teardown
1. `rm -rf /tmp/test-T00021`
```

### Manual Inspection

When manual verification needed, document how to capture evidence:

```markdown
### Verification

| Check | Expected | How to Verify |
|-------|----------|---------------|
| UI renders | Dashboard shows | Screenshot: `evidence/dashboard.png` |
| Animation smooth | No jank | Record: 5-second screen capture |
| Colors correct | Brand colors | Visual compare with `assets/brand.png` |
```

## Integration with Dev Workflow

Run before starting implementation:

```
PLAN
  ├── Create 1-definition.md
  ├── Create 2-plan.md
  ├── Create 3-spec.md
  │
  ▶ VERIFY: validate_plan.py T0000N
  │         └── Exit 0? → Ready for IMPLEMENT
  │         └── Exit 1? → Review warnings, fix if needed
  │         └── Exit 2? → BLOCKED - fix missing sections
  │
  └── IMPLEMENT begins
```

## Checklist

Before running validation:
- [ ] 1-definition.md has Summary, Scope, Success Criteria
- [ ] 2-plan.md has Approach, Steps, Technical Decisions, Files to Modify
- [ ] 3-spec.md has Test Environment, Test Cases, E2E Procedure, Edge Cases
- [ ] All TBD/TODO resolved
- [ ] Open Questions answered
- [ ] E2E has Setup/Execution/Verification
- [ ] Manual steps have capture instructions
