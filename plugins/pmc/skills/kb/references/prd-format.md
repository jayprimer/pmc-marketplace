---
Summary: PRD template for features (feat-), components (comp-), and infrastructure (infra-) with scope, success criteria, and constraints.
---

# PRD Format

Product Requirements Document template.

## Location

`.pmc/docs/1-prd/{prefix}-{name}.md`

## Template

```markdown
---
Summary: {One sentence: what this feature/component does and its primary purpose}
---

# {Name}

## What

[One paragraph - what is this and why it matters]

## Scope

- [Specific thing to build]
- [Specific thing to build]

## Out of Scope

- [Explicit exclusion]
- [What this will NOT do]

## Acceptance Criteria

- [ ] [Testable condition]
- [ ] [Testable condition]
- [ ] [Testable condition]

## Constraints

- [Technical limitation or dependency]
- [Performance/security requirement]

## Notes

[Optional: related docs, open questions, anything else useful]
```

## Naming Convention

Use prefix to categorize:

| Prefix | Type | Examples |
|--------|------|----------|
| `feat-` | Features (user-facing) | `feat-auth.md`, `feat-search.md` |
| `comp-` | Components (internal) | `comp-api-gateway.md`, `comp-cache.md` |
| `infra-` | Infrastructure | `infra-tech-stack.md`, `infra-test-setup.md` |

**Flexibility:** These prefixes are defaults. Claude can use other prefixes if appropriate (e.g., `admin-`, `tool-`), but must stay consistent with chosen convention throughout the project. When ambiguous, default to `feat-`.

## Discovery

```
Glob: .pmc/docs/1-prd/*.md        # All PRDs
Glob: .pmc/docs/1-prd/feat-*.md   # Features only
Glob: .pmc/docs/1-prd/comp-*.md   # Components only
Glob: .pmc/docs/1-prd/infra-*.md  # Infrastructure only
```
