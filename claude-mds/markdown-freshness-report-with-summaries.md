# Markdown Files Freshness Report with Summaries
Generated: 2025-09-30

## Quick Navigation
- [Root Directory Files](#root-directory-files-by-modification-time)
- [Most Recent Files (Sept 26-30)](#most-recent---highest-reliability-sept-26-30-2025)
- [Older Files](#older-files-for-reference)

## Summary Statistics
- **Total markdown files (excluding .venv)**: 50
- **Files modified in last 7 days**: 19 (most recent and reliable)
- **Files from April-May 2025**: 14 (5-6 months old)
- **Files older than 6 months**: 19 (potentially stale)

## Root Directory Files (by modification time)

```
-rw-r--r--@ 1 MAM  staff   5845 Sep 30 08:12 markdown-freshness-report.md
-rw-r--r--@ 1 MAM  staff  20183 Sep 30 08:00 biosample-flattening-timeline-2020-2025.md
-rw-r--r--@ 1 MAM  staff  18802 Sep 29 15:50 compass_artifact_wf-06eefb19-9272-4def-9e2c-7206bd671ea2_text_markdown.md
-rw-r--r--  1 MAM  staff   6685 Sep 29 11:12 environmental-context-targets-not-covered-2025-09-29.md
-rw-r--r--  1 MAM  staff   8197 Sep 29 10:32 measurement-discovery-completion-and-cleanup-2025-09-29.md
-rw-r--r--  1 MAM  staff   5121 Sep 29 09:10 measurement_field_insights_2025-09-29.md
-rw-r--r--@ 1 MAM  staff   4086 Sep 29 08:39 claude_overnight_skip_analysis_2025-09-29.md
-rw-r--r--  1 MAM  staff   5202 Sep 28 22:05 schema-based-ranking-removal-2025-09-28.md
-rw-r--r--  1 MAM  staff   8808 Sep 28 21:08 session-addendum-2025-09-28.md
-rw-r--r--@ 1 MAM  staff   8894 Sep 28 15:36 architectural-pattern-inconsistency-analysis.md
-rw-r--r--  1 MAM  staff  10455 Sep 28 14:47 measurement-value-unit-extraction-strategies.md
-rw-r--r--  1 MAM  staff   7632 Sep 28 14:31 measurement-discovery-consistency-assessment.md
-rw-r--r--  1 MAM  staff   7383 Sep 28 09:33 consistency-audit-2025-09-27.md
-rw-r--r--  1 MAM  staff   8906 Sep 28 07:59 session-addendum-2025-09-27.md
-rw-r--r--  1 MAM  staff   9935 Sep 27 01:04 NMDC_Biosample_Measurement_Discovery_Strategy.md
-rw-r--r--  1 MAM  staff   5771 Sep 26 13:58 session-addendum-2025-09-26.md
-rw-r--r--  1 MAM  staff  11446 Sep 26 10:49 session-summary-2025-09-26.md
-rw-r--r--@ 1 MAM  staff   2268 Sep 25 13:41 sra_duckdb_vs_parquet.md
-rw-r--r--@ 1 MAM  staff  27122 Apr  5 11:19 CLAUDE.md
```

---

## Most Recent - Highest Reliability (Sept 26-30, 2025)

### 1. `biosample-flattening-timeline-2020-2025.md` ⭐ **NEWEST & MOST COMPREHENSIVE**
**Sep 30, 2025** | **20KB**

**Summary**: Comprehensive 5-year timeline documenting evolution of biosample flattening from INCATools (2020) through to-duckdb (2025). Documents collaboration between turbomam, Chris Mungall, and Bill Duncan across 6 major phases. Includes:
- Complete collection architecture with critical collections (`measurement_results_skip_filtered`, `env_triads_flattened`)
- Strategic filtering for Google Earth embeddings alignment (3M from 45M samples)
- GOLD (API vs Excel) and NMDC DuckDB approaches
- NERSC hosting details (m3408, m3513)
- Schema stability notice
- XML path inclusion/exclusion documentation

**Key Value**: Canonical reference for ALL biosample flattening work; replaces outdated documentation

---

### 2. `markdown-freshness-report.md`
**Sep 30, 2025** | **6KB**

**Summary**: This report (original version without summaries). Categorizes all markdown files by age with recommendations for sharing with another LLM for documentation collaboration.

---

### 3. `compass_artifact_wf-06eefb19-9272-4def-9e2c-7206bd671ea2_text_markdown.md`
**Sep 29, 2025** | **19KB**

**Summary**: Complete guide for submitting ontologies to EBI's Ontology Lookup Service (OLS). Covers:
- Two submission pathways: Direct OLS vs OBO Foundry registration
- Technical requirements: OWL/RDF formats, ROBOT validation, Dublin Core metadata
- Common pain points: Format confusion, import dependency failures, timeline uncertainty
- Human review processes and validation infrastructure
- Local installation and deployment considerations

**Key Value**: Detailed procedural guide for ontology submission workflows

---

### 4. `environmental-context-targets-not-covered-2025-09-29.md`
**Sep 29, 2025** | **7KB**

**Summary**: Analysis of environmental context/triad processing targets NOT covered by main `env-triads` pipeline. Documents:
- NMDC-specific environmental processing (predictions, soil extraction)
- MIxS schema extraction for triad fields
- NCBI environmental candidates filtering (2017+)
- GOLD environmental context processing
- Workflow recommendations for cross-database analysis

**Key Value**: Identifies complementary environmental processing pipelines beyond main workflow

---

### 5. `measurement-discovery-completion-and-cleanup-2025-09-29.md`
**Sep 29, 2025** | **8KB**

**Summary**: Major milestone session completing comprehensive measurement discovery. Achievements:
- Processed 247,556 harmonized_name/content pairs with quantulum3
- Applied 208-field data-driven skip list
- Created `measurement_results_skip_filtered` collection
- Project cleanup: Moved Python files to package structure, removed 5 obsolete Makefile targets, cleaned 4 backup collections
- Established production-ready measurement discovery workflow

**Key Value**: Documents transition from experimental to production-ready measurement discovery

---

### 6. `measurement_field_insights_2025-09-29.md`
**Sep 29, 2025** | **5KB**

**Summary**: Semantic analysis of measurement vs non-measurement fields. Key findings:
- True measurements: spatial/physical (area, temperature), chemical properties (pH)
- Parsing challenges: Complex chemicals, time formats (ISO 8601)
- Categorical false positives: Fields with "not applicable" dominance
- Recommendations for predictive modeling using schema types and semantic keywords

**Key Value**: Domain knowledge patterns for distinguishing true measurements from categorical data

---

### 7. `claude_overnight_skip_analysis_2025-09-29.md`
**Sep 29, 2025** | **4KB**

**Summary**: Data-driven analysis identifying additional fields to skip in measurement processing:
- High-confidence skips: Categorical fields, zero parse success, single-value dominated
- Medium-confidence skips: Multiple quantulum3 outputs, high dimensionless ratio
- ~35 additional recommendations beyond collaborative skip list
- Impact: Combined skip list ~191 harmonized_names

**Key Value**: Automated recommendations separate from manual MAM+Claude collaborative list

---

### 8. `schema-based-ranking-removal-2025-09-28.md`
**Sep 28, 2025** | **5KB**

**Summary**: Removed misleading schema-based measurement ranking systems. Problem: Rankings gave high scores to fields with zero actual data (e.g., `annual_precpt` score 62.4 but 0 documents). Actions:
- Dropped 3 untrusted collections (`measurement_attribute_rankings`, `unified_measurement_attribute_rankings`, `nmdc_slot_usage_analysis`)
- Removed 5 schema-based scripts
- Preserved empirical evidence collections

**Key Value**: Documents shift from schema-based to empirical data-driven measurement discovery

---

### 9. `session-addendum-2025-09-28.md`
**Sep 28, 2025** | **9KB**

**Summary**: Session completing measurement parsing pipeline and implementing enhanced ranking framework. Achievements:
- Background pipeline: 19,795 unique `host_age` values parsed (85% success rate)
- Enhanced framework with multi-evidence scoring (pattern exclusion, value variation, quantulum3 validation, semantic similarity)
- Test validation successful (correctly distinguished measurements from false positives)

**Key Value**: Documents replacement of failed schema-based approach with working multi-evidence framework

---

### 10. `architectural-pattern-inconsistency-analysis.md`
**Sep 28, 2025** | **9KB**

**Summary**: Analysis of problematic pattern using mongosh as general-purpose JavaScript runtime for YAML parsing, file I/O, and shell commands. Issues:
- Tool misuse (mongosh designed for database operations)
- Architectural confusion (blurs data processing vs storage)
- Maintenance complexity
- Recommendations: Use Python for data processing, shell commands in Makefiles, mongosh for database operations only

**Key Value**: Identifies anti-pattern to avoid in future development

---

### 11. `measurement-value-unit-extraction-strategies.md`
**Sep 28, 2025** | **10KB**

**Summary**: Strategies for efficient value/unit extraction addressing quantulum3 limitations. Approaches:
- Domain knowledge overlay (biomedical/environmental unit dictionaries)
- Value distribution analysis (statistical profiling)
- Unit consensus scoring (reliability assessment)
- Tiered regex patterns for fast first-pass extraction

**Key Value**: Practical strategies for improving measurement parsing beyond quantulum3

---

### 12. `measurement-discovery-consistency-assessment.md`
**Sep 28, 2025** | **8KB**

**Summary**: Assessment of measurement discovery pipeline consistency with codebase patterns. Strengths:
- Consistent connection patterns via mongo-js-executor
- Small focused Makefile targets
- Error-tolerant infrastructure
Areas needing improvement: Collection naming accuracy, target naming consistency, metatarget coverage

**Key Value**: Quality assurance review ensuring pipeline follows established patterns

---

### 13. `consistency-audit-2025-09-27.md`
**Sep 28, 2025** | **7KB**

**Summary**: Critical consistency issues introduced during harmonized name counting pipeline development:
- Collection name mismatch (creates `harmonized_name_counts`, indexes `harmonized_name_usage_stats`)
- Implementation pattern inconsistency (mixed mongo-js-executor vs embedded mongosh JavaScript)
- MongoDB connection configuration inconsistency
- Target naming inconsistency (step-based vs descriptive naming)

**Key Value**: Documents technical debt requiring remediation

---

### 14. `session-addendum-2025-09-27.md`
**Sep 28, 2025** | **9KB**

**Summary**: Session implementing NCBI metadata measurement discovery pipeline. Achievements:
- SRA biosample-bioproject relationship pipeline (31.8M pairs)
- Three-step harmonized name counting system (biosamples → bioprojects → merged results)
- Overcame memory explosions and network timeout issues with checkpoint-based processing

**Key Value**: Documents robust large-scale MongoDB aggregation patterns

---

### 15. `NMDC_Biosample_Measurement_Discovery_Strategy.md`
**Sep 27, 2025** | **10KB**

**Summary**: Comprehensive strategy for measurement discovery in NCBI biosamples. Addresses:
- Quantulum3 unit parsing issues (PSU → wrong units, host age abbreviations)
- Manual curation limitations (258-field hardcoded list)
- Four-phase automated pipeline: Discovery → Prioritization → Processing → Export
- Unit correction strategies and normalization approaches

**Key Value**: Strategic overview of measurement discovery methodology

---

### 16. `session-addendum-2025-09-26.md`
**Sep 26, 2025** | **6KB**

**Summary**: Discovery of four-Makefile NCBI architecture:
- `ncbi_metadata.Makefile` - Core loading/flattening
- `ncbi_biosample_measurements.Makefile` - Measurements processing
- `ncbi_schema.Makefile` - Schema/package definitions
- `env_triads.Makefile` - Environmental context analysis

Documents comprehensive collection coverage and pipeline dependencies

**Key Value**: Architectural overview of NCBI processing infrastructure

---

### 17. `session-summary-2025-09-26.md`
**Sep 26, 2025** | **11KB**

**Summary**: NCBI biosamples analysis session covering:
- Schema structure (nested XML-derived with `Attributes.Attribute` arrays)
- Environmental triad fields and indexes
- Date handling (ISO timestamps)
- Data distribution (44M total, 30M post-2017, 5M complete triads)
- Google Earth Alpha satellite embeddings alignment
- Pipeline: Subset → Flatten → Enhance → DuckDB export

**Key Value**: Foundational understanding of NCBI biosample structure and processing goals

---

### 18. `sra_duckdb_vs_parquet.md`
**Sep 25, 2025** | **2KB**

**Summary**: Best practices for SRA metadata in DuckDB. Recommendations:
- Default: Query Parquet in place (zero copy, interoperability, performance)
- Materialize when: Need mutations, portable artifact, performance tuning, MotherDuck sync
- Hybrid pattern: Keep raw Parquet, lightweight DuckDB catalog for views/UDFs

**Key Value**: Practical guidance on DuckDB vs Parquet trade-offs for SRA data

---

## Canonical Reference (April 2025)

### 19. `CLAUDE.md`
**April 5, 2025** | **27KB**

**Summary**: Primary project instructions file containing:
- Build/run commands (Poetry, Makefiles, notebooks)
- Environmental context voting sheets quickstart
- MongoDB/DuckDB/SQLite database documentation
- XML processing workflow
- External data fetching methods
- Code style guidelines
- Project structure conventions

**Status**: Should be reviewed/updated for current state. Many sections accurate but some may need updates based on recent work.

**Key Value**: Core reference for project conventions and workflows

---

## Older Files (For Reference)

### `claude-mds/` Directory (April-May 2025, 5-6 months old)
Collection of technical analysis documents created during April-May 2025 sessions. Potentially outdated:

- `which-file-type-where.md` (Apr 28) - File type organization patterns
- `to-do-mongo-js.md` (Apr 28) - MongoDB JavaScript todos
- `env_triads.md` (Apr 28) - Environmental triads analysis
- `env-triad-annotation.md` (Apr 28) - Annotation approaches
- `adhoc-scripts-db-analysis.md` (Apr 28) - Ad-hoc analysis scripts
- `requests-caching.md` (Apr 26) - Web request caching patterns
- `postgres-sqlite-usage-analysis.md` (Apr 26) - Database technology usage
- `makefile-analysis.md` (Apr 26) - Makefile structure analysis
- `gold-knowledge-management.md` (Apr 26) - GOLD data handling
- `enviema.md` (Apr 26) - Environmental metadata analysis
- `env-triads-makefile-scripts-update.md` (Apr 26) - Pipeline updates
- `cache-consolidation.md` (Apr 26) - Caching consolidation work
- `submission-schema-CLAUDE.md` (Apr 1) - Submission schema documentation
- `nmdc-env-triad-valueset-lifecycle.md` (Apr 1) - NMDC value set lifecycle

**Note**: Review these for obsolete information before using. They predate significant measurement discovery and collection architecture work.

---

### `unorganized/` Directory (Feb-Aug 2024, 7-13 months old)
Explicitly marked as potentially outdated content:

- `README_root.md` (Feb 25, 2025)
- `README_environmental_context_value_sets.md` (Feb 25, 2025)
- `PRODUCT_STATUS.md` (Feb 25, 2025)
- `mongodb-commands-and-historical-performance.md` (Feb 5, 2025)
- `llm-models-inc-some-plugins.md` (Aug 16, 2024)
- `sty-11-zs2syx06_nmdc-metadata-vs-paper-via-claude.md` (Aug 16, 2024)
- `resources-to-explore.md` (Aug 16, 2024)
- `interesting-studies.md` (Aug 16, 2024)
- `PRJEB21776.md` (Aug 16, 2024)

**Note**: The directory name itself suggests careful review needed. Likely contains historical context but potentially outdated technical details.

---

### Notebook READMEs (Feb-Dec 2024, 6-10 months old)

- `notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md` (Feb 25, 2025)
- `notebooks/voting-sheet-generation-readme.md` (Dec 18, 2024)
- `notebooks/environmental_context_value_sets/voting_sheets_output/filtering_and_prioritizing_voting_sheet_rows.md` (Dec 18, 2024)
- `notebooks/studies_exploration/emp_500_ng/misc/ocean-depth-confirmation/README.md` (Feb 25, 2025)
- `notebooks/studies_exploration/emp_500_ng/myrold/README.md` (Feb 24, 2025)
- `notebooks/software_methods_exploration/biosample_to_bioproject.md` (Feb 10, 2025)
- `notebooks/studies_exploration/ncbi_annotation_mining/README.md` (Mar 23, 2025)
- `notebooks/mixs_inline_examples_checking/todo.md` (Mar 10, 2025)
- `notebooks/studies_exploration/ncbi_annotation_mining/triad_values_with_envo_review.md` (Mar 10, 2025)

**Note**: May contain valuable workflow documentation but technical details likely superseded by recent work.

---

## Recommendations for LLM Documentation Collaboration

### Priority Share List (19 files - All Sept 25-30, 2025):
1. **`biosample-flattening-timeline-2020-2025.md`** ⭐ **MUST INCLUDE** - Canonical comprehensive reference
2. **`CLAUDE.md`** - Project conventions (note: may need updating)
3. All 17 files from September 26-30 section above

### Review Before Sharing:
- `claude-mds/` files - Verify technical details are current (5-6 months old)
- Explicitly mark as "historical context" if including

### Exclude or Mark as Historical:
- `unorganized/` directory - Directory name indicates potentially outdated
- Files older than Aug 2024 unless specifically relevant

---

## Git Commands for Deeper Analysis

### Check File Modification Patterns:
```bash
# Show line-by-line last modification dates
git blame filename.md

# Show when specific sections changed
git log -p -- filename.md

# Show frequency of dates in file history
git blame filename.md | awk '{print $3}' | sort | uniq -c | sort -rn
```

### Verify Section Freshness:
```bash
# Check when CLAUDE.md sections were last updated
git log --all --full-history -p -- CLAUDE.md | less
```

---

**Report End** | Total files analyzed: 50 | Recommendation: Prioritize Sept 25-30 files for maximum reliability
