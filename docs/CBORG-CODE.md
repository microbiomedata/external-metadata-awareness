# External Metadata Awareness Development Guidelines

## Build and Run Commands
- Setup: `poetry install`
- Run Python script: `poetry run python external_metadata_awareness/script_name.py`
- Run script alias: `poetry run script-alias` (defined in pyproject.toml)
- Run Makefile target: `make -f Makefiles/target.Makefile target_name` or `make target_name`
- Run linting: `poetry run deptry .`
- Run notebook: `poetry run jupyter notebook`

## Code Style Guidelines
- Python 3.10+ required
- Type hints required (`from typing import List, Dict, Optional`)
- Snake case for variables/functions (`fetch_data`, `process_xml`)
- PascalCase for classes (`MongoClient`, `XMLParser`)
- Google-style docstrings for functions/classes
- Click library for CLI commands with typed options
- Consistent MongoDB connection using `mongodb_connection.py`
- Exception handling with specific exception types
- Environment variables in .env files (loaded with dotenv)
- Use MongoDB for storage, DuckDB for analysis

## Project Organization
- Python modules in `external_metadata_awareness/`
- Makefile targets in `Makefiles/*.Makefile`
- Analysis notebooks in `notebooks/`
- Downloaded data in `downloads/`
- Local files in `local/`
- Lexical matching results in `lexmatch-output/`

---

# Environmental Triad Pipeline Session Log - 2025-10-13

Session documentation from successful completion of the env_triads pipeline.

## Performance Benchmarks

### With Good Cache (64% hit rate)
- **Full pipeline runtime**: ~4 hours (7:50 PM - 11:29 PM)
- **OLS annotation**: 2h 41min (47,410 documents processed)
- **BioPortal processing**: ~4.5 minutes (518 CURIEs)
- **OAK annotation**: ~2.5 minutes (local, no network calls)
- **populate-env-triads-collection**: ~28 minutes (6.2M documents)
- **Index creation**: ~2 minutes (5 indexes on 17M documents)

### Cache Impact Analysis
- **Initial cache state**: 301,382 total entries, only 696 valid (0.2%)
  - 300,686 entries expired (>30 days old)
  - Would have required ~8+ hours for OLS alone
- **After cache replacement**: 99,796 total entries, 63,980 valid (64%)
  - Reduced OLS time from ~7 hours to 2h 41min
  - **Lesson: 30-day cache expiry is critical - old caches are useless**

## Collection Sizes & Statistics

### Final Collections
```
biosamples_flattened:                    49,049,009 documents
biosamples_env_triad_value_counts_gt_1:     69,834 documents
env_triad_component_labels:                  52,067 documents
env_triad_component_curies_uc:                5,367 documents
env_triads:                               6,264,662 documents
env_triads_flattened:                    17,034,191 documents
```

### env_triads_flattened Structure
- **Average components per biosample**: 2.72
- **Fields**: `accession | attribute | instance | raw_original | raw_component | id | label | prefix | source`
- **Indexes**:
  - `accession_1` (26 sec)
  - `attribute_1_instance_1` (27 sec)
  - `id_1` (25 sec)
  - `prefix_1` (25 sec)
  - `accession_1_attribute_1_instance_1` (30 sec)

### Sample Record
```javascript
{
  accession: "SAMN46496120",
  attribute: "env_broad_scale",
  instance: 0,
  raw_original: "agricultural soil [ENVO:00002259]",
  raw_component: "agricultural soil",
  id: "ENVO:00002259",
  label: "agricultural soil",
  prefix: "ENVO",
  source: "OAK"
}
```

## Annotation Coverage

### Annotation Sources
- **OAK annotations**: 24,409 successful mappings (local ENVO/PO lexical index)
- **OLS annotations**: 1,408 successful mappings (EBI OLS API with cache)
- **BioPortal mappings**: 518 CURIEs processed with cross-ontology mappings

### Cross-Ontology Mappings Discovered
Interesting examples from BioPortal processing:

**Agricultural terms (AGRO → ENVO)**
- AGRO:00000079 (animal manure) → ENVO:00003031
- AGRO:00000080 (poultry litter) → ENVO:00002192
- AGRO:00000363 (greenhouse) → ENVO:03600087

**Biological tissues (BTO → UBERON, PO)**
- BTO:0000081 (reproductive system) → UBERON:0000990
- BTO:0000486 (fruit) → PO:0009001
- BTO:0001188 (root) → PO:0009005, PO:0025025

**Chemical/Material (CHEBI → ENVO, FOODON)**
- CHEBI:15377 (water) → ENVO:00002006
- CHEBI:53243 (polyvinyl chloride) → FOODON:03500037

**Anatomical (NCIT → UBERON)**
- NCIT:C12381 (Cecum) → UBERON:0001153
- NCIT:C12407 (Vagina) → UBERON:0000996
- NCIT:C13234 (Feces) → UBERON:0001988, ENVO:00002003

## Common Issues & Pitfalls

### 1. MongoDB `$out` Operator Overwrites
- JavaScript files using `$out` (e.g., `enriched_biosamples_env_triad_value_counts_gt_1.js`) **replace entire collections**
- Make targets don't detect existing MongoDB collections
- **Impact**: Lost 52K annotated labels when pipeline restarted
- **Solution**: Check collection status before running, or add collection existence checks to Makefiles

### 2. ENV_FILE Parameter Required
- BioPortal API key must be in `local/.env`
- Must pass `ENV_FILE=local/.env` to make targets
- Scripts use `os.getenv()` which checks system environment first
- **Without it**: Pipeline fails at `env-triad-values-splitter` step

### 3. Cache Expiration Silent Failure
- `requests_cache` expires entries after 30 days by default
- Old caches appear to work but hit network for every request
- **Symptom**: Process takes 7+ hours instead of <3 hours
- **Detection**: Check `sqlite3 cache.db "SELECT COUNT(*) FROM responses WHERE expires > strftime('%s', 'now')"`

### 4. Malformed CURIEs
Failed expansions for non-standard colon-separated identifiers:
```
AFTER:PROCESSING, AGRICULTURAL:FEATURE, ARID:BIOME,
CO:ASSEMBLY, DAY:24, FIELD:CONDITIONS, GUT:001-024,
IN:VITRO, LAB:REARED, ONE:DAY, PRE:MORPHINE, etc.
```
These are not valid ontology CURIEs despite containing colons.

## Makefile Time Estimates vs Actual

| Step | Makefile Comment | Actual Time |
|------|------------------|-------------|
| `biosamples-flattened` | (no estimate) | ~2.5 min |
| `env-triad-values-splitter` | "< 1 minute" | ~22 sec ✓ |
| `env-triad-oak-annotator` | "3 minutes" | ~2.5 min ✓ |
| `env-triad-ols-annotator` | "7 min w/cache; 7 hrs w/o" | 2h 41min (needs update) |
| `env-triad-bioportal-curie-mapper` | "2 min w/cache; 13 min w/o" | ~4.5 min (partial cache) |
| `populate-env-triads-collection` | "30 min + 6 for indexing" | ~28 min ✓ |

**Note**: OLS time highly dependent on cache freshness and hit rate.

## Command Sequence Used

### Initial Failed Attempt
```bash
make -f Makefiles/env_triads.Makefile env-triads
```
- Triggered `biosamples-flattened` dependency unnecessarily
- Started re-flattening 49M documents
- Aborted after ~10 minutes

### Successful Run
```bash
# 1. Manual cleanup of empty collections
poetry run mongo-connect --uri "mongodb://localhost:27017/ncbi_metadata" \
  --connect --command "db.env_triads.drop(); db.env_triads_flattened.drop();"

# 2. Run value counts and annotation pipeline
make -f Makefiles/env_triads.Makefile env-triad-value-counts ENV_FILE=local/.env

# 3. Flatten the populated env_triads collection
make -f Makefiles/env_triads.Makefile env-triads-flattened ENV_FILE=local/.env
```

## Lessons Learned

1. **Cache is critical** - 64% hit rate reduced 7-hour step to 2h 41min
2. **Cache freshness matters** - 30-day expiry means monthly pipeline runs need fresh cache
3. **Make targets are not idempotent** - MongoDB operations don't check for existing data
4. **ENV_FILE must be explicit** - Don't rely on system environment for API keys
5. **BioPortal provides valuable cross-ontology mappings** - Many terms map to ENVO/UBERON
6. **Monitoring is essential** - Pipeline provides minimal progress feedback during long operations

## Recommendations for Documentation

1. **Update ENV_TRIAD_WORKFLOW.md**:
   - Add realistic time estimates with cache considerations
   - Document cache hit rate impact
   - Add collection size expectations

2. **Update Makefile comments**:
   - Correct OLS time estimate (2-3 hours typical with good cache)
   - Add cache freshness warnings
   - Note ENV_FILE requirement prominently

3. **Create TROUBLESHOOTING.md**:
   - Cache expiration issues
   - ENV_FILE requirements
   - MongoDB `$out` overwrite behavior
   - How to check pipeline progress

4. **Update ARCHITECTURE.md**:
   - Final collection sizes (6.2M env_triads, 17M flattened)
   - Annotation coverage statistics
   - Cross-ontology mapping examples

## Date/Time Log

```
Started: Mon Oct 13 19:50:25 EDT 2025
Completed: Mon Oct 13 23:29:00 EDT 2025
Total Duration: ~3h 39min
```

## System Info

- MongoDB: Running on localhost:27017
- Database: ncbi_metadata
- Cache file: external-metadata-awareness-requests-cache.sqlite (2.1GB)
- Python: 3.11.10
- Poetry environment: .venv
