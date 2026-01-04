---
Summary: Ticket document formats (1-definition, 2-plan, 3-spec, 4-progress, 5-final) with TDD workflow, status tracking, and archive procedures.
---

# Ticket Document Formats

Tickets are bite-size features. Each ticket has 5 documents - simplified versions of main docs.

## Design Principles

### Why Tickets Exist

1. **Bite-size scope** - PRDs define features, but features are too large to implement in one go. Tickets break features into implementable chunks.

2. **Structured workflow** - Each document serves a specific phase:
   - Definition → Plan → Spec → Progress → Final
   - Forces thinking before coding

3. **Progress tracking** - `4-progress.md` tracks across sessions. I (Claude) may lose context between sessions; this document preserves state.

4. **Programmatic completion** - `5-final.md` with `Status: COMPLETE` or `Status: BLOCKED` allows scripts to determine if ticket is done. No ambiguity.

5. **Accountability** - Documents create paper trail. Can review what was planned vs what was done.

### Ticket vs PRD

| PRD | Ticket |
|-----|--------|
| Feature-level (large) | Task-level (small) |
| What to build | How to build one piece |
| Multiple tickets per PRD | One focused deliverable |
| Lives in `1-prd/` | Lives in `tickets/T0000N/` |

### Document Flow

```
1-definition.md    What to build (mini-PRD)
       ↓
2-plan.md          How to build
       ↓
3-spec.md          Technical details
       ↓
4-progress.md      Track progress including test development (update throughout)
       ↓
5-final.md         Completion marker
       ↓
REFLECTION         Review session, update kb (patterns/code-maps/sops/refs)
       ↓
ARCHIVE            Move to archive/, update index + 3-plan/
```

**Rationale for 5 documents:** Test notes merged into 4-progress.md since test development is part of overall progress. `tests.json` remains source of truth for test definitions.

### When to Create Each Document

| Document | When to create |
|----------|----------------|
| `1-definition.md` | When ticket is identified |
| `2-plan.md` | Before starting implementation |
| `3-spec.md` | Before starting implementation |
| `4-progress.md` | **At ticket creation** (Status: PLANNED) |
| `tests.json` | After 3-spec, **before** implementation (TDD) |
| `5-final.md` | When ticket reaches terminal state |

### Test-Driven Development (TDD)

**TDD is mandatory by default.** Tests are written before implementation.

#### TDD Workflow

```
3-spec.md → tests.json → verify RED → implement → GREEN → refactor → repeat
```

1. **Write tests first** - Create `tests.json` after 3-spec, before any implementation
2. **Verify RED** - Confirm tests fail (no implementation exists yet)
3. **Implement to GREEN** - Write minimal code to pass tests
4. **Refactor** - Clean up while keeping tests green
5. **Repeat** - Next test cycle

#### Opting Out (Trivial Tickets Only)

For trivial tickets (single-file fix, typo, config change), add to 1-definition.md:

```markdown
## Constraints

- TDD: no (trivial: {reason})
```

Examples of trivial:
- Fix typo in error message
- Update config value
- Add comment/docstring
- Rename variable

If in doubt, use TDD.

### Completion Criteria

A ticket is complete when:
1. All required tests in `tests.json` have `status: passed`
2. `5-final.md` exists with `## Status\n\nCOMPLETE`

### Status Values

- `4-progress.md` Status: `PLANNED` → ticket created, not started
- `4-progress.md` Status: `IN_PROGRESS` → work started
- `5-final.md` Status: `BLOCKED` → cannot proceed, needs human input (includes abandoned/cancelled)
- `5-final.md` Status: `COMPLETE` → done, ready to archive

### Terminal States

Terminal states require `5-final.md`:
- `BLOCKED` → cannot proceed, needs human input (includes abandoned/cancelled)
- `COMPLETE` → done, ready to archive

**Note:** Abandoned or cancelled tickets use `5-final.md` with `BLOCKED` status explaining reason, then archive normally. This is manual/special case processing.

### Why 5 Documents

Each serves distinct purpose:
- **1-definition**: Scope control (prevent creep)
- **2-plan**: Think before code
- **3-spec**: Technical details (API, data models, state transitions)
- **4-progress**: Session continuity + test development notes
- **5-final**: Completion signal + summary

Test notes merged into progress because test development is progress. `tests.json` is source of truth for test definitions.

## Location

```
.pmc/docs/tickets/T0000N/
├── 1-definition.md      # Mini-PRD: what/scope/acceptance, add to index
├── 2-plan.md            # Implementation approach
├── 3-spec.md            # Technical details
├── 4-progress.md        # Progress tracking + test development
└── 5-final.md           # Completion marker (BLOCKED | COMPLETE)
```

Screenshots go in `.pmc/docs/tests/tickets/T0000N/screenshots/` alongside test definitions.

## 1-definition.md

Mini-PRD for the ticket.

```markdown
# T0000N: {Title}

## What

[One paragraph - what needs to be done and why]

## Scope

- [Specific deliverable]
- [Specific deliverable]

## Out of Scope

- [Explicit exclusion]

## Acceptance Criteria

- [ ] [Testable condition]
- [ ] [Testable condition]

## Constraints

- [Technical limitation or dependency]

## Related

- .pmc/docs/1-prd/feat-xxx.md
```

## 2-plan.md

Implementation plan.

```markdown
# T0000N: Plan

## Approach

[One paragraph summary of how to implement]

## Steps

1. [Step with detail]
2. [Step with detail]
3. [Step with detail]

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| {what} | {chosen} | {why} |

## Files to Modify

| File | Changes |
|------|---------|
| `path/file.py` | [what changes] |
| `path/new.py` | [create, purpose] |

## Risks (optional)

- [Risk → mitigation]
```

### Required Sections

| Section | Purpose | Validated By |
|---------|---------|--------------|
| Approach | Strategy summary | - |
| Steps | Ordered implementation | No TBD/TODO markers |
| Technical Decisions | Design choices | Table must exist |
| Files to Modify | Impact scope | Table format |

**Avoid placeholders:** Do not use `TBD`, `TODO`, `???`, or `[TBD]` in plans. Resolve all decisions before implementation.

## 3-spec.md

Technical specification with test requirements. **This is the TDD contract.**

```markdown
# T0000N: Spec

## Test Environment Setup

### Prerequisites
- [tools, versions required]
- [services that must be running]

### Environment Variables
```bash
export VAR=value
# Or: None required.
```

### Database/State Setup
```bash
# Commands to prepare state, or: None required.
```

## Mock Data

### Files Required

| File | Purpose | Create How |
|------|---------|------------|
| {path} | {what it provides} | {command or manual} |

*Or: None required.*

## Test Cases

### Unit Tests

| Test | Input | Expected | File |
|------|-------|----------|------|
| {name} | {input} | {output} | tests/unit/{file}.py |

### Integration Tests

| Test | Setup | Action | Verify |
|------|-------|--------|--------|
| {name} | {how to set up} | {what to do} | {what to check} |

## E2E Test Procedure

### Setup
1. {prepare environment}
2. {prepare data}
3. {start services}

### Execution
1. {action to perform}
2. {action to perform}

### Verification

| Check | Expected |
|-------|----------|
| {what to check} | {expected result} |
| Screenshot | Save to `evidence/{ticket}-{name}.png` |

### Teardown
1. {cleanup step}

## Edge Cases

| Case | Input | Expected Behavior |
|------|-------|-------------------|
| {edge case} | {input} | {handling} |

## Open Questions

*(Resolve ALL before implementation - mark with RESOLVED)*

1. {question} - RESOLVED: {answer}
2. {question} - RESOLVED: {answer}

## API (if applicable)

### POST /api/example
- Request: `{field: type}`
- Response: `{field: type}`
- Errors: 400, 500

## Data Models (if applicable)

### ModelName
- field_name: type - description

## State Transitions (if applicable)

```
draft → pending → active → completed
          ↓
       rejected
```
```

### Required Sections for Validation

| Section | Required | Validated By |
|---------|----------|--------------|
| Test Environment Setup | Yes | Prerequisites subsection exists |
| Environment Variables | Yes | Documented or "None required" |
| Mock Data | Recommended | Table or "None required" |
| Unit Tests | Yes | Table with Input/Expected columns |
| Integration Tests | Yes | Table with Setup/Action/Verify |
| E2E Test Procedure | Yes | Has Setup, Execution, Verification subsections |
| Edge Cases | Recommended | Table format |
| Open Questions | Yes | All marked RESOLVED or empty |

### Manual Verification Requirements

When E2E requires visual/manual checks, document clearly:

```markdown
### Verification

| Check | Expected | How to Verify |
|-------|----------|---------------|
| UI renders | Dashboard shows | Screenshot: `evidence/dashboard.png` |
| Animation smooth | No jank | Record 5-second capture |
| Output correct | Matches spec | Manual inspection |
```

**Key:** Every manual check needs a capture/record instruction.

## 4-progress.md

Notes during **entire ticket workflow** including test development.

**IMPORTANT:** Created at ticket creation time (not when work starts).

### Frontmatter Format

The first lines of 4-progress.md use a pipe-delimited frontmatter for programmatic indexing:

```markdown
---
T0000N|PLANNED|Brief Title|Initial planning complete, ready for implementation
---
```

Format: `<ticket id>|<status>|<title>|<progress summary>`

| Field | Description |
|-------|-------------|
| ticket id | T0000N format |
| status | PLANNED, IN_PROGRESS |
| title | Brief ticket title |
| progress summary | Current state + important references (GitHub issue #, PR #, etc.) |

### Progress Summary Content

The progress summary should include:
- Current state (what's happening)
- **Important references** (GitHub issue #, PR #, related tickets)
- Key blockers or next steps

**Examples:**
```
# GitHub issue origin
T00015|IN_PROGRESS|Fix login bug|GH#42, implementing OAuth fix

# Multiple references
T00020|PLANNED|Add search|GH#55, depends on T00019

# No external reference
T00025|IN_PROGRESS|Refactor CLI|2/4 TDD cycles complete
```

### Purpose

- Track what I did, what worked, what didn't
- Preserve context between sessions
- Document blockers for human review
- Record decisions and reasoning
- Track test development notes (source of truth is `tests.json`)
- **Provide programmatic indexing** via frontmatter

### Initial State (at ticket creation)

```markdown
---
T0000N|PLANNED|Brief Title|GH#42, pending implementation
---

# T0000N: Progress

## Status

PLANNED

## References

- GitHub: #42

## Next

- [Steps to begin implementation]
```

### Active State (during work)

```markdown
---
T0000N|IN_PROGRESS|Brief Title|GH#42, 2/5 TDD cycles complete
---

# T0000N: Progress

## Status

IN_PROGRESS

## TDD Cycles

### Cycle 1: {feature/behavior}
- [x] RED: test fails ({reason})
- [x] GREEN: implemented {what}
- [x] REFACTOR: {what was cleaned}

### Cycle 2: {feature/behavior}
- [x] RED: test fails ({reason})
- [ ] GREEN: ...
- [ ] REFACTOR: ...

## Done

- [What was accomplished]
- [Decision made and why]
- [Approach that worked]

## Next

- [What to do next]
- [Open questions to resolve]

## Test Development

- Test file: `.pmc/docs/tests/tickets/T0000N/tests.json`
- Required: X tests, Optional: Y tests
- RED verified: [list tests confirmed failing before impl]
- Infrastructure needed: [debug endpoints, test data, etc.]

## Issues (if any)

**{Issue Title}**: {description}
- Tried: {what was attempted}
- Blocked: yes/no
- Need: {what's needed from human}

## Notes

[Session notes, observations, things to remember]
```

### What to Record

- Implementation decisions and reasoning
- Approaches tried (successful and failed)
- Blockers encountered
- Questions for human
- Test development observations
- Anything useful for next session

## 5-final.md

Completion marker. Existence + terminal status = ticket done.

```markdown
# T0000N: Complete

Status: COMPLETE

## Summary

[One paragraph - what was accomplished]

## Changes

- `path/file.py`: [what changed]
- `path/new.py`: [created, purpose]

## Tests

All required tests passing: X/X

## Limitations (optional)

- [Known limitation]

## Revealed Intent

User preferences and clarifications discovered during this ticket:
- [Preference/clarification discovered during iterative work]
- [Design choice user expressed]

## Declared Use-Cases

Specific scenarios user mentioned this solves:
- [Use-case or scenario user described]

## Open Questions

Unresolved items for future reference:
- [Question that wasn't answered]
- [Decision deferred to later]

## Learned

Reflection prompts (answer what applies):
- Pattern discovered? → document in 6-patterns/
- Code flow mapped? → update 5-code-maps/
- Useful research? → save in 6-references/
- Repetitive procedure? → create 2-sop/

### What worked
- [Approach/tool/technique that was effective]

### What to improve
- [What could be done better next time]

### KB updates made
- [List any docs created/updated during reflection]
```

### Intent Capture Sections

These sections preserve user context that emerges during iterative work:

| Section | Purpose | Example |
|---------|---------|---------|
| Revealed Intent | Preferences user expressed | "User prefers tabs over spaces" |
| Declared Use-Cases | Scenarios user described | "Used for CI pipeline validation" |
| Open Questions | Unresolved items | "Should we support Python 3.10?" |

**Why capture this?** During implementation, users clarify requirements, express preferences, and describe use-cases. This information is valuable but easily lost between sessions. Capturing it in 5-final.md preserves context for future work.

### Status Values

| Status | Meaning |
|--------|---------|
| `COMPLETE` | Successfully done, all tests pass |
| `BLOCKED` | Cannot proceed - includes abandoned/cancelled with reason |

**For BLOCKED tickets**, add explanation after status:
```markdown
Status: BLOCKED

## Reason

[Why blocked: cancelled, abandoned, superseded by T00015, etc.]
```

## Programmatic Completion Check

```python
import re

def is_ticket_complete(ticket_id):
    final_path = f".pmc/docs/tickets/{ticket_id}/5-final.md"
    if not exists(final_path):
        return False
    content = read(final_path)
    return bool(re.search(r'Status:\s*COMPLETE', content, re.IGNORECASE))

def is_ticket_blocked(ticket_id):
    final_path = f".pmc/docs/tickets/{ticket_id}/5-final.md"
    if not exists(final_path):
        return False
    content = read(final_path)
    return bool(re.search(r'Status:\s*BLOCKED', content, re.IGNORECASE))
```

## Document Creation Order

1. `1-definition.md` - Define what to build, **add to index**
2. `2-plan.md` - Plan how to build
3. `3-spec.md` - Technical details
4. `4-progress.md` - **Create at ticket creation** with Status: PLANNED (update throughout)
5. `5-final.md` - On terminal state (COMPLETE or BLOCKED)

## Index Format

`.pmc/docs/tickets/index.md` is a **lookup table** - quickly find ticket number by title (or vice versa):
```
T00001 Brief Name
T00002 Brief Name
```

One line per active ticket. Remove when archiving. Numbering comes from scanning directories (active + archive), not from this file.

## Reflection (before archiving)

When ticket reaches terminal state, REFLECT:

1. **Review session**: What worked? What didn't?
2. **Check for kb updates**:
   - New pattern discovered? → create `6-patterns/{problem}.md`
   - Code flow learned? → update `5-code-maps/{feature}.md`
   - Useful research? → save in `6-references/{topic}.md`
   - Repetitive procedure? → create `2-sop/{verb}-{noun}.md`
3. **Document in 5-final.md**: Fill out "Learned" section with findings and kb updates made

## Archiving

After REFLECTION, when ticket reaches terminal state (COMPLETE or BLOCKED):
1. Move `.pmc/docs/tickets/T0000N/` → `.pmc/docs/tickets/archive/T0000N/`
2. Remove from `.pmc/docs/tickets/index.md`
3. Add to `.pmc/docs/3-plan/archive.md`:
   - **Phase tickets**: Archived with phase (see plan-format.md)
   - **Standalone tickets**: Copy the line from index.md (e.g., `T00001 Brief Name`)

### Revisiting Completed Work

**No undo mechanism.** Once archived, tickets cannot be un-archived.

- **Not yet archived**: Can still revisit and modify in place
- **Already archived**: Report as known issue in `6-patterns/` (Status: open), then address as new ticket
