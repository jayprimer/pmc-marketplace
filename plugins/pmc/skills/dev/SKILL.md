---
name: dev
description: |
  Orchestrate KB development workflow from request to completion.
  Coordinates skills in sequence: kb → plan → test → validate → complete → reflect → inbox.

  WORKFLOW:
  1. LOOKUP - /pmc:kb (check existing PRDs, patterns, code maps)
  2. PLAN - /pmc:plan + /pmc:plan-validation + /pmc:lint-kb
  3. IMPLEMENT - /pmc:test (TDD cycle: RED → GREEN → REFACTOR)
  4. VALIDATE - /pmc:validate + /pmc:ticket-status
  5. COMPLETE - /pmc:complete (write 5-final.md, commit)
  6. REFLECT - /pmc:reflect + /pmc:lint-kb
  7. INBOX - /pmc:inbox (process pending items)

  Use when:
  - User says "implement", "build", "develop", "work on"
  - Starting new feature or phase work
  - Need guided workflow from start to finish
  - User says "dev workflow", "full cycle"
---

# Development Workflow

Orchestrate complete KB development cycle from request to completion.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand KB structure and formats.

## State Announcements

**ALWAYS announce stage transitions** to make workflow progress clear:

```
=== ENTERING LOOKUP ===
[... do lookup work ...]

=== ENTERING PLAN ===
[... do planning work ...]

=== ENTERING IMPLEMENT (T00001) ===
[... TDD cycle ...]

=== ENTERING VALIDATE (T00001) ===
[... validation work ...]

=== ENTERING COMPLETE (T00001) ===
[... finalization ...]

=== ENTERING REFLECT ===
[... capture learnings ...]

=== ENTERING INBOX ===
[... process pending items ...]

=== PHASE COMPLETE ===
[... archive and next ...]
```

**Why:** Makes it easy to:
- Track where you are in the workflow
- Resume after interruption
- Identify which stage failed if issues occur

## Workflow Overview

```
USER REQUEST
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. LOOKUP                                                   │
│    /pmc:kb                                                  │
│    Check existing: PRDs, patterns, code maps, SOPs          │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PLAN                                                     │
│    /pmc:plan           → Create PRD, tickets, roadmap       │
│    /pmc:plan-validation → Verify plan completeness          │
│    /pmc:lint-kb        → Check doc formats                  │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. IMPLEMENT (per ticket)                                   │
│    /pmc:test           → TDD cycle (RED → GREEN → REFACTOR) │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. VALIDATE                                                 │
│    /pmc:validate       → Check trajectory, coverage         │
│    /pmc:ticket-status  → Determine next step                │
│    Loop if next_step != needs-final                         │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. COMPLETE                                                 │
│    /pmc:complete       → Write 5-final.md, commit           │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. REFLECT                                                  │
│    /pmc:reflect        → Capture learnings to KB            │
│    /pmc:lint-kb        → Verify new docs                    │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. INBOX (after primary work complete)                      │
│    /pmc:inbox          → Process pending items from 0-inbox │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  PHASE E2E (if multi-ticket phase)
     /pmc:ticket-status check_phase.py
     │
     ▼
  PHASE COMPLETE
     Archive tickets, /pmc:reflect, /pmc:lint-kb
     │
     ▼
  NEXT TICKET/PHASE
```

---

## Step 1: LOOKUP

**Skill:** `/pmc:kb`

Check existing KB before starting new work.

**Decision point:**
- Found existing work? → Continue from current state
- New work? → Proceed to PLAN

---

## Step 2: PLAN

**Skills:**
- `/pmc:plan` → Create PRD (if large), tickets, add to roadmap
- `/pmc:plan-validation T0000N` → Verify plan is complete and actionable
- `/pmc:lint-kb` → Verify doc formats before implementation

**Flow:**
1. Run `/pmc:plan` to create artifacts
2. Run `/pmc:plan-validation T0000N` - must return exit 0 (ready)
3. Run `/pmc:lint-kb` to verify formats

---

## Step 3: IMPLEMENT

**Skill:** `/pmc:test T0000N`

Execute TDD cycle per ticket:
- **RED**: Verify test fails before implementation
- **GREEN**: Implement minimal code to pass
- **REFACTOR**: Clean up, keep tests green

---

## Step 4: VALIDATE

**Skills:**
- `/pmc:validate T0000N` → Check trajectory, coverage, evidence
- `/pmc:ticket-status T0000N` → Determine next step

**Status loop:**
```
┌──────────────────────────────────────┐
│ /pmc:ticket-status T0000N            │
└──────────────────────────────────────┘
         │
    ┌────┴────┬─────────┬──────────┬──────────┐
    ▼         ▼         ▼          ▼          ▼
needs-final needs-impl tests-   blocked    other
    │         │       failing     │          │
    ▼         ▼         ▼         ▼          ▼
 Step 5    Step 3   Step 3    Escalate   Handle
          (impl)   (fix)                per status
```

---

## Step 5: COMPLETE

**Skill:** `/pmc:complete T0000N`

- Write 5-final.md with Status: COMPLETE (or BLOCKED)
- Update 4-progress.md
- Commit: "T0000N: complete"

---

## Step 6: REFLECT

**Skills:**
- `/pmc:reflect` → Capture learnings to KB (patterns, decisions, code maps)
- `/pmc:lint-kb` → Verify new docs formatted correctly

---

## Step 7: INBOX

**Skill:** `/pmc:inbox`

Process pending items from 0-inbox/ AFTER primary work complete.

---

## Phase Workflow

For multi-ticket phases:

```
1. /pmc:kb                    # Lookup first
2. /pmc:plan                  # PRD + phase + tickets
3. /pmc:lint-kb               # Verify doc formats
4. FOR each ticket in phase:
   ├── /pmc:plan-validation   # Validate plan before impl
   ├── /pmc:test              # TDD cycle
   ├── /pmc:validate          # Verify tests
   ├── /pmc:ticket-status     # Loop until needs-final
   ├── /pmc:complete          # Finalize ticket
   ├── /pmc:reflect           # Capture learnings
   └── /pmc:lint-kb           # Verify new docs
5. Phase E2E ticket           # Integration testing
6. Archive all phase tickets
7. /pmc:reflect               # Phase-level learnings
8. /pmc:lint-kb               # Final doc validation
9. /pmc:inbox                 # Process pending items
```

---

## Single Ticket Flow

For small, standalone work:

```
1. /pmc:kb                   # Lookup first
2. /pmc:plan                 # Create ticket + roadmap
3. /pmc:plan-validation      # Validate plan complete
4. /pmc:lint-kb              # Verify doc formats
5. /pmc:test                 # TDD cycle
6. /pmc:validate             # Check trajectory, coverage
7. /pmc:ticket-status        # Loop until needs-final
8. /pmc:complete             # Finalize ticket
9. /pmc:reflect              # Capture learnings
10. /pmc:lint-kb             # Verify new docs
11. Archive ticket           # Move to archive/
12. /pmc:inbox               # Process pending items
```

---

## Skill Reference

| Step | Skill | Purpose |
|------|-------|---------|
| 1. LOOKUP | `/pmc:kb` | Understand structure, check existing |
| 2. PLAN | `/pmc:plan` | Create PRD, tickets, roadmap |
| 2. PLAN | `/pmc:plan-validation` | Verify plan completeness |
| 2. PLAN | `/pmc:lint-kb` | Validate doc formats |
| 3. IMPLEMENT | `/pmc:test` | Execute TDD cycle |
| 4. VALIDATE | `/pmc:validate` | Check trajectory, coverage |
| 4. VALIDATE | `/pmc:ticket-status` | Determine next step |
| 5. COMPLETE | `/pmc:complete` | Write 5-final.md, commit |
| 6. REFLECT | `/pmc:reflect` | Capture learnings to KB |
| 6. REFLECT | `/pmc:lint-kb` | Verify new docs |
| 7. INBOX | `/pmc:inbox` | Process pending items |

**Supporting skills:**
- `/pmc:update-kb` - Sync KB docs with codebase (periodic)
- `/pmc:workflow` - Develop PMC workflows (automation)

---

## Handling Blocked Status

When `/pmc:ticket-status` returns `blocked`:

1. Check blocked_reason
2. Options:
   - Resolve blocker → continue
   - Create pattern (Status: open) → document issue
   - Escalate to user → get decision
   - Use `/pmc:complete` with BLOCKED status → move on
