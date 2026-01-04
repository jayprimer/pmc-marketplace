---
name: kb
description: |
  Knowledge base for session continuity. Maintains project documentation
  with fixed directory structure (.pmc/docs/) and formats for PRDs, SOPs,
  tickets (T0000N), patterns, decisions, code maps, research, and status.

  CRITICAL BEHAVIORS:
  1. LOOKUP FIRST - Before any task, check kb for existing docs (SOPs, patterns,
     code maps, status) that may guide the work. Don't reinvent what's documented.
  2. LEARN = DOCUMENT - When user says "learn X", record it in appropriate doc:
     - Procedure? → 2-sop/
     - Problem/solution? → 6-patterns/ (with Status: open|resolved)
     - Code flow? → 7-code-maps/
     - Research/notes? → 8-research/
     - Design decision? → 5-decisions/D###-{name}.md
     - User clarification? → capture in ticket 5-final.md
  3. CAPTURE INTENT - When user clarifies requirements or expresses preferences,
     record in ticket's 5-final.md (Revealed Intent section).
  4. INBOX - Direct user messages → 0-inbox/ for later processing by /pmc:dev or /pmc:plan.

  Use when: setting up docs structure, creating/managing tickets,
  documenting solutions, mapping code flows, archiving completed work,
  tracking project status, capturing user intent, OR when user asks to "learn" something.
---

# Knowledge Base

Manage project documentation with consistent structure and formats.

## Quick KB Overview

**Get the full docs structure:**
```
Bash: ls -la .pmc/docs/                    # Top-level directories
Bash: find .pmc/docs -type d -maxdepth 2   # All directories (2 levels)
Bash: find .pmc/docs -name "*.md" | head -50  # First 50 markdown files
```

**Or use Glob for specific areas:**
```
Glob: .pmc/docs/*/                  # All top-level directories
Glob: .pmc/docs/**/*.md             # All markdown files
```

This quick listing is sufficient for initial KB loading - you don't need to read all files upfront.

## Inbox (0-inbox/)

Task queue for messages from any source. Free-form format.

### When to Use Inbox

| Source | Action |
|--------|--------|
| Direct user message (not actionable now) | Write to `0-inbox/{descriptive-name}.md` |
| GitHub issue/PR notification | Write to `0-inbox/` → ticket with GH# in 4-progress.md |
| Slack message | Write to `0-inbox/` with context |
| Any external integration | Write to `0-inbox/` |

**GitHub Issues:** Arrive via inbox → create ticket → track `GH#N` in 4-progress.md frontmatter and References section.

### Inbox Format

Free-form. Include enough context for later processing:
```markdown
# {Brief Title}

Source: {user/github/slack/etc}
Date: {YYYY-MM-DD}

{Content - can be any format from the source}
```

### Processing

Inbox items are processed by `/pmc:dev` and `/pmc:plan` **after completing their primary directive**:
1. Check `0-inbox/` for pending items
2. Assess scope of each item
3. Create appropriate artifacts (single ticket, phase, PRD, etc.)
4. Remove processed items from inbox

**Do not process inbox items during the primary workflow** - only after completing the main task.

## Core Workflow

### 1. LOOKUP FIRST (Before Any Task)

Before starting work, check existing documentation.

**Why**: Don't waste time rediscovering. If it's documented, use it.

### 2. LEARN = DOCUMENT (When User Says "Learn X")

When user says "learn how to...", "remember this...", "note that...":

| What they learned | Document in |
|-------------------|-------------|
| How to do a task (commands, steps) | `2-sop/{verb}-{noun}.md` |
| How to fix a problem | `6-patterns/{problem}.md` (Status: resolved) |
| Known limitation/bug we can't fix | `6-patterns/{problem}.md` (Status: open) |
| Workaround for issue | `6-patterns/{problem}.md` (Status: open, with workaround) |
| Technical debt found | `6-patterns/{problem}.md` (Status: open) |
| How code works | `7-code-maps/{feature}.md` |
| Research, notes | `8-research/{topic}.md` |
| Design/architecture decision | `5-decisions/D###-{name}.md` |
| User preference/clarification | Ticket `5-final.md` (Revealed Intent) |
| Miscellaneous | `9-other/{topic}.md` |

**Always create the doc immediately.** Learning without documenting = lost knowledge.

### 3. UPDATE AFTER WORK

After completing tickets/tasks:
- New pattern discovered? → `6-patterns/`
- Code flow mapped? → `7-code-maps/`
- Procedure refined? → `2-sop/`
- Useful research? → `8-research/`

## Design Principles

### Why This Structure Exists

1. **Separation of concerns** - Each directory has one purpose. PRDs define what, SOPs define how, plans track progress, etc.

2. **Discoverability** - Descriptive filenames + glob/grep = no indexes needed (except tickets which use index.md as lookup table for number ↔ title mapping).

3. **Session continuity** - I (Claude) lose context between sessions. Docs preserve state.

4. **Programmatic verification** - JSON formats (tests) + status markers (5-final.md with BLOCKED | COMPLETE) allow scripts to track progress.

5. **Accountability** - Paper trail of decisions, plans, and outcomes.

### Document Hierarchy

```
PRD (feature-level)
 └── Phase (milestone)
      └── Ticket (implementable chunk)
           └── Tests (verification)
```

- **PRD** defines the feature (what/why)
- **Phase** groups tickets into milestones with E2E testing
- **Ticket** is one implementable piece (1-3 days work)
- **Tests** verify ticket completion

### When to Use What

| Situation | Action |
|-----------|--------|
| New feature idea | Create PRD in `1-prd/` |
| Breaking PRD into work | Plan phases in `3-plan/roadmap.md` |
| Starting implementation | Create ticket in `tickets/` + add to roadmap |
| Repetitive procedure | Document in `2-sop/` |
| Check project status | Read `4-status/features.md` or `4-status/health.md` |
| Made design/arch decision | Create `5-decisions/D###-{name}.md` |
| Solved a tricky problem | Document in `6-patterns/` (Status: resolved) |
| Found limitation we can't fix | Document in `6-patterns/` (Status: open) |
| Found technical debt | Document in `6-patterns/` (Status: open) |
| Explored codebase | Document in `7-code-maps/` |
| Research/notes | Store in `8-research/` |
| Miscellaneous doc | Store in `9-other/` |
| User clarified intent | Capture in ticket `5-final.md` |
| Ticket/phase complete | Run `/pmc:reflect` |

## End-to-End Workflow

### Feature Implementation Flow

```
1. IDEA
   └── Create PRD: .pmc/docs/1-prd/feat-{name}.md

2. PLANNING
   └── Add to .pmc/docs/3-plan/roadmap.md
       ├── Single ticket? → Add under "In Progress" or "Next"
       └── Multiple tickets? → Create phase with E2E ticket

3. IMPLEMENTATION (per ticket, TDD mandatory)
   ├── Create ticket: .pmc/docs/tickets/T0000N/
   │   ├── 1-definition.md (what) → add to index
   │   ├── 2-plan.md (how)
   │   ├── 3-spec.md (technical details)
   │   └── 4-progress.md (Status: PLANNED)
   │
   ├── TDD CYCLE (repeat per behavior):
   │   ├── Write test: .pmc/docs/tests/tickets/T0000N/tests.json
   │   ├── RED: verify test fails (no implementation)
   │   ├── GREEN: implement minimal code to pass
   │   ├── REFACTOR: clean up, keep green
   │   └── Track in 4-progress.md (TDD Cycles section)
   │
   └── Complete: 5-final.md with Status: COMPLETE (or BLOCKED)

   Note: TDD opt-out only for trivial tickets (typo, config). Add "TDD: no" to constraints.

4. PHASE E2E (final ticket of phase)
   └── Live end-to-end testing of entire phase
       └── All tickets working together

5. PHASE COMPLETE
   ├── Archive tickets
   ├── Update .pmc/docs/3-plan/archive.md
   └── Update code maps if needed

6. REFLECTION (after ticket or phase) → use /pmc:reflect
   ├── Review session: what worked, what didn't
   ├── Update kb:
   │   ├── Pattern discovered? → 6-patterns/ (Status: resolved)
   │   ├── Open issue found? → 6-patterns/ (Status: open)
   │   ├── Decision made? → 5-decisions/D###-{name}.md
   │   ├── Code flow learned? → 7-code-maps/
   │   ├── Useful research? → 8-research/
   │   └── Repetitive procedure? → 2-sop/
   └── Capture learnings in 5-final.md "Learned" section

7. REPEAT for next phase
```

## Git Worktree Integration

### Directory Layout

```
project/                     # Main worktree (main branch)
├── .pmc/
│   ├── docs/                # Git tracked
│   └── data/                # Gitignored (runtime artifacts)
├── .worktrees/              # Gitignored (feature worktrees)
│   ├── T00001/
│   └── phase-1/
└── src/, tests/, ...
```

### Branch Strategy

```
main
 └── phase/N
      ├── ticket/T00001
      ├── ticket/T00002
      └── ticket/T00003 (phase E2E)
```

| Type | Branch Pattern | Base Branch |
|------|----------------|-------------|
| Phase | `phase/N` | `main` |
| Ticket | `ticket/T0000N` | `phase/N` |

### Phase Development Flow

#### 1. Phase Start (main worktree)

```bash
git checkout main
git checkout -b phase/1
git push -u origin phase/1
```

Update `3-plan/roadmap.md` with phase tickets.

#### 2. Ticket Implementation

**Planning (main branch):**
```bash
git checkout main
# Create tickets/T00001/1-definition.md, 2-plan.md, 3-spec.md, 4-progress.md
git add .pmc/docs/tickets/
git commit -m "T00001: define ticket"
```

**Implementation (ticket worktree):**
```bash
git worktree add .worktrees/T00001 -b ticket/T00001 phase/1
cd .worktrees/T00001
# Implement, update 4-progress.md
git commit -m "T00001: implement feature"
# Write 5-final.md with Status: COMPLETE
git commit -m "T00001: complete"
git push -u origin ticket/T00001
```

**Merge to phase:**
```bash
git checkout phase/1
git merge ticket/T00001
git push
git branch -d ticket/T00001
git worktree remove .worktrees/T00001
```

#### 3. Phase E2E

```bash
git worktree add .worktrees/phase-1 phase/1
cd .worktrees/phase-1
# Run E2E tests, fix integration issues
# Write phase E2E ticket 5-final.md
git commit -m "T00003: phase 1 E2E complete"
git push
```

#### 4. Phase Complete

```bash
git checkout main
git merge phase/1
git push
# Archive tickets, update 3-plan/archive.md
git commit -m "phase 1: archive"
git worktree remove .worktrees/phase-1
git branch -d phase/1
```

### Git Commit Points

| Workflow Step | Branch | Commit Message |
|---------------|--------|----------------|
| Ticket planning | main | `T0000N: define ticket` |
| Implementation chunks | ticket/T0000N | `T0000N: {description}` |
| Ticket complete | ticket/T0000N | `T0000N: complete` |
| Phase E2E done | phase/N | `T0000N: phase N E2E complete` |
| Phase archive | main | `phase N: archive` |

### Quick Reference: What Goes Where

| I need to... | Create in... |
|--------------|--------------|
| Define a new feature | `1-prd/feat-{name}.md` |
| Plan phases/tickets | `3-plan/roadmap.md` |
| Start implementing | `tickets/T0000N/` |
| Document a procedure | `2-sop/{verb}-{noun}.md` |
| Check feature status | `4-status/features.md` |
| Track project health | `4-status/health.md` |
| Record a decision | `5-decisions/D###-{name}.md` |
| Save a solution | `6-patterns/{problem}.md` (Status: resolved) |
| Track known issue | `6-patterns/{problem}.md` (Status: open) |
| Map code flow | `7-code-maps/{feature}.md` |
| Store research | `8-research/{topic}.md` |
| Store misc docs | `9-other/{name}.md` |
| Write tests | `tests/tickets/T0000N/tests.json` |

## Configuration

Default docs directory: `.pmc/docs/`
Override in CLAUDE.md: `Docs directory: path/to/docs`

## Directory Structure

See [references/directory-structure.md](references/directory-structure.md) for the complete structure.

**Quick summary:**
```
.pmc/docs/
├── 0-inbox/        # Task queue from any source (free-form)
├── 1-prd/          # PRDs: feat-*, comp-*, infra-*
├── 2-sop/          # Procedures: {verb}-{noun}.md
├── 3-plan/         # roadmap.md, archive.md
├── 4-status/       # features.md, health.md, audits/
├── 5-decisions/    # D###-{name}.md (individual ADRs)
├── 6-patterns/     # Solutions/issues: Status: open|resolved
├── 7-code-maps/    # Feature traces
├── 8-research/     # Research & notes
├── 9-other/        # Miscellaneous free-form
├── tests/          # smoke/, core/, tickets/T0000N/
└── tickets/        # index.md, T0000N/, archive/
```

**Discovery:** Use `Glob` to list files, `Grep` to search content.

## Document Formats

**All format templates are in [references/](references/):**

| Document Type | Reference |
|--------------|-----------|
| Directory structure | [directory-structure.md](references/directory-structure.md) |
| PRDs | [prd-format.md](references/prd-format.md) |
| SOPs | [sop-format.md](references/sop-format.md) |
| Roadmap/Plans | [plan-format.md](references/plan-format.md) |
| Status docs | [status-formats.md](references/status-formats.md) |
| Decisions | [decision-format.md](references/decision-format.md) |
| Patterns | [pattern-format.md](references/pattern-format.md) |
| Code Maps | [codemap-format.md](references/codemap-format.md) |
| Research | [research-format.md](references/research-format.md) |
| Other | [other-format.md](references/other-format.md) |
| Tickets | [ticket-formats.md](references/ticket-formats.md) |
| Tests | [test-formats.md](references/test-formats.md) |

**Read the relevant reference file before creating/editing any document type.**

## Maintenance Rules

1. **Update tickets index** when creating/archiving
2. **Sequential numbering** for tickets and decisions - never skip
3. **Archive, don't delete** completed work
4. **Use templates exactly** - keep formats consistent
5. **Update 3-plan/** on completion
6. **Use descriptive filenames** - no index needed for other directories
7. **Keep code maps current** - update 7-code-maps/ after ticket or phase completion
8. **REFLECT after every ticket** - review session, update kb, capture learnings
9. **Branch from correct base** - tickets from phase
10. **Clean up worktrees** - remove after merge, don't leave stale worktrees
11. **Track decisions** - create 5-decisions/D###-{name}.md when making design choices
12. **Update health** - refresh 4-status/health.md after phase completion
13. **Capture intent** - record user clarifications in ticket 5-final.md
14. **Use pattern status** - mark 6-patterns/ as open (known issue) or resolved (solution)
15. **Resolve doc conflicts** - when parallel work touches same doc (pattern, code-map), merge at phase boundary: compare versions, combine insights, note both sources
