---
Summary: Research template for notes, external documentation, and findings in 8-research/.
---

# Research Format

Archive of useful information - research, notes, external docs.

## Design Principles

### Why Research Docs Exist

1. **Catch-all for knowledge** - Research, API docs, benchmarks - anything useful that doesn't fit elsewhere.

2. **Preserve context** - What was learned? What were the findings? Research docs keep the knowledge.

3. **Reduce re-research** - Already looked up API rate limits? Document it. Don't research again next session.

### When to Create

- Researched something useful → document it
- Found external documentation → summarize key parts
- Anything worth remembering that doesn't fit other categories

**Note:** Design decisions now go to `5-decisions/` as individual ADR files.

## Location

`.pmc/docs/8-research/{topic}.md`

## Format

No strict template. Just useful content with a clear title.

```markdown
---
Summary: {One sentence: what this research covers and why it's useful}
---

# {Topic}

{Content - whatever format makes sense}
```

## Naming Convention

Descriptive topic name:

```
api-rate-limits.md
auth-flow-research.md
database-schema.md
third-party-libs.md
deployment-notes.md
performance-benchmarks.md
competitor-analysis.md
```

## Discovery

```
Glob: .pmc/docs/8-research/*.md
Grep: "rate limit" in .pmc/docs/8-research/
```

## What Goes Here

- Research notes
- External API documentation
- Benchmarks and measurements
- Technology comparisons
- Anything useful that doesn't fit elsewhere

## What Goes Elsewhere

| Content | Location |
|---------|----------|
| Design decisions | `5-decisions/D###-{name}.md` |
| Problem solutions | `6-patterns/{problem}.md` |
| Code navigation | `7-code-maps/{feature}.md` |
| Procedures | `2-sop/{verb}-{noun}.md` |
