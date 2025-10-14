# External Metadata Awareness - AI Assistant Guide

**Cost Control Priority**: Keep responses concise. User pays per token for input AND output.

---

## AI Assistant Cost Guidelines

**Default Behavior**:
- **Be terse**: 1-3 sentences per explanation
- **Don't read files proactively**: Wait for explicit request
- **No verbose artifacts**: No session logs, exhaustive docs, or command references unless asked
- **Use bullets, not paragraphs**
- **Quote minimal code**: <10 lines, only when essential
- **Ask before deep dives**: "Want me to analyze X?" vs. auto-analyzing

**When Writing Issues/Docs**:
- Max 5 bullet points for issue descriptions
- No restating obvious information
- No comprehensive background sections
- Focus: What needs doing + immediate context only

**User will interrupt you** if output is too verbose. Treat that as feedback to be even more concise.

---

## Essential Commands

```bash
# Poetry
poetry run <script-name>  # See pyproject.toml [tool.poetry.scripts]

# Make
make -f Makefiles/<file>.Makefile <target> ENV_FILE=local/.env

# MongoDB
poetry run mongo-connect --uri mongodb://localhost:27017/ncbi_metadata --connect
```

---

## Critical Warnings

- `make purge` drops entire database
- MongoDB `$out` completely replaces collections
- Always use `ENV_FILE=local/.env` for BioPortal key
- Don't use `print()` - use logging (#203)
- Don't commit to main - use PRs

---

## Key Locations

- `Makefiles/`: Pipeline orchestration
- `external_metadata_awareness/`: Python scripts
- `mongo-js/`: MongoDB aggregations
- `notebooks/environmental_context_value_sets/`: Voting sheet generation
- `local/`: Gitignored data/caches

---

## Current Work

- **#222**: Biosample normalization
- **#223**: Infrastructure improvements

---

## Documentation

**Quick reference** (extracted to save tokens):
- [CLAUDE_FULL_REFERENCE.md](docs/CLAUDE_FULL_REFERENCE.md) - Complete commands/concepts (load manually when needed)

**Primary docs** (for detailed work):
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Collections, schemas, data flow
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Code style, testing
- [PRIORITY_ROADMAP.md](docs/PRIORITY_ROADMAP.md) - Issue priorities
- [ENV_TRIAD_WORKFLOW.md](docs/ENV_TRIAD_WORKFLOW.md) - Environmental triad pipeline

**Historical context** (rarely needed):
- `docs/` - Session notes, analysis (49 files, may be outdated)
- `unorganized/` - Analysis archives

---

## Questions?

Open issue or PR. Keep descriptions brief.
