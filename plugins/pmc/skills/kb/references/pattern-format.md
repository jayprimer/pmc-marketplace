---
Summary: Pattern template for solutions (Status: resolved) and known issues (Status: open) with symptoms, causes, and fixes.
---

# Pattern Format

Solutions for known frequent issues AND tracking of known unresolved issues.

## Design Principles

### Why Patterns Exist

1. **Avoid repeated struggle** - After spending iterations solving a tricky problem, document it. Don't waste time rediscovering the same solution.

2. **Quick lookup** - Problem-focused naming means I search by the issue I'm facing, find the fix fast.

3. **Accumulate knowledge** - Each solved problem becomes reusable. Codebase-specific patterns that no general knowledge covers.

4. **Track known issues** - Open patterns document known limitations awaiting solutions. Single source for "what's broken."

### When to Create

- Spent multiple attempts solving something → document it
- Found a non-obvious solution → document it
- Same issue appeared twice → definitely document it
- Discovered a limitation/bug → document as open pattern

### Pattern vs SOP

These serve different purposes but **boundaries are flexible**:

| Pattern | SOP |
|---------|-----|
| **Coding solutions** | **Operational procedures** |
| Technical fixes, code patterns | How Claude performs tasks |
| "How to fix X problem" | "How to run/deploy/backup Y" |
| Problem-focused | Task-focused |

An SOP may reference a pattern (e.g., "if DNS fails, see pattern `docker-dns-resolution.md`").

**Edge cases**: When a fix involves running commands (e.g., Docker DNS fix), either location works. Don't overthink the distinction—choose one and move on.

## Location

`.pmc/docs/6-patterns/{problem-description}.md`

## Template

### Resolved Pattern

```markdown
---
Summary: {One sentence: the problem and its solution or status}
---

# {Problem Description}

**Status**: resolved
**Severity**: low | medium | high | critical
**Discovered**: YYYY-MM-DD (ticket or context)

{When this happens / symptoms}

## Solution

```code
the fix
```

## Why (optional)

[Brief explanation if not obvious]

## See Also (optional)

- Related pattern or doc
```

### Open Pattern (Known Issue)

```markdown
---
Summary: {One sentence: the problem and its status (open/unresolved)}
---

# {Problem Description}

**Status**: open
**Severity**: low | medium | high | critical
**Discovered**: YYYY-MM-DD (ticket or context)
**Target**: Phase N | ticket T0000N | unplanned

{When this happens / symptoms}

## Workaround

[Temporary mitigation, if any. "None" if no workaround.]

## Root Cause (if known)

[Why this happens, if understood]

## See Also (optional)

- Related pattern or doc
```

### Status Values

| Status | Meaning |
|--------|---------|
| `open` | Known issue, not yet solved |
| `resolved` | Solution documented and verified |

### Severity Levels

| Severity | Impact |
|----------|--------|
| `critical` | Blocks core functionality |
| `high` | Significant impact, workaround difficult |
| `medium` | Annoying but workable |
| `low` | Minor inconvenience |

## Naming Convention

Problem-focused, descriptive:

```
port-conflict.md
docker-network-timeout.md
async-race-condition.md
react-useeffect-cleanup.md
pydantic-validation-error.md
git-merge-conflict-lock.md
sqlite-locked-database.md
npm-peer-dependency.md
```

## Examples

### Resolved Pattern Example

```markdown
# Docker Container DNS Resolution Fails

**Status**: resolved
**Severity**: medium
**Discovered**: 2025-12-15 (T00042)

Container can't resolve hostnames, `ping google.com` fails but `ping 8.8.8.8` works.

## Solution

```bash
# Add DNS to daemon.json
echo '{"dns": ["8.8.8.8", "8.8.4.4"]}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

## Why

Docker inherits host DNS which may point to localhost resolver not accessible from container network namespace.
```

### Open Pattern Example

```markdown
# Windows Shell JSON Quoting Fails

**Status**: open
**Severity**: medium
**Discovered**: 2025-12-28 (T00001)
**Target**: Phase 3

Shell executor fails when JSON contains quotes on Windows. Works on Linux/Mac.

## Workaround

Use file-based input instead of inline JSON for complex payloads.

## Root Cause

Windows cmd.exe and PowerShell have different escaping rules than Unix shells. Current shell executor doesn't normalize quoting across platforms.

## See Also

- T00001 baseline assessment
```

## Discovery

```
# All patterns
Glob: .pmc/docs/6-patterns/*.md

# Search by content
Grep: "docker" in .pmc/docs/6-patterns/
Grep: "timeout" in .pmc/docs/6-patterns/

# Find open issues
Grep: "Status.*open" in .pmc/docs/6-patterns/

# Find by severity
Grep: "Severity.*critical" in .pmc/docs/6-patterns/
```
