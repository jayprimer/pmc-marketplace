---
name: memory
description: |
  PMC memory system for persistent context across sessions. Store, search,
  and retrieve project knowledge using semantic vector search (OpenAI embeddings)
  and full-text keyword search.

  Use when: storing important context, searching for past solutions,
  retrieving project-specific knowledge, or building up institutional memory.
---

# PMC Memory System

Persistent memory for cross-session knowledge using SQLite + OpenAI embeddings.

## Quick Start

```bash
# Check memory status
pmc memory stats

# Add a memory
pmc memory add "content here" -c category

# Search memories (hybrid = vector + keyword)
pmc memory search "query"

# List recent memories
pmc memory list -n 10

# Get specific memory by ID (8+ char prefix works)
pmc memory get abc12345

# View search analytics
pmc memory search-stats
pmc memory search-logs
```

## Prerequisites

**OpenAI API Key required** for semantic search:

```bash
# In .env file
OPENAI_API_KEY=sk-...
```

Without the API key, falls back to hash-based embeddings (not semantic).

## Commands

### Add Memory

```bash
pmc memory add <content> [options]

Options:
  -c, --category TEXT      Category tag (can use multiple times)
  -t, --timestamp TEXT     Set created/updated time (YYYY-MM-DD, ISO, "today", "yesterday")
  --embed/--no-embed       Generate embedding (default: --embed)
```

**Examples:**
```bash
# Add with category
pmc memory add "API uses JWT tokens for auth" -c ctx

# Add user preference
pmc memory add "User prefers functional style over classes" -c pref

# Add a solution
pmc memory add "Fix: clear cache after deploy" -c fix

# Add with specific timestamp
pmc memory add "Migrated to Python 3.12" -c ctx -t 2024-06-15

# Add without embedding (faster, keyword-only search)
pmc memory add "Quick note" -c note --no-embed
```

### Get Memory

```bash
pmc memory get <id>
```

Retrieve a single memory by ID. Supports **partial ID matching** (8+ characters).

**Examples:**
```bash
# Full UUID
pmc memory get 550e8400-e29b-41d4-a716-446655440000

# Partial ID (8+ chars)
pmc memory get 550e8400
```

### Update Memory

```bash
pmc memory update <id> [options]

Options:
  --content TEXT           New content
  -c, --category TEXT      New categories (replaces existing)
  -t, --timestamp TEXT     Update timestamp
  --embed/--no-embed       Regenerate embedding
```

Supports partial ID matching (8+ characters).

**Examples:**
```bash
# Update content
pmc memory update 550e8400 --content "Updated: API uses OAuth2"

# Change category
pmc memory update 550e8400 -c pref

# Update timestamp
pmc memory update 550e8400 -t today
```

### Search Memories

```bash
pmc memory search <query> [options]

Options:
  -m, --mode TEXT          Search mode: hybrid, vector, keyword (default: hybrid)
  -n, --limit INT          Max results (default: 10)
  -c, --category TEXT      Filter by category
  --before TEXT            Filter: created before date
  --after TEXT             Filter: created after date
  --between TEXT TEXT      Filter: created between dates
```

**Search Modes:**

| Mode | Description | When to Use |
|------|-------------|-------------|
| `hybrid` | Vector + keyword with RRF fusion | Default, best overall |
| `vector` | Semantic similarity only | Find conceptually related |
| `keyword` | Full-text search (FTS5) | Exact term matching |

**Examples:**
```bash
# Hybrid search (default)
pmc memory search "authentication flow"

# Semantic search only
pmc memory search "how to handle errors" -m vector

# Keyword search only
pmc memory search "JWT token" -m keyword

# Filter by category
pmc memory search "config" -c ctx

# Filter by date range
pmc memory search "migration" --after 2024-01-01
pmc memory search "fix" --between 2024-01-01 2024-06-30

# Combined filters
pmc memory search "database" -c fix --after 2024-06-01 -n 5
```

### List Memories

```bash
pmc memory list [options]

Options:
  -n, --limit INT          Max results (default: 10)
  --offset INT             Skip first N results
  -c, --category TEXT      Filter by category
```

Lists memories ordered by updated_at (most recent first).

**Examples:**
```bash
# List recent memories
pmc memory list

# Filter by category
pmc memory list -c fix

# Paginate
pmc memory list -n 10 --offset 10
```

### Delete Memory

```bash
pmc memory delete [id] [options]

Options:
  -f, --force              Skip confirmation
  -c, --category TEXT      Delete all in category (bulk)
  --before TEXT            Delete all before date (bulk)
  --after TEXT             Delete all after date (bulk)
  --between TEXT TEXT      Delete all between dates (bulk)
```

Supports partial ID matching (8+ characters) for single delete.

**Examples:**
```bash
# Delete single by ID (with confirmation)
pmc memory delete 550e8400

# Delete single, skip confirmation
pmc memory delete 550e8400 -f

# Bulk delete by category
pmc memory delete -c note -f

# Bulk delete by date
pmc memory delete --before 2024-01-01 -f

# Bulk delete by date range
pmc memory delete --between 2024-01-01 2024-06-30 -f

# Combine filters
pmc memory delete -c note --before 2024-01-01 -f
```

### Categories

```bash
pmc memory categories
```

List all categories with memory counts.

**Output:**
```
ctx    15
fix     8
pref    5
note    3
```

### Reset (Clear All)

```bash
pmc memory reset [options]

Options:
  -f, --force    Skip confirmation
```

**Warning:** This deletes ALL memories permanently.

### Export

```bash
pmc memory export [output_file] [options]

Options:
  --all                    Export all memories (default if no filters)
  -q, --query TEXT         Filter by search query
  -c, --category TEXT      Filter by category
  --before TEXT            Filter: created before date
  --after TEXT             Filter: created after date
  --between TEXT TEXT      Filter: created between dates
```

Exports to JSON format. Default file: `memories_export.json`

**Examples:**
```bash
# Export all
pmc memory export backup.json --all

# Export by category
pmc memory export fixes.json -c fix

# Export by date range
pmc memory export q1.json --between 2024-01-01 2024-03-31

# Export search results
pmc memory export auth.json -q "authentication"

# Combined filters
pmc memory export ctx_2024.json -c ctx --after 2024-01-01
```

### Import

```bash
pmc memory import <input_file> [options]

Options:
  --skip-duplicates    Skip memories with same content (default: error)
  --update-existing    Update if content matches (default: error)
```

Imports from JSON format.

**Examples:**
```bash
# Import, error on duplicates
pmc memory import backup.json

# Skip duplicates silently
pmc memory import backup.json --skip-duplicates

# Update existing memories if content matches
pmc memory import backup.json --update-existing
```

### Statistics

```bash
pmc memory stats
```

Shows:
- Total memory count
- Category breakdown
- Database size
- Embedding model (OpenAI text-embedding-3-small or fallback)

### Search Analytics

Track and analyze search queries for usage patterns.

#### View Search Logs

```bash
pmc memory search-logs [options]

Options:
  -n, --limit INT     Max logs to display (default: 20)
  --offset INT        Skip first N logs
```

Shows recent search queries with:
- Timestamp
- Query text
- Search mode (hybrid/vector/keyword)
- Result count
- Category filters used
- Date filters used

**Example output:**
```
2024-06-15 14:30:22 authentication flow
  mode=hybrid limit=10 results=5 cats=ctx

2024-06-15 14:25:10 database connection
  mode=keyword limit=10 results=3 cats=-
```

#### Search Statistics

```bash
pmc memory search-stats
```

Shows aggregate analytics:
- Total searches performed
- Average results per search
- Searches by mode (hybrid/vector/keyword)
- Top 10 most frequent queries

**Example output:**
```
Search Statistics
----------------------------------------
Total searches: 47
Avg results: 3.2

By Mode:
  hybrid: 35
  keyword: 10
  vector: 2

Top Queries:
  5x authentication
  4x database config
  3x error handling
```

## Categories

Use these **exact** category tags (minimal set, easy to remember):

| Tag | Use For | Example |
|-----|---------|---------|
| `ctx` | Project-specific facts | "Uses port 3000", "DB is Postgres 15" |
| `pref` | User preferences | "Prefers tabs", "No emojis in code" |
| `fix` | Solutions found | "Fix: restart Redis after config change" |
| `note` | Temporary/misc | Anything else |
| `user` | Auto-captured user prompts | Recorded by UserPromptSubmit hook for recall |

**Why minimal?**
- 5 tags are easy to remember
- Search finds content anyway (categories are for filtering)
- `pmc memory list -c fix` to browse all solutions
- `pmc memory search "query" -c user` to recall past conversations

## Date Formats

All date options accept flexible formats:

| Format | Example |
|--------|---------|
| `YYYY-MM-DD` | `2024-06-15` |
| ISO datetime | `2024-06-15T14:30:00` |
| `today` | Current date |
| `yesterday` | Previous day |

## Partial ID Matching

Commands that accept memory IDs (`get`, `update`, `delete`) support **8+ character prefixes**:

```bash
# Instead of full UUID
pmc memory get 550e8400-e29b-41d4-a716-446655440000

# Use 8-char prefix
pmc memory get 550e8400
```

If prefix is ambiguous (matches multiple), an error lists all matches.

## Architecture

```
┌──────────────────────────────────────────┐
│              pmc memory CLI              │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────┴───────────────────────┐
│              MemoryStore                 │
│         SQLite + FTS5 + Embeddings       │
└──────────────────┬───────────────────────┘
                   │
       ┌───────────┼───────────┬───────────┐
       ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ memories │ │  FTS5    │ │ OpenAI   │ │ search   │
│  table   │ │  index   │ │ embeddings│ │  logs    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

**Database:** `.pmc/memory.db`

## Embedding Priority

1. **OpenAI** (if `OPENAI_API_KEY` set) - 1536 dimensions
2. **SentenceTransformer** (if installed) - 384 dimensions
3. **Hash fallback** (always available) - not semantic

## Search Algorithm

### Hybrid Search (Default)

Combines vector and keyword results using Reciprocal Rank Fusion (RRF):

```
score = Σ (1 / (k + rank)) for each method
```

- Gets top results from both vector and keyword search
- Merges using RRF with k=60
- Returns re-ranked combined results

### Vector Search

1. Generate embedding for query using OpenAI
2. Calculate cosine similarity with all stored embeddings
3. Return sorted by similarity score

### Keyword Search

Uses SQLite FTS5 with BM25 ranking for full-text search.

## Best Practices

### What to Store

- **ctx**: Project facts ("uses Postgres 15", "API on port 8080")
- **pref**: User preferences ("no semicolons", "prefers composition")
- **fix**: Solutions found ("restart Redis after config change")
- **note**: Temporary things you might need later
- **user**: Auto-captured by hook; search to recall past conversations

### What NOT to Store

- Temporary notes (use scratch files)
- Large code blocks (use code maps instead)
- Sensitive data (API keys, passwords)

### Effective Queries

```bash
# Good: Conceptual queries
pmc memory search "error handling patterns"
pmc memory search "authentication flow"

# Good: Specific terms
pmc memory search "retry backoff" -m keyword

# Less effective: Too vague
pmc memory search "code"
```

## Integration with KB

Memory complements the KB documentation system:

| KB Docs | Memory |
|---------|--------|
| Structured, versioned | Unstructured, additive |
| Git tracked | Local SQLite |
| Long-form documentation | Short context snippets |
| Shared across team | Per-machine |

Use memory for quick context; use KB docs for permanent knowledge.

## Configuration

In `pmc.config.json`:

```json
{
  "memory": {
    "database": ".pmc/memory.db",
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536,
    "default_limit": 10,
    "injection_max_tokens": 2000
  }
}
```

## Troubleshooting

### "Embedding model: hash-based (fallback)"

OpenAI API key not set. Add to `.env`:
```
OPENAI_API_KEY=sk-...
```

### Search returns no results

1. Check if memories exist: `pmc memory list`
2. Try keyword mode: `pmc memory search "term" -m keyword`
3. Check database path: `pmc memory stats`

### Low similarity scores

- Vector search scores are cosine similarity (0-1)
- Scores below 0.3 indicate weak semantic match
- Try more specific queries or keyword search
