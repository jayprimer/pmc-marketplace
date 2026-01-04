---
Summary: Catch-all format for miscellaneous free-form documents in 9-other/.
---

# Other Format

Miscellaneous documents that don't fit elsewhere.

## Design Principles

### Why 9-other Exists

1. **Catch-all** - Not everything fits neatly into categories. This is the escape hatch.

2. **No friction** - When you need to document something quickly, don't waste time categorizing.

3. **Later organization** - Docs can be moved to proper locations later if patterns emerge.

### When to Use

- Temporary notes that don't fit elsewhere
- One-off documentation
- Experimental or exploratory notes
- Anything that would otherwise be lost

### When NOT to Use

If the content clearly fits another category, use that instead:

| Content | Use Instead |
|---------|-------------|
| How to do X | `2-sop/` |
| Problem solution | `6-patterns/` |
| Design decision | `5-decisions/` |
| Code understanding | `7-code-maps/` |
| Research/findings | `8-research/` |

## Location

`.pmc/docs/9-other/{name}.md`

## Format

Free-form. No strict template required.

```markdown
---
Summary: {One sentence: what this document is about}
---

# {Title}

{Content - any format}
```

## Naming Convention

Descriptive, no prefix required:

```
meeting-notes-2024-06.md
scratch-ideas.md
random-thoughts.md
temp-analysis.md
```

## Discovery

```
Glob: .pmc/docs/9-other/*.md
```

## Cleanup

Periodically review 9-other/:
- Move docs to proper categories if they fit
- Delete obsolete docs
- Keep only what's still useful
