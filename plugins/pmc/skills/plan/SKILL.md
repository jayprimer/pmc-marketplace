---
name: plan
description: |
  Plan development work following KB skill's structured approach with PRDs,
  phases, tickets, TDD specifications, and parallel execution planning.

  WORKFLOW:
  1. KB LOOKUP - Check existing PRDs, patterns, code maps, SOPs
  2. SCOPE - Small (ticket only) or Large (PRD + phases)?
  3. PRD - Create for large work
  4. PHASES - Break into 2-5 tickets + Phase E2E
  5. TICKETS - Create with TDD spec (3-spec.md is critical)
  6. PARALLEL ANALYSIS - Dependency matrix, file conflicts, execution mode
  7. GIT SETUP - Phase branch, worktrees for parallel tickets
  8. QUESTIONS - Resolve all ambiguity before implementation

  Use when:
  - User asks to implement something non-trivial
  - User says "plan", "design", "how would you implement"
  - Task requires multiple files or sessions
  - Requirements are unclear
---

# Plan Development Work

Plan development tasks following KB skill's structured approach with PRDs, phases, tickets, TDD, and parallel execution.

## Prerequisites

**ALWAYS run /pmc:kb first** to understand KB structure, ticket formats, and TDD workflow.

## When to Use

**Plan when:**
- New feature requests
- Significant refactors
- Multi-step bug fixes
- User asks to plan work
- Requirements unclear

**Skip planning for:**
- Single typo fixes
- Config tweaks
- Pure documentation

---

## Planning Workflow

```
1. KB LOOKUP
   └── Check existing PRDs, patterns, code maps, SOPs

2. SCOPE DETERMINATION
   ├── Small (single ticket)? → Create ticket + add to roadmap.md
   └── Large (multiple tickets)? → Create PRD + phases

3. PRD CREATION (if large)
   └── .pmc/docs/1-prd/feat-{name}.md

4. ROADMAP UPDATE (always)
   └── Update .pmc/docs/3-plan/roadmap.md
       ├── Single ticket → Add under "In Progress" or "Next"
       └── Phase → Create phase section with tickets + E2E

5. TICKET CREATION (per ticket in phase)
   └── .pmc/docs/tickets/T0000N/
       ├── 1-definition.md
       ├── 2-plan.md
       ├── 3-spec.md (TDD spec)
       └── 4-progress.md (Status: PLANNED)

6. PARALLEL ANALYSIS (if multiple tickets)
   ├── Create dependency matrix
   ├── Analyze file conflicts
   └── Determine execution mode (parallel/sequential)

7. GIT SETUP (for phase work)
   ├── Create phase branch
   └── Create worktrees for parallel tickets

8. QUESTIONS RESOLUTION
   └── All ambiguity resolved before implementation
```

---

## Step 1: KB Lookup

**Always check KB first.**
**If found:** Reference in plan, don't duplicate.

---

## Step 2: Scope Determination

### Small Work (Single Ticket)

Criteria:
- Affects 1-3 files
- Clear scope, no ambiguity
- Can complete in one session

→ Create ticket + add to roadmap.md under "In Progress" or "Next"
→ Then proceed to Step 5 (Ticket Creation)

### Large Work (Phases)

Criteria:
- Multiple components affected
- Needs architectural decisions
- Will take multiple sessions

→ Continue to Step 3 (PRD Creation)

---

## Step 3: PRD Creation

For large work, create PRD first.

**File:** `.pmc/docs/1-prd/feat-{name}.md`

**Format:** See [kb/references/prd-format.md](../kb/references/prd-format.md)

---

## Step 4: Roadmap Update

**ALL tickets go in roadmap.md** - single or phased.

**File:** `.pmc/docs/3-plan/roadmap.md`

**Format:** See [kb/references/plan-format.md](../kb/references/plan-format.md)

### Guidelines

1. **Every ticket in roadmap** - Single tickets under In Progress/Next, phases as sections
2. **Each phase is independently testable** - Complete feature slice
3. **Last ticket is always Phase E2E** - Integration testing
4. **Phase size: 2-5 tickets** - Not too small, not too big
5. **Remove on completion** - Move to archive.md

---

## Step 5: Ticket Creation

Create ticket with TDD specification.

**Directory:** `.pmc/docs/tickets/T0000N/`

**Format:** See [kb/references/ticket-formats.md](../kb/references/ticket-formats.md) for all 5 ticket documents:
- `1-definition.md` - What to build (scope, success criteria)
- `2-plan.md` - How to build (approach, steps, files)
- `3-spec.md` - TDD spec (tests, environment, edge cases)
- `4-progress.md` - Progress log (created during work)
- `5-final.md` - Completion (status, learnings)

**Update Index:** Add to `.pmc/docs/tickets/index.md`:
```
T0000N Brief Title
```

---

## Step 6: Parallel Execution Analysis

For phases with multiple tickets, analyze parallelization potential.

### When to Use Parallel Execution

| Scenario | Use Parallel | Reason |
|----------|--------------|--------|
| Independent tickets (no shared files) | **Yes** | No merge conflicts |
| Tickets modify different modules | **Yes** | Minimal conflicts |
| Tickets share some files, different sections | **Maybe** | Careful merge needed |
| Tickets heavily modify same files | **No** | Sequential is safer |
| Phase E2E ticket | **No** | Must run after all complete |

### Create Dependency Matrix

Analyze ticket dependencies in roadmap:

```markdown
#### Dependency Matrix

| Ticket | Depends On | Blocks | Can Parallel With |
|--------|------------|--------|-------------------|
| T00001 | - | T00003 | T00002 |
| T00002 | - | - | T00001 |
| T00003 | T00001 | T00004 | - |
| T00004 | all | - | - (E2E) |
```

### Analyze File Conflicts

Check which tickets modify same files:

```markdown
#### File Ownership

| File | T00001 | T00002 | T00003 | Conflict Risk |
|------|--------|--------|--------|---------------|
| src/auth/login.py | ✓ | - | ✓ | MEDIUM |
| src/auth/session.py | - | ✓ | - | NONE |
| tests/test_auth.py | ✓ | ✓ | ✓ | HIGH |
```

**Conflict Risk Levels:**
- **NONE**: Different files, safe for parallel
- **LOW**: Same file, different sections
- **MEDIUM**: Same file, may touch same areas
- **HIGH**: Same file, likely conflicts - consider sequential

### Allocate Resources

Each parallel worktree needs isolated resources to avoid runtime conflicts.

```markdown
#### Resource Allocation

| Resource | Main | T00001 | T00002 | T00003 |
|----------|------|--------|--------|--------|
| Web Server Port | 3000 | 3001 | 3002 | 3003 |
| API Port | 8000 | 8001 | 8002 | 8003 |
| Database | dev.db | test_T00001.db | test_T00002.db | test_T00003.db |
| Redis Port | 6379 | 6380 | 6381 | 6382 |
| Temp Directory | /tmp/app | /tmp/app-T00001 | /tmp/app-T00002 | /tmp/app-T00003 |
| Browser Debug | 9222 | 9223 | 9224 | 9225 |
```

**Common Resources:**
- Network ports (web, API, WebSocket, debug)
- Databases (separate file/schema per worktree)
- Cache (Redis/Memcached - separate port or key prefix)
- File paths (temp dirs, logs, uploads)
- Browser debug ports (Chrome DevTools, Playwright)

**Per-Worktree Environment:** Create `.env.local` (gitignored) in each worktree:

```bash
# .worktrees/T00001/.env.local
PORT=3001
API_PORT=8001
DATABASE_URL=sqlite:///test_T00001.db
REDIS_PORT=6380
BROWSER_DEBUG_PORT=9223
```

### Determine Execution Mode

Add to roadmap phase header:

```markdown
### feat-auth: Phase 1 - Basic Login

**Execution Mode:** Parallel (2 concurrent)
**Phase Branch:** `phase/1`
```

Or for sequential:
```markdown
**Execution Mode:** Sequential (tickets share many files)
```

---

## Step 7: Git Worktree Setup

### Create Phase Branch

```bash
git checkout main
git pull origin main
git checkout -b phase/1
git push -u origin phase/1
```

### Create Worktrees for Parallel Tickets

For each ticket that can run in parallel:

```bash
# Create worktree for T00001
git worktree add .worktrees/T00001 -b ticket/T00001 phase/1

# Create worktree for T00002 (parallel)
git worktree add .worktrees/T00002 -b ticket/T00002 phase/1
```

### Verify Setup

```bash
git worktree list

# Expected:
# /path/to/project          abc1234 [main]
# /path/to/project/.worktrees/T00001  def5678 [ticket/T00001]
# /path/to/project/.worktrees/T00002  ghi9012 [ticket/T00002]
```

### Update Roadmap with Assignment

```markdown
#### Ticket Status

| Ticket | Branch | Worktree | Assignee | Status |
|--------|--------|----------|----------|--------|
| T00001 | `ticket/T00001` | `.worktrees/T00001` | agent-1 | ready |
| T00002 | `ticket/T00002` | `.worktrees/T00002` | agent-2 | ready |
| T00003 | - | - | - | waiting (T00001) |
| T00004 | - | - | - | Phase E2E (last) |
```

---

## Step 8: Questions Resolution

**All questions must be resolved before implementation.**

### Asking Format

```markdown
## Questions Before Implementation

1. **{Topic}**
   - Question: {what needs clarification}
   - Option A: {choice}
   - Option B: {choice}
   - Recommendation: {if any}
```

### Recording Decisions

Add architectural decisions to `.pmc/docs/5-decisions/D###-{name}.md`.

---

## Merge Workflow (After Implementation)

### Merge Order Strategy

1. Tickets with no dependencies first
2. Tickets that others depend on before dependents
3. Tickets that modify shared files - coordinate timing
4. Phase E2E always last

### Merge Ticket to Phase

```bash
git checkout phase/1
git pull origin phase/1
git merge ticket/T00001 --no-ff -m "Merge T00001: Login form UI"
git push origin phase/1
```

### Update Dependent Worktrees

After merging, sync other ticket branches:

```bash
cd .worktrees/T00002
git fetch origin
git merge origin/phase/1 -m "Sync with phase/1 after T00001 merge"
```

### Merge Phase to Main

After all tickets (including E2E) complete:

```bash
git checkout main
git pull origin main
git merge phase/1 --no-ff -m "Merge Phase 1: Basic Login"
git push origin main
```

---

## Cleanup Workflow

### After Ticket Complete

```bash
# Remove worktree
git worktree remove .worktrees/T00001

# Delete local branch
git branch -d ticket/T00001

# Delete remote branch
git push origin --delete ticket/T00001
```

### After Phase Complete

```bash
# Remove phase worktree (if used)
git worktree remove .worktrees/phase-1

# Delete branches
git branch -d phase/1
git push origin --delete phase/1

# Cleanup
git worktree prune
git worktree list
```

---

## Next Step: Inbox Processing

After completing planning, use `/pmc:inbox` to process pending items from 0-inbox/.

---

## Phase E2E Ticket

Last ticket of each phase is E2E testing.

**Format:** See [kb/references/ticket-formats.md](../kb/references/ticket-formats.md) (Phase E2E section)

---

## Checklists

### KB Lookup
- [ ] PRDs checked
- [ ] Patterns checked
- [ ] Code maps checked
- [ ] SOPs checked
- [ ] Roadmap checked

### Ticket
- [ ] 1-definition.md complete
- [ ] 2-plan.md with steps
- [ ] 3-spec.md with TDD spec
- [ ] 4-progress.md with Status: PLANNED
- [ ] Test environment documented
- [ ] Mock data documented
- [ ] E2E procedure documented
- [ ] Edge cases listed
- [ ] Questions resolved
- [ ] Added to index.md
- [ ] Added to roadmap.md

### Phase
- [ ] PRD exists (for features)
- [ ] Phase in roadmap.md
- [ ] 2-5 tickets per phase
- [ ] Phase E2E ticket included
- [ ] Each phase independently testable

### Parallel Execution
- [ ] Dependency matrix created
- [ ] File conflicts analyzed
- [ ] Resource allocation table created
- [ ] Per-worktree .env.local documented
- [ ] Execution mode determined
- [ ] Phase branch created
- [ ] Worktrees created for parallel tickets
- [ ] Ticket status table in roadmap
- [ ] Assignees documented

### Cleanup
- [ ] All ticket worktrees removed
- [ ] All ticket branches merged and deleted
- [ ] Phase worktree removed
- [ ] Phase branch merged and deleted
- [ ] `git worktree prune` run
- [ ] No stale worktrees
- [ ] Allocated resources cleaned up (temp DBs, logs, temp dirs)

---

## Example: Parallel Phase Planning

```markdown
## In Progress

### feat-auth: Phase 1 - Basic Login

**Execution Mode:** Parallel (2 concurrent)
**Phase Branch:** `phase/1`

#### Dependency Matrix

| Ticket | Depends On | Can Parallel With |
|--------|------------|-------------------|
| T00001 | - | T00002 |
| T00002 | - | T00001 |
| T00003 | T00001 | - |
| T00004 | all | - (E2E) |

#### Resource Allocation

| Resource | Main | T00001 | T00002 |
|----------|------|--------|--------|
| Web Port | 3000 | 3001 | 3002 |
| API Port | 8000 | 8001 | 8002 |
| Database | dev.db | test_T00001.db | test_T00002.db |
| Browser Debug | 9222 | 9223 | 9224 |

#### Ticket Status

| Ticket | Branch | Worktree | Status |
|--------|--------|----------|--------|
| T00001 Login form | `ticket/T00001` | `.worktrees/T00001` | implementing |
| T00002 Session | `ticket/T00002` | `.worktrees/T00002` | implementing |
| T00003 Logout | - | - | waiting (T00001) |
| T00004 Phase E2E | - | - | waiting (all) |

#### Progress
- [ ] T00001 Login form UI <- active (agent-1)
- [ ] T00002 Session management <- active (agent-2)
- [ ] T00003 Logout flow [blocked: T00001]
- [ ] T00004 Phase 1 E2E Testing
```
