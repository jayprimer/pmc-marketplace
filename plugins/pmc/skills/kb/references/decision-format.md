---
Summary: Decision record format for individual ADR files in 5-decisions/ with status, rationale, and trade-offs.
---

# Decision Format

Architecture Decision Records as individual files in `5-decisions/`.

## Design Principles

### Why Individual Decision Files

1. **Better discoverability** - Glob/grep to find specific decisions by name
2. **Cleaner versioning** - Each decision has its own git history
3. **Easier linking** - Reference specific decision files from tickets, patterns, etc.
4. **No append conflicts** - Parallel work doesn't conflict on a single log file

### When to Create

- Architectural choice (database, framework, API design)
- Design pattern selection
- Breaking change rationale
- Technology adoption/deprecation
- Any decision with trade-offs worth documenting

## Location

`.pmc/docs/5-decisions/D###-{name}.md`

## Naming Convention

- Format: `D` + 3 zero-padded digits + `-{descriptive-name}.md`
- Examples:
  - `D001-use-sqlite.md`
  - `D002-api-versioning-strategy.md`
  - `D003-adopt-pydantic-v2.md`
- Sequential numbering, never reuse numbers
- Use lowercase kebab-case for name portion

## Template

```markdown
---
Summary: {One sentence: what was decided and why}
---

# D###: {Decision Title}

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated | superseded
**Context**: {ticket, discussion, or situation that prompted this}

## Decision

{Clear statement of what was decided}

## Rationale

{Why this choice was made - the reasoning}

## Alternatives Considered

### Option A: {name}
{Description}
- (+) Pros
- (-) Cons
- **Rejected because**: {reason}

### Option B: {name}
{Description}
- (+) Pros
- (-) Cons
- **Rejected because**: {reason}

## Trade-offs

**Benefits:**
- {benefit 1}
- {benefit 2}

**Drawbacks:**
- {drawback 1}
- {drawback 2}

## Consequences

{What changes as a result of this decision}

## Related

- {link to related decision, ticket, or pattern}
```

## Status Values

| Status | Meaning |
|--------|---------|
| `proposed` | Under discussion, not yet approved |
| `accepted` | Approved and in effect |
| `deprecated` | No longer recommended, but may still be in use |
| `superseded` | Replaced by newer decision (link to it) |

### Superseding a Decision

When a decision is replaced:

1. Update old decision's status to `superseded`
2. Add note: `Superseded by: D###-{new-decision}.md`
3. Create new decision with context referencing the old one

## Discovery

```bash
# All decisions
Glob: .pmc/docs/5-decisions/D*.md

# Find by status
Grep: "Status.*accepted" in .pmc/docs/5-decisions/

# Find by topic
Grep: "database" in .pmc/docs/5-decisions/

# Latest decision number
ls .pmc/docs/5-decisions/D*.md | grep -oP 'D\d+' | sort -u | tail -1
```

## Initialization

```bash
mkdir -p .pmc/docs/5-decisions
```

## Example

```markdown
---
Summary: Use SQLite for local storage due to zero-config deployment and sufficient performance.
---

# D001: Use SQLite for Local Storage

**Date**: 2024-06-15
**Status**: accepted
**Context**: T00015 - Need persistent storage for memory feature

## Decision

Use SQLite as the local database for PMC memory and runtime data.

## Rationale

PMC is a CLI tool that runs locally. SQLite provides:
- Zero configuration (no server process)
- Single file database (easy backup/restore)
- Sufficient performance for expected data volumes
- Well-supported Python integration

## Alternatives Considered

### Option A: PostgreSQL
Full-featured relational database.
- (+) More features, better concurrency
- (-) Requires running server process
- (-) Complex setup for end users
- **Rejected because**: Overkill for local CLI tool

### Option B: JSON files
Simple file-based storage.
- (+) Human readable, no dependencies
- (-) No query capabilities
- (-) Poor performance at scale
- **Rejected because**: Need structured queries for memory search

## Trade-offs

**Benefits:**
- Zero deployment friction
- Portable (single file)
- Good Python ecosystem (sqlite3 built-in)

**Drawbacks:**
- Single writer limitation
- Less suitable if we add web server component

## Consequences

- All data stored in `.pmc/data/pmc.db`
- Migrations handled via Alembic
- Backup = copy single file

## Related

- T00015: Memory feature implementation
```
