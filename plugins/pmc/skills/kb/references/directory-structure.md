---
Summary: Complete .pmc/docs/ directory structure with inbox, PRDs, SOPs, plans, status, decisions, patterns, code-maps, research, and tickets.
---

# Directory Structure Reference

Complete docs directory structure.

## Full Structure

```
.pmc/docs/
├── 0-inbox/                     # Task queue from any source (user, GitHub, Slack, etc.)
│   └── {any}.md                 # Free-form format
│
├── 1-prd/
│   ├── feat-{name}.md          # Features (user-facing)
│   ├── comp-{name}.md          # Components (internal)
│   └── infra-{name}.md         # Infrastructure
│
├── 2-sop/
│   └── {verb}-{noun}.md        # e.g., start-server.md, backup-db.md
│
├── 3-plan/
│   ├── roadmap.md              # In Progress + Next + Backlog
│   └── archive.md              # Completed phases
│
├── 4-status/
│   ├── features.md             # Component/feature status matrix
│   ├── health.md               # Test counts, open patterns, debt
│   └── audits/                 # KB audit reports from update-kb
│       └── {date}-audit.md
│
├── 5-decisions/
│   └── D001-{name}.md          # Individual decision records (ADR format)
│
├── 6-patterns/
│   └── {problem}.md            # Solutions AND open issues (Status: resolved|open)
│
├── 7-code-maps/
│   └── {feature}.md            # e.g., user-auth.md, search-api.md
│
├── 8-research/
│   └── {topic}.md              # Research, notes, external documentation
│
├── 9-other/
│   └── {any}.md                # Miscellaneous free-form docs
│
├── tests/
│   ├── smoke/{app}/
│   │   ├── tests.json          # Test definitions
│   │   └── {scripts}           # Custom scripts alongside tests.json
│   ├── core/{feature}/
│   │   ├── tests.json
│   │   └── {scripts}
│   └── tickets/T0000N/
│       ├── tests.json
│       ├── {scripts}
│       └── screenshots/        # Visual test captures
│
└── tickets/
    ├── index.md                # Lookup table: number ↔ title
    ├── T0000N/
    │   ├── 1-definition.md     # What to build, add to index
    │   ├── 2-plan.md           # How to build
    │   ├── 3-spec.md           # Technical details
    │   ├── 4-progress.md       # Progress notes + test development
    │   └── 5-final.md          # Completion (BLOCKED | COMPLETE)
    └── archive/
```

## 0-inbox/ (Task Queue)

Free-form task queue from any source:
- Direct user messages
- GitHub issues/PRs (create ticket, track issue # in 4-progress.md)
- Slack messages
- External integrations

**Processing:** `/pmc:dev` and `/pmc:plan` check inbox after completing their primary directive. Items are removed once properly planned (PRD/roadmap/tickets).

**GitHub Issues:** Delivered to inbox → processed into ticket → track GitHub issue # in ticket's 4-progress.md frontmatter.

```bash
# List inbox items
Glob: .pmc/docs/0-inbox/*.md
```

## Discovery

No index files needed for most directories. Use:

```bash
# Inbox items
Glob: .pmc/docs/0-inbox/*.md

# PRDs by type
Glob: .pmc/docs/1-prd/feat-*.md   # Features
Glob: .pmc/docs/1-prd/comp-*.md   # Components
Glob: .pmc/docs/1-prd/infra-*.md  # Infrastructure

# Status docs
Read: .pmc/docs/4-status/features.md   # Feature matrix
Read: .pmc/docs/4-status/health.md     # Project health
Glob: .pmc/docs/4-status/audits/*.md   # Audit reports

# Decisions
Glob: .pmc/docs/5-decisions/D*.md      # All decisions
Grep: "Status.*accepted" in .pmc/docs/5-decisions/

# Patterns (solutions and known issues)
Glob: .pmc/docs/6-patterns/*.md
Grep: "Status.*open" in .pmc/docs/6-patterns/   # Find open issues
Grep: "Severity.*critical" in .pmc/docs/6-patterns/

# Code maps
Glob: .pmc/docs/7-code-maps/*.md

# Research
Glob: .pmc/docs/8-research/*.md

# Other
Glob: .pmc/docs/9-other/*.md

# Search content
Grep: "retry" in .pmc/docs/
```

## Only One Index

Index exists only for tickets/ directory as a **lookup table** - quickly find ticket number by title (or vice versa) without opening each directory.

### tickets/index.md

```
T00001 Brief Name
T00002 Brief Name
```

One line per ACTIVE ticket. Remove when archiving. Numbering comes from scanning directories (active + archive), not from this file.

## Plan Files

### 3-plan/roadmap.md

```markdown
# Roadmap

## In Progress

### feat-name: Phase N - Description
- [x] T00001 Done ticket
- [ ] T00002 Current ticket <- current
- [ ] T00003 Upcoming ticket
- [ ] Phase E2E

## Next

### feat-name: Phase N+1 - Description
- T00004, T00005
- Phase E2E

## Backlog

- feat-other (not planned yet)
```

### 3-plan/archive.md

```markdown
# Completed

## 2024-01

### feat-name: Phase 1 - Description
T00001-T00003, Phase E2E passed
```

## Initialization

> **Note:** Commands below are reference/illustrative (Linux syntax). Create environment-specific SOPs for actual usage.

```bash
# Create structure
mkdir -p .pmc/docs/{0-inbox,1-prd,2-sop,3-plan}
mkdir -p .pmc/docs/4-status/audits
mkdir -p .pmc/docs/{5-decisions,6-patterns,7-code-maps,8-research,9-other}
mkdir -p .pmc/docs/tests/{smoke,core,tickets}
mkdir -p .pmc/docs/tickets/archive

# Create required files
touch .pmc/docs/3-plan/{roadmap.md,archive.md}
touch .pmc/docs/4-status/{features.md,health.md}
touch .pmc/docs/tickets/index.md
```

## Numbering

### Tickets (T#####)

- Format: `T` + 5 zero-padded digits
- Check both `.pmc/docs/tickets/` and `.pmc/docs/tickets/archive/`
- Find highest, add 1

### Decisions (D###)

- Format: `D` + 3 zero-padded digits + `-{name}.md`
- Example: `D001-use-sqlite.md`, `D002-api-versioning.md`
- Sequential numbering, never reuse

### Finding Next Number

> **Note:** Commands below are reference/illustrative (Linux syntax). Create environment-specific SOPs for actual usage.

```bash
# Next ticket
ls -d .pmc/docs/tickets/T* .pmc/docs/tickets/archive/T* 2>/dev/null | grep -oP 'T\d+' | sort -u | tail -1

# Next decision
ls .pmc/docs/5-decisions/D*.md 2>/dev/null | grep -oP 'D\d+' | sort -u | tail -1
```
