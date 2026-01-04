---
name: reflect
description: |
  Perform reflection after completing work to capture learnings in KB.
  Ensures knowledge is preserved for future sessions.

  WHEN TO USE:
  - After completing a ticket (before archiving)
  - After completing a phase
  - Before session ends (user says "wrapping up", "stopping for now")
  - When user says "reflect", "capture learnings", "what did we learn"

  CAPTURES:
  - Patterns: problems solved (resolved) OR issues found (open)
  - Decisions: architectural/design choices made
  - Code flows: new understanding of codebase
  - Procedures: repetitive tasks worth documenting
  - Learnings: in ticket's 5-final.md
---

# Reflect

Capture learnings and update KB after completing work.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand KB structure and document formats.

## When to Reflect

| Trigger | Scope |
|---------|-------|
| Ticket complete | Single ticket learnings |
| Phase complete | All phase tickets + integration learnings |
| Session ending | Everything done this session |
| User request | Specific topic or full review |

---

## Reflection Checklist

### 1. Patterns (6-patterns/)

**Ask:** Did we solve a problem or find an issue worth documenting?

| Type | Status | When to Create |
|------|--------|----------------|
| Solution | `Status: resolved` | Fixed a tricky bug, found a workaround |
| Known Issue | `Status: open` | Found limitation, bug we can't fix now |

**Format:** See [kb/references/pattern-format.md](../kb/references/pattern-format.md)

### 2. Decisions (5-decisions/D###-{name}.md)

**Ask:** Did we make architectural or design decisions?

**Format:** See [kb/references/decision-format.md](../kb/references/decision-format.md)

### 3. Code Maps (7-code-maps/)

**Ask:** Did we learn how code works that wasn't documented?

- Update existing code map if we learned more
- Create new code map if we explored new area
- Add `Last updated: YYYY-MM-DD` marker

### 4. Procedures (2-sop/)

**Ask:** Did we do something repetitive that should be a procedure?

Create SOP if:
- Same steps done 2+ times
- Complex process worth documenting
- Future sessions will need these steps

### 5. Research (8-research/)

**Ask:** Did we do research worth keeping?

Save if:
- External docs/APIs we referenced
- Design alternatives we explored
- Useful links or resources

### 6. Ticket Learnings (5-final.md)

**Always update** the ticket's 5-final.md with learnings, revealed intent, and decisions made.

**Format:** See [kb/references/ticket-formats.md](../kb/references/ticket-formats.md) (5-final.md section)

---

## Quick Reflection (Session Ending)

When time is short:

1. **Scan session** - What did we work on?
2. **Key learnings** - One-liner each
3. **Open issues** - Anything unresolved?
4. **Next steps** - What should next session start with?

Minimum output:
```markdown
## Session Reflection - YYYY-MM-DD

### Completed
- T0000N: {brief summary}

### Key Learnings
- {insight}

### Open Issues
- {issue} (pattern created: Y/N)

### Next Session
- Start with: {task}
```

---

## Reflection by Scope

### After Ticket

```
1. Update 5-final.md
   └── Learned section
   └── Revealed Intent (if any)

2. Check for patterns
   ├── Problem solved? → 6-patterns/{name}.md (Status: resolved)
   └── Issue found? → 6-patterns/{name}.md (Status: open)

3. Check for decisions
   └── Design choice made? → 5-decisions/D###-{name}.md

4. Update code map (if learned new code flow)
```

### After Phase

```
1. All ticket reflections done?

2. Integration learnings
   └── How tickets worked together
   └── Unexpected interactions

3. Update 4-status/health.md
   └── Test counts
   └── Open patterns count
   └── Technical debt notes

4. Phase retrospective
   └── What worked well
   └── What to improve
```

### Before Session End

```
1. Uncommitted learnings?
   └── Anything not yet captured in docs

2. Current state
   └── What's in progress
   └── What's blocked

3. Next session setup
   └── What to start with
   └── Any context to preserve
```

---

## Pattern Clarification

**Patterns are for BOTH solutions AND open issues:**

| I found... | Create pattern with... |
|------------|------------------------|
| Bug fix that was tricky | `Status: resolved` |
| Workaround for limitation | `Status: resolved` (document workaround) |
| Bug we can't fix now | `Status: open` (document for future) |
| Platform limitation | `Status: open` (document workaround if any) |
| Technical debt | `Status: open` (document scope) |

**Open patterns are valuable** - they prevent future developers from wasting time rediscovering known issues.

---

## Output

After reflection, confirm:

```
## Reflection Complete

### Updated
- [ ] 5-final.md: Learned section
- [ ] 6-patterns/: {N} patterns (X resolved, Y open)
- [ ] 5-decisions/D###-{name}.md: {N} decisions
- [ ] 7-code-maps/: {files updated}
- [ ] 2-sop/: {new procedures}
- [ ] 8-research/: {research saved}

### Open Items
- {Any unresolved issues}

### Next Steps
- {What to do next}
```
