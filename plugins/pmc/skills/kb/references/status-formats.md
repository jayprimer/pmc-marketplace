---
Summary: Status document formats for features.md, health.md, and audits/ in 4-status/.
---

# Status Formats

Living project status documents in `4-status/`.

## Design Principles

### Why Status Docs Exist

1. **Quick health check** - Answer "what works?" without reading all ticket finals
2. **Project pulse** - Test counts, open issues, tech debt at a glance
3. **Audit trail** - KB consistency checks and validation history

### When to Update

| Document | Update when... |
|----------|----------------|
| `features.md` | Feature status changes (new, fixed, broken) |
| `health.md` | After each phase completion, or when manually requested |
| `audits/` | After running `/pmc:update-kb` or manual KB audit |

## Location

`.pmc/docs/4-status/`

## Files

### features.md

Component and feature status matrix.

```markdown
---
Summary: Component and feature status matrix with platform support and known issues.
---

# Feature Status

Last updated: YYYY-MM-DD

## Component Matrix

| Component | Status | Windows | Linux | Mac | Notes |
|-----------|--------|---------|-------|-----|-------|
| CLI | stable | yes | yes | yes | |
| Dashboard | stable | yes | yes | yes | |
| Workflow Engine | stable | partial | yes | yes | JSON quoting issues |
| Memory | stable | yes | yes | yes | |

## Status Legend

- **stable**: Production-ready
- **beta**: Works but may have issues
- **alpha**: Experimental
- **broken**: Known non-functional
- **partial**: Works with limitations (see Notes)

## Feature Checklist

### CLI Commands
- [x] `pmc run` - Execute workflows
- [x] `pmc status` - Check execution status
- [x] `pmc list` - List workflows
- [ ] `pmc export` - Export results (planned)

### Dashboard Pages
- [x] Workflows list
- [x] Workflow editor
- [x] Execution monitor
- [x] Chat interface
- [ ] Settings page (planned)

## Open Patterns (Known Issues)

See `6-patterns/` for details:
- windows-shell-json-quoting.md (Status: open)
```

### health.md

Project health metrics snapshot.

```markdown
---
Summary: Project health metrics including test coverage, open patterns, and technical debt.
---

# Project Health

Last updated: YYYY-MM-DD (after Phase N)

## Test Coverage

| Category | Count | Passing | Failing | Skipped |
|----------|-------|---------|---------|---------|
| Smoke | 12 | 12 | 0 | 0 |
| Unit | 180 | 175 | 3 | 2 |
| Integration | 45 | 44 | 1 | 0 |
| E2E | 59 | 57 | 0 | 2 |
| **Total** | **296** | **288** | **4** | **4** |

## Open Patterns

| Severity | Count | Examples |
|----------|-------|----------|
| Critical | 0 | |
| High | 1 | dashboard-memory-leak.md |
| Medium | 3 | windows-shell-json-quoting.md, ... |
| Low | 2 | ... |

## Technical Debt

| Area | Description | Effort | Priority |
|------|-------------|--------|----------|
| Tests | Windows shell tests skipped | medium | Phase 3 |
| Docs | API reference incomplete | low | backlog |

## Performance Baselines

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Smoke tests | 4.2s | <5s | ok |
| Full suite | 58s | <120s | ok |
| Dashboard load | 1.1s | <2s | ok |

## Trends

- Phase 1→2: +45 tests, -2 open patterns
- Test pass rate: 97.3%
```

### audits/

KB consistency audit reports from `/pmc:update-kb`.

```markdown
---
Summary: KB audit from YYYY-MM-DD covering structure, formats, and consistency.
---

# KB Audit: YYYY-MM-DD

## Summary

- **Status**: passed | failed | warnings
- **Documents checked**: N
- **Issues found**: N

## Structure Check

| Directory | Expected | Found | Status |
|-----------|----------|-------|--------|
| 0-inbox | exists | yes | ✓ |
| tickets/index.md | exists | yes | ✓ |
| 3-plan/roadmap.md | exists | yes | ✓ |

## Format Validation

| Document | Format | Status |
|----------|--------|--------|
| tickets/T00001/4-progress.md | frontmatter | ✓ |
| 6-patterns/example.md | Status field | ✓ |

## Issues

### Critical
- (none)

### Warnings
- 8-research/old-notes.md: missing Summary frontmatter

## Recommendations

- Add Summary frontmatter to legacy documents
```

**Naming**: `{YYYY-MM-DD}-audit.md` (e.g., `2024-06-15-audit.md`)

## Discovery

```
# All status docs
Glob: .pmc/docs/4-status/*.md
Glob: .pmc/docs/4-status/audits/*.md

# Check feature status
Read: .pmc/docs/4-status/features.md

# Latest audit
Glob: .pmc/docs/4-status/audits/*.md | sort | tail -1
```

## Initialization

```bash
mkdir -p .pmc/docs/4-status/audits
touch .pmc/docs/4-status/{features.md,health.md}
```
