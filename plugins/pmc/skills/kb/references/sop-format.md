---
Summary: SOP template for repeatable procedures with prerequisites, steps, verification, and troubleshooting.
---

# SOP Format

Standard Operating Procedure - how to do things.

## Design Principles

### Why SOPs Exist

1. **Repeatability** - Commands I run often (start server, backup db, deploy) should be documented, not remembered.

2. **Reduce errors** - Exact commands with flags, in order. No guessing or forgetting steps.

3. **Session continuity** - Environment setup, port numbers, paths - things I forget between sessions.

4. **Scalable complexity** - Simple SOPs are just commands. Complex ones add steps, troubleshooting, rollback.

### When to Create

- Running the same command sequence twice → document it
- Non-obvious flags or parameters → document it
- Multi-step process with order dependency → document it

## Location

`.pmc/docs/2-sop/{verb}-{noun}.md`

## Template

```markdown
---
Summary: {One sentence: what this procedure does and when to use it}
---

# {Name}

{One line - when/why to use this}

## Commands

```bash
# Start dev server
npm run dev

# Stop
Ctrl+C
```

## Steps (if multi-step)

1. First do X
   ```bash
   command
   ```
2. Then Y → expect: "success message"
3. Verify: `check command`

## Troubleshooting (if common issues)

**Port in use**: `lsof -i :3000 | xargs kill`
**DB connection failed**: Check docker with `docker ps`

## Rollback (if destructive)

```bash
undo command
```
```

## Section Guide

| Complexity | Sections |
|------------|----------|
| Simple | Commands only |
| Medium | Commands + Steps |
| Complex | All sections |

Only include sections you need.

## Naming Convention

Use verb-noun format:

```
start-server.md
stop-server.md
backup-db.md
restore-db.md
access-docker-db.md
deploy-staging.md
deploy-prod.md
reset-cache.md
```

## Discovery

```
Glob: .pmc/docs/2-sop/*.md           # All SOPs
Grep: "docker" in .pmc/docs/2-sop/   # Search by keyword
```
