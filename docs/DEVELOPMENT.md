# Development Guide

Guidelines for contributing code, testing, and maintaining this repository.

---

## Code Style Guidelines

### Python Requirements
- **Version**: Python >= 3.10 required
- **Type Hints**: Expected for all function parameters and returns
  ```python
  from typing import List, Dict, Tuple, Optional

  def process_biosamples(ids: List[str]) -> Dict[str, Any]:
      ...
  ```

### Documentation
- **Docstrings**: Google style preferred
  ```python
  def normalize_date(date_str: Optional[str]) -> Optional[str]:
      """
      Normalize date string to YYYY-MM-DD format.

      Args:
          date_str: Input date string in various formats

      Returns:
          Date in YYYY-MM-DD format, or None if invalid
      """
  ```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `calculate_value`, `biosample_id`)
- **Classes**: `PascalCase` (e.g., `MongoDBConnection`, `BioportalMapper`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_BATCH_SIZE`, `DEFAULT_TIMEOUT`)
- **DuckDB Files**: Use underscores, not hyphens (e.g., `ncbi_metadata_flat_20251019.duckdb`)
  - Pattern: `{source}_{description}_{YYYYMMDD}.duckdb`
  - Rationale: Hyphens require quoting in DuckDB SQL
  - See: [Issue #282](https://github.com/microbiomedata/external-metadata-awareness/issues/282)

### CLI Tools
- **Framework**: Use Click library for CLI commands
- **Help Text**: Always provide clear help text
  ```python
  @click.command()
  @click.option('--input-file', required=True, help='Input CSV file path')
  def process_file(input_file: Path) -> None:
      """Process biosample data from CSV."""
  ```

### Logging vs Print
- **Use logging, not print()** (except for CLI tool output)
- **See**: [Issue #203](https://github.com/microbiomedata/external-metadata-awareness/issues/203)
- **Pattern**:
  ```python
  import logging
  logger = logging.getLogger(__name__)

  logger.info("Processing 1000 biosamples")
  logger.warning("Missing collection_date for 50 biosamples")
  ```

### Error Handling
- **Use specific exceptions**, not bare `except:`
  ```python
  try:
      data = parse_biosample(xml)
  except XMLParseError as e:
      logger.error(f"Failed to parse biosample: {e}")
      raise
  ```

### Environment Variables
- **Store in .env files** (gitignored)
- **Load with python-dotenv**:
  ```python
  from dotenv import load_dotenv
  load_dotenv('local/.env')
  api_key = os.getenv('BIOPORTAL_API_KEY')
  ```

---

## Project Structure

### Package Organization
Scripts registered in `pyproject.toml` under `[tool.poetry.scripts]`:
```toml
[tool.poetry.scripts]
normalize-satisfying-biosamples = 'external_metadata_awareness.normalize_satisfying_biosamples:normalize_biosamples'
mongo-connect = 'external_metadata_awareness.mongodb_connection:main'
```

### Primary Tools
- **Data Processing**: pandas, duckdb, pymongo
- **CLI**: Click
- **Ontologies**: OAK (ontology-access-kit)
- **Date Parsing**: dateparser
- **Coordinates**: geopy

### Configuration
- **Preferences**: YAML files (e.g., `voting_sheets_configurations.yaml`)
- **Credentials**: .env files (never commit)
- **Settings**: pyproject.toml for dependencies and CLI aliases

---

## Git Workflow

### Branching Strategy
- **main**: Stable, deployable code
- **Feature branches**: `feature/issue-123-description`
- **Bugfix branches**: `bugfix/issue-456-description`

### Commit Messages
```
Add date normalization for biosample CSV export

- Implement normalize_date() with dateparser
- Handle year-only and year-month formats
- Add imputation logging for missing day/month

Closes #214
```

### Pull Requests
- **Link to issues**: Use "Closes #123" in PR description
- **Small, focused PRs**: One logical change per PR
- **Self-review**: Review your own diff before requesting review
- **Tests**: Add tests for new functionality (when test infrastructure exists)

### What NOT to Commit
❌ Large files (>100MB) - Use `local/` directory instead
❌ Credentials (.env files) - Already in .gitignore
❌ Generated data (DuckDB files, CSVs) - Use `local/` directory
❌ Virtual environments - Poetry manages dependencies
❌ IDE configs (.vscode/, .idea/) - Use global gitignore

---

## Testing

### Current State
- **Status**: `/tests/__init__.py` exists but no test files present
- **Coverage**: No automated testing currently
- **Manual Testing**: Scripts tested via Makefile targets

### Future Testing Strategy (Issue TBD)
```python
# tests/test_normalize_biosamples.py
import pytest
from external_metadata_awareness.normalize_satisfying_biosamples import normalize_date

def test_normalize_date_iso_format():
    assert normalize_date('2024-01-15') == '2024-01-15'

def test_normalize_date_year_only():
    assert normalize_date('2024') == '2024-01-01'

def test_normalize_date_invalid():
    assert normalize_date('not-a-date') is None
```

### Testing Tools (when implemented)
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Fixtures**: Shared test data in `tests/fixtures/`

---

## Dependencies

### Adding New Dependencies
```bash
# Add to main dependencies
poetry add package-name

# Add to dev dependencies
poetry add --group dev package-name

# Update lock file
poetry lock

# Install updated dependencies
poetry install
```

### Dependency Audit
- **Check unused**: [Issue #42](https://github.com/microbiomedata/external-metadata-awareness/issues/42)
- **Known unused** (as of 2025-10-02):
  - `git-filter-repo`
  - `llm`
  - `textdistance`
  - `case-converter`

### Security Updates
```bash
# Update all dependencies to latest compatible versions
poetry update

# Update specific package
poetry update package-name
```

---

## Development Areas & TODOs

### Active Infrastructure Work
See [Issue #223](https://github.com/microbiomedata/external-metadata-awareness/issues/223) for tracking:

1. **MongoDB Connection Unification** ([#176](https://github.com/microbiomedata/external-metadata-awareness/issues/176))
   - Standardize on URI-style connections
   - Use `mongodb_connection.py` utility everywhere
   - Consistent parameter naming

2. **Logging Framework** ([#203](https://github.com/microbiomedata/external-metadata-awareness/issues/203))
   - Replace print() with logging
   - Configure log levels
   - Add log rotation

3. **Code Quality Checks** ([#202](https://github.com/microbiomedata/external-metadata-awareness/issues/202))
   - Pre-commit hooks
   - Linters: ruff, black, mypy
   - GitHub Actions CI

### Known Issues

**Orphaned Scripts** (may need cleanup):
- `cborg_test.py`: CBORG API test script
- `dict_print_biosamples_from_efetch.py`: Standalone script
- `entrez_vs_mongodb.py`: Comparison tool
- `study-image-table.py`: Non-standard naming

**Abandoned Directories**:
- `notebooks/old/`: Superseded notebooks
- `unorganized/`: Documentation needing organization

**Makefile TODOs**:
- `Makefiles/ncbi_metadata.Makefile`: 18+ TODOs about architecture
- Focus areas: Logging, connection handling, optimization

---

## Performance Patterns

### Batch Processing
Always process in batches for large datasets:
```python
BATCH_SIZE = 10_000

for i in range(0, total_count, BATCH_SIZE):
    batch = collection.find().skip(i).limit(BATCH_SIZE)
    process_batch(batch)
```

### Progress Reporting
Use tqdm for user-facing progress:
```python
from tqdm import tqdm

for biosample in tqdm(biosamples, desc="Processing biosamples"):
    process(biosample)
```

**Note**: [Issue #159](https://github.com/microbiomedata/external-metadata-awareness/issues/159) tracks adding tqdm to more scripts

### Unique Value Deduplication
Process unique values first, then map back:
```python
# Fast: Process 6,660 unique dates
unique_dates = df['collection_date'].unique()
date_map = {d: normalize_date(d) for d in unique_dates}
df['collection_date_normalized'] = df['collection_date'].map(date_map)

# Slow: Process 506,000 rows individually ❌
df['collection_date_normalized'] = df['collection_date'].apply(normalize_date)
```

### MongoDB Indexing
Create indexes for frequently queried fields:
```javascript
// In mongo-js scripts
db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true});
db.env_triads_flattened.createIndex({accession: 1, component: 1}, {background: true});
```

---

## MongoDB JavaScript Patterns

### Execution Methods

**Preferred: mongo-js-executor** (Python wrapper - standardized interface)

Use for all production scripts in `mongo-js/` directory:
```bash
# Standard pattern
$(RUN) mongo-js-executor \
  --mongo-uri "$(MONGO_URI)" \
  $(ENV_FILE_OPTION) \
  --js-file mongo-js/your_script.js \
  --verbose
```

Benefits:
- Consistent URI handling across all scripts
- Supports .env files for configuration
- Better error handling and logging
- Database name can be parameterized via URI

**Alternative: mongosh --eval** (Direct shell - use sparingly)

Use only for:
- One-line commands (drop collections, quick counts)
- Ad-hoc debugging queries
- Simple maintenance tasks

```bash
mongosh "$(MONGO_URI)" --eval "db.collection.countDocuments()"
```

Limitations:
- Harder to parameterize database names
- No .env file support
- Inconsistent quoting across shells

### Best Practices for JS Scripts

**Database Inheritance**: JS scripts inherit DB from connection URI
```javascript
// ✅ Good: Use db object from mongosh context
const collection = db.measurement_results_skip_filtered;

// ❌ Avoid: Hardcoding database names
const collection = db.getSiblingDB('ncbi_metadata').measurement_results;
```

**Documentation Headers**: Include standard header in all scripts
```javascript
// Purpose: One-line description
// Input: Source collection(s) and expected size
// Output: Target collection and expected size
// Related: Issue #XXX
```

**Progress Reporting**: For long-running operations
```javascript
print(`Processing ${total} documents...`);
// ... operation
print(`✓ Created ${result.insertedCount} documents`);
```

### Related Issues
- [#281](https://github.com/microbiomedata/external-metadata-awareness/issues/281) - Database name parameterization
- [#282](https://github.com/microbiomedata/external-metadata-awareness/issues/282) - Naming conventions

---

## Debugging Tips

### MongoDB Queries
Use `mongosh` for interactive debugging:
```bash
mongosh mongodb://localhost:27017/ncbi_metadata

# Count documents
db.biosamples.countDocuments()

# Find examples
db.biosamples.findOne()

# Check indexes
db.biosamples.getIndexes()
```

### DuckDB Queries
Use DuckDB CLI for quick analysis:
```bash
duckdb local/ncbi_biosamples.duckdb

# Show tables
.tables

# Describe schema
DESCRIBE biosamples;

# Query data
SELECT COUNT(*) FROM biosamples WHERE collection_date >= '2024-01-01';
```

### Python Debugging
```python
# Use logging for production
logger.debug(f"Processing biosample: {biosample_id}")

# Use print for quick debugging (remove before commit)
print(f"DEBUG: {variable_name = }")  # Python 3.8+ f-string debug syntax
```

---

## Documentation Standards

### README Files
- Each major workflow should have a README in its directory
- Example: `notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md`

### Code Comments
- **When to comment**: Explain "why", not "what"
- **Good**: `# Impute day=01 for year-month dates to avoid dateparser using current day`
- **Bad**: `# Set day to 01`

### Docstring Requirements
All public functions/classes need docstrings:
```python
def process_biosamples(collection_name: str, batch_size: int = 1000) -> int:
    """
    Process biosamples from MongoDB collection in batches.

    Args:
        collection_name: Name of MongoDB collection to process
        batch_size: Number of biosamples to process per batch (default: 1000)

    Returns:
        Total number of biosamples processed

    Raises:
        pymongo.errors.ConnectionFailure: If MongoDB is unavailable
        ValueError: If collection_name is empty
    """
```

---

## Release Process

### Versioning
- **Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Current**: 0.1.0 (pre-release)
- **Update**: Edit `version` in `pyproject.toml`

### Changelog
- Consider maintaining CHANGELOG.md for significant changes
- Format: Keep a Changelog style

### Tagged Releases
```bash
git tag -a v0.2.0 -m "Add biosample normalization tools"
git push origin v0.2.0
```

---

## Resources

### Internal Documentation
- **CLAUDE.md**: Command reference and key concepts
- **ARCHITECTURE.md**: Database systems and data flow
- **GETTING_STARTED.md**: Quick start for new contributors
- **PRIORITY_ROADMAP.md**: Current priorities and issue categories

### External Resources
- **Poetry**: https://python-poetry.org/docs/
- **Click**: https://click.palletsprojects.com/
- **OAK**: https://incatools.github.io/ontology-access-kit/
- **MongoDB**: https://www.mongodb.com/docs/
- **DuckDB**: https://duckdb.org/docs/

### Issue Templates
When creating issues:
- Link to related issues
- Provide code examples or error messages
- Specify affected files/functions
- Include steps to reproduce (for bugs)

---

## Questions?

- Open an issue for bugs or feature requests
- See [GETTING_STARTED.md](GETTING_STARTED.md) for onboarding
- Check [PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md) for current work focus
