---
Summary: Roadmap and archive format for phases, tickets, parallel execution planning, and git worktree workflows.
---

# Plan Format

Project roadmap, progress tracking, and parallel execution planning.

## Design Principles

### Why Roadmap Exists

1. **Bridge PRD to tickets** - PRDs are too large to implement directly. Roadmap breaks features into phases, phases into tickets.

2. **Visibility** - One place to see: what's in progress, what's next, what's blocked.

3. **Phase-level milestones** - Each phase ends with E2E testing to verify the milestone works as a whole.

4. **Session continuity** - I (Claude) can resume work by checking roadmap for current state.

5. **Parallel execution** - Multiple tickets can be worked on concurrently using worktrees.

### PRD → Phase → Ticket Flow

```
PRD (feat-auth)
 │
 ├── Phase 1: Basic Login
 │   ├── T00001 Login form UI
 │   ├── T00002 Session management
 │   ├── T00003 Logout flow
 │   └── T00004 Phase 1 E2E Testing  <- Final ticket of phase
 │
 └── Phase 2: OAuth
     ├── T00005 Google OAuth
     ├── T00006 GitHub OAuth
     └── T00007 Phase 2 E2E Testing  <- Final ticket of phase
```

### Phase E2E Testing

- **What**: Live integration testing of the phase
- **When**: Final ticket of each phase
- **Why**: Verify phase components work together as a whole
- **How**: Create a standard ticket `T0000N Phase X E2E Testing`
- **Scope**: Only new integration tests - do NOT re-run individual ticket tests

Phase E2E is a normal ticket following standard ticket workflow (5 documents, tests.json, etc.).

## Files

```
3-plan/
├── roadmap.md    # Active work (In Progress + Next + Backlog)
└── archive.md    # Completed phases (append-only)
```

## roadmap.md

```markdown
---
Summary: Active project roadmap with phases, tickets, and current work status.
---

# Roadmap

## In Progress

### feat-auth: Phase 1 - Basic Login
- [x] T00001 Login form UI
- [x] T00002 Session management
- [ ] T00003 Logout flow <- current
- [ ] T00004 Phase 1 E2E Testing

## Next

### feat-auth: Phase 2 - OAuth
- T00005 Google OAuth
- T00006 GitHub OAuth
- T00007 Phase 2 E2E Testing

### feat-search: Phase 1 - Basic
- T00008 Search API
- T00009 Search UI
- T00010 Phase 1 E2E Testing

## Backlog

- feat-payments (not planned yet)
- feat-notifications
```

### Tracking Readiness Status

Use markers to indicate ticket planning status:

```markdown
## In Progress

### Phase 1: Feature
- [x] T00001 Login form [+ ready]
- [ ] T00002 Session management [? questions] <- current
- [ ] T00003 Logout flow [x missing]
- [ ] T00004 Phase 1 E2E Testing
```

| Marker | Meaning | Action Required |
|--------|---------|-----------------|
| `[+ ready]` | Plan validated, ready to implement | None |
| `[? questions]` | Has unresolved Open Questions in 3-spec.md | Resolve before implementing |
| `[x missing]` | Missing required sections in plan | Complete 2-plan.md and 3-spec.md |
| *(no marker)* | Not yet planned | Create ticket docs first |

### Validation Before Implementation

Before marking ticket as current:

```bash
python .pmc/marketplace/plugins/pmc/skills/plan-validation/scripts/validate_plan.py T00003
```

- Exit 0 → Add `[+ ready]` marker
- Exit 1 → Add `[? questions]` or `[x missing]` based on issues
- Fix issues before proceeding

---

## Parallel Execution Planning

### When to Use Parallel Execution

| Scenario | Use Parallel | Reason |
|----------|--------------|--------|
| Independent tickets (no shared files) | **Yes** | No merge conflicts |
| Tickets modify different modules | **Yes** | Minimal conflicts |
| Tickets share some files but different sections | **Maybe** | Careful merge needed |
| Tickets heavily modify same files | **No** | Sequential is safer |
| Phase E2E ticket | **No** | Must run after all tickets complete |

### Parallel Execution Markers

```markdown
## In Progress

### feat-auth: Phase 1 - Basic Login

**Parallel Execution: 2 concurrent**

| Ticket | Worktree | Assignee | Status |
|--------|----------|----------|--------|
| T00001 | `.worktrees/T00001` | agent-1 | implementing |
| T00002 | `.worktrees/T00002` | agent-2 | implementing |
| T00003 | - | - | waiting |
| T00004 | - | - | Phase E2E (last) |

**Dependencies:**
- T00003 depends on T00001 (uses login form)
- T00004 depends on all (E2E testing)
```

### Dependency Analysis

Before parallel execution, analyze dependencies:

```markdown
## Dependency Matrix

| Ticket | Depends On | Blocks | Can Parallel With |
|--------|------------|--------|-------------------|
| T00001 | - | T00003 | T00002 |
| T00002 | - | - | T00001 |
| T00003 | T00001 | T00004 | - |
| T00004 | T00001, T00002, T00003 | - | - (E2E) |
```

### File Conflict Analysis

Check for potential merge conflicts:

```markdown
## File Ownership

| File | T00001 | T00002 | T00003 | Conflict Risk |
|------|--------|--------|--------|---------------|
| src/auth/login.py | ✓ | - | ✓ | MEDIUM |
| src/auth/session.py | - | ✓ | - | NONE |
| src/auth/logout.py | - | - | ✓ | NONE |
| tests/test_auth.py | ✓ | ✓ | ✓ | HIGH |
```

**Conflict Risk Levels:**
- **NONE**: Different files, safe for parallel
- **LOW**: Same file, different sections
- **MEDIUM**: Same file, may touch same areas
- **HIGH**: Same file, likely conflicts - consider sequential

### Resource Allocation

When running parallel worktrees, each needs isolated resources to avoid conflicts.

#### Resource Allocation Table

```markdown
#### Resource Allocation

| Resource | Main | T00001 | T00002 | T00003 |
|----------|------|--------|--------|--------|
| Web Server Port | 3000 | 3001 | 3002 | 3003 |
| API Port | 8000 | 8001 | 8002 | 8003 |
| Database | dev.db | test_T00001.db | test_T00002.db | test_T00003.db |
| Redis Port | 6379 | 6380 | 6381 | 6382 |
| Temp Directory | /tmp/app | /tmp/app-T00001 | /tmp/app-T00002 | /tmp/app-T00003 |
| Log Directory | logs/ | logs-T00001/ | logs-T00002/ | logs-T00003/ |
```

#### Common Resources to Allocate

| Resource Type | Examples | Allocation Strategy |
|---------------|----------|---------------------|
| **Network Ports** | Web server, API, WebSocket, debug | Unique port per worktree |
| **Databases** | SQLite files, Postgres schemas | Separate file/schema per worktree |
| **Cache** | Redis, Memcached | Separate port or key prefix |
| **File Paths** | Temp dirs, logs, uploads | Ticket-suffixed directories |
| **Environment** | `.env` files | Per-worktree `.env.local` |
| **Browser Ports** | Chrome DevTools, Playwright | Unique debug ports |
| **Process IDs** | Lock files, PID files | Ticket-suffixed filenames |

#### Environment Setup Per Worktree

Each worktree should have its own `.env.local` (gitignored):

```bash
# .worktrees/T00001/.env.local
PORT=3001
API_PORT=8001
DATABASE_URL=sqlite:///test_T00001.db
REDIS_PORT=6380
TEMP_DIR=/tmp/app-T00001
LOG_DIR=./logs-T00001
BROWSER_DEBUG_PORT=9222
```

#### Database Isolation Strategies

| Database | Isolation Method |
|----------|------------------|
| SQLite | Separate file: `test_T00001.db` |
| PostgreSQL | Separate schema: `ticket_t00001` |
| MySQL | Separate database: `app_t00001` |
| MongoDB | Separate database: `app_t00001` |

#### Cleanup After Ticket Complete

When removing worktree, also clean up resources:

```bash
# Remove worktree
git worktree remove .worktrees/T00001

# Clean up allocated resources
rm -f test_T00001.db           # SQLite
rm -rf /tmp/app-T00001         # Temp files
rm -rf logs-T00001/            # Logs
# Drop schema/database if using Postgres/MySQL
```

---

## Git Worktree Workflow

### Directory Layout

```
project/                     # Main worktree (main branch)
├── .pmc/
│   ├── docs/                # Git tracked (KB docs)
│   └── data/                # Gitignored (runtime artifacts)
├── .worktrees/              # Gitignored (feature worktrees)
│   ├── T00001/              # Ticket worktree
│   ├── T00002/              # Ticket worktree
│   └── phase-1/             # Phase E2E worktree
└── src/, tests/, ...
```

### Branch Strategy

```
main
 └── phase/N                 # Phase branch (all phase work)
      ├── ticket/T00001      # Individual ticket branch
      ├── ticket/T00002      # Individual ticket branch
      └── ticket/T00003      # Individual ticket branch
```

| Type | Branch Pattern | Base Branch | Worktree Location |
|------|----------------|-------------|-------------------|
| Phase | `phase/N` | `main` | `.worktrees/phase-N/` |
| Ticket | `ticket/T0000N` | `phase/N` | `.worktrees/T0000N/` |

---

## Parallel Execution Setup

### Step 1: Create Phase Branch

```bash
# From main worktree
git checkout main
git pull origin main
git checkout -b phase/1
git push -u origin phase/1
```

### Step 2: Create Ticket Worktrees (Parallel)

For each ticket that can run in parallel:

```bash
# Create worktree for T00001
git worktree add .worktrees/T00001 -b ticket/T00001 phase/1

# Create worktree for T00002 (parallel)
git worktree add .worktrees/T00002 -b ticket/T00002 phase/1
```

### Step 3: Verify Worktree Setup

```bash
# List all worktrees
git worktree list

# Expected output:
# /path/to/project          abc1234 [main]
# /path/to/project/.worktrees/T00001  def5678 [ticket/T00001]
# /path/to/project/.worktrees/T00002  ghi9012 [ticket/T00002]
```

### Step 4: Work in Worktrees

Each agent/session works in its assigned worktree:

```bash
cd .worktrees/T00001
# ... implement ticket ...
git add .
git commit -m "T00001: implement feature"
git push -u origin ticket/T00001
```

---

## Merging Workflow

### Merge Order Strategy

```
                    ┌─────────────┐
                    │   phase/1   │
                    └─────────────┘
                          ▲
          ┌───────────────┼───────────────┐
          │               │               │
     ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
     │ T00001  │    │ T00002  │    │ T00003  │
     └─────────┘    └─────────┘    └─────────┘
     (merge 1st)    (merge 2nd)   (merge 3rd)
```

**Merge order considerations:**
1. Tickets with no dependencies first
2. Tickets that others depend on before dependents
3. Tickets that modify shared files - coordinate timing
4. Phase E2E always last

### Step 1: Sync Phase Branch

Before merging, ensure phase branch is current:

```bash
git checkout phase/1
git pull origin phase/1
```

### Step 2: Merge Ticket to Phase

```bash
# Merge T00001 (no dependencies)
git checkout phase/1
git merge ticket/T00001 --no-ff -m "Merge T00001: Login form UI"
git push origin phase/1
```

### Step 3: Update Dependent Worktrees

After merging, update other ticket branches to avoid conflicts:

```bash
# In T00002 worktree (if still open)
cd .worktrees/T00002
git fetch origin
git merge origin/phase/1 -m "Sync with phase/1 after T00001 merge"
```

### Step 4: Handle Merge Conflicts

If conflicts occur:

```bash
# In the ticket worktree
git merge origin/phase/1

# If conflicts:
# 1. Resolve in each file
# 2. git add <resolved-files>
# 3. git commit -m "Resolve conflicts with phase/1"
# 4. Test to ensure nothing broke
```

### Step 5: Complete All Merges

After all tickets merged to phase:

```bash
# Merge phase to main
git checkout main
git pull origin main
git merge phase/1 --no-ff -m "Merge Phase 1: Basic Login"
git push origin main
```

---

## Worktree Cleanup

### After Ticket Complete

```bash
# Remove worktree
git worktree remove .worktrees/T00001

# Delete local branch (already merged)
git branch -d ticket/T00001

# Delete remote branch (optional, for cleanup)
git push origin --delete ticket/T00001
```

### After Phase Complete

```bash
# Remove phase worktree (if used)
git worktree remove .worktrees/phase-1

# Delete phase branch (already merged)
git branch -d phase/1
git push origin --delete phase/1

# Verify no stale worktrees
git worktree prune
git worktree list
```

### Cleanup Checklist

- [ ] All ticket worktrees removed
- [ ] All ticket branches merged and deleted (local)
- [ ] All ticket branches deleted (remote)
- [ ] Phase worktree removed (if used)
- [ ] Phase branch merged and deleted
- [ ] `git worktree prune` run
- [ ] No stale entries in `git worktree list`
- [ ] Allocated resources cleaned up:
  - [ ] Test databases removed
  - [ ] Temp directories removed
  - [ ] Log directories removed (or archived)
  - [ ] Cache entries cleared (if using key prefixes)

---

## Parallel Execution Roadmap Format

### Full Example

```markdown
---
Summary: Active project roadmap with parallel execution planning.
---

# Roadmap

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
| Redis Port | 6379 | 6380 | 6381 |
| Browser Debug | 9222 | 9223 | 9224 |

#### Ticket Status

| Ticket | Branch | Worktree | Assignee | Status |
|--------|--------|----------|----------|--------|
| T00001 Login form | `ticket/T00001` | `.worktrees/T00001` | agent-1 | merged |
| T00002 Session | `ticket/T00002` | `.worktrees/T00002` | agent-2 | implementing |
| T00003 Logout | - | - | - | waiting (T00001) |
| T00004 Phase E2E | - | - | - | waiting (all) |

#### Progress
- [x] T00001 Login form UI [merged]
- [ ] T00002 Session management <- active
- [ ] T00003 Logout flow [blocked: T00001]
- [ ] T00004 Phase 1 E2E Testing

## Next

### feat-search: Phase 1 - Basic

**Execution Mode:** Sequential (tickets share many files)

- T00005 Search API
- T00006 Search UI
- T00007 Phase 1 E2E Testing

## Backlog

- feat-payments (not planned yet)
```

---

## archive.md

```markdown
---
Summary: Completed phases and tickets archived by date with E2E pass status.
---

# Completed

## 2024-01

### feat-auth: Phase 1 - Basic Login
T00001-T00004, Phase E2E passed
Execution: Parallel (T00001, T00002 concurrent)

## 2024-02

### feat-search: Phase 1 - Basic
T00008-T00010, Phase E2E passed
Execution: Sequential
```

---

## Conventions

| Element | Format |
|---------|--------|
| Feature | `feat-{name}` (matches PRD prefix) |
| Phase header | `### feat-name: Phase N - Description` |
| Current ticket | `<- current` or `<- active` marker |
| Phase E2E ticket | `T0000N Phase N E2E Testing` (always last) |
| Completed | `T00001-T00004, Phase E2E passed` |
| Parallel marker | `**Execution Mode:** Parallel (N concurrent)` |
| Sequential marker | `**Execution Mode:** Sequential` |

---

## Workflow Summary

### Sequential Workflow (Default)

```
1. Create phase branch from main
2. Create ticket, implement, merge to phase
3. Repeat for each ticket
4. Phase E2E ticket last
5. Merge phase to main
6. Archive and cleanup
```

### Parallel Workflow

```
1. Create phase branch from main
2. Analyze dependencies and file conflicts
3. Allocate resources (ports, DBs, temp dirs)
4. Create worktrees for parallel tickets
5. Setup per-worktree .env.local
6. Work concurrently in worktrees
7. Merge in dependency order, sync other branches
8. Sequential tickets after dependencies resolved
9. Phase E2E ticket last
10. Merge phase to main
11. Cleanup worktrees, branches, and allocated resources
12. Archive
```

### Starting a new feature
1. Create PRD in `1-prd/feat-{name}.md`
2. Break into phases in `3-plan/roadmap.md` under "Next" or "Backlog"
3. List tickets for each phase
4. Analyze dependencies for parallel execution potential

### Starting a phase
1. Move phase from "Next" to "In Progress"
2. Create phase branch: `git checkout -b phase/N`
3. Determine execution mode (parallel/sequential)
4. If parallel: allocate resources (ports, DBs) per ticket
5. Create worktrees for parallel tickets
6. Setup per-worktree .env.local with allocated resources
7. Create ticket docs, add to index and roadmap

### During implementation
1. Work in assigned worktrees
2. Commit and push regularly
3. Sync with phase branch after each merge
4. Update roadmap status

### Completing tickets
1. Merge to phase branch in dependency order
2. Update roadmap: mark `[merged]`
3. Remove worktree and delete branch
4. Update dependent ticket worktrees

### Phase E2E ticket
1. All other tickets merged
2. Create worktree for E2E work (optional)
3. Run integration tests
4. Pass all tests → phase complete

### Completing a phase
1. Merge phase to main
2. Remove all worktrees
3. Delete phase and ticket branches
4. Run `git worktree prune`
5. Clean up allocated resources (DBs, temp dirs, logs)
6. Append to `archive.md` under current month
7. Move next phase to "In Progress"
