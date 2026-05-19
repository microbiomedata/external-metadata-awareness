# Collection export rationale

For each MongoDB collection EMA can export to the DuckDB/Parquet lakehouse target, this doc names a consumer, a canonical query that consumer would actually run, and the reason the collection is worth shipping. Source of truth for the current export list: `Makefiles/ncbi_to_duckdb.Makefile :: FLAT_COLLECTIONS`.

The intent is to make the export decision *justifiable per collection*, not inherited from prior choices. If a collection here has no concrete consumer + query + reason, it shouldn't be in `FLAT_COLLECTIONS`.

Status legend:
- **export**: currently in `FLAT_COLLECTIONS`; justification below
- **candidate**: not currently exported; reviewing
- **internal**: keep loaded in Mongo, do not export

## Currently exported

### attribute_harmonized_pairings — export

- Consumer: schema-mapping analysts (you, NMDC submission-portal devs)
- Query: "For attribute `geographic location`, which `harmonized_name` values are actually used in NCBI? What's the count distribution?"
- Reason: lets a downstream tool map raw NCBI attribute strings to canonical harmonized_names without re-aggregating 800M rows.

### bioprojects_flattened — export

- Consumer: NMDC lakehouse, JGI Dremio cross-source joins
- Query: "Join biosamples to their parent BioProject on `project_accession`; filter by submission date range."
- Reason: the only flat representation of BioProject metadata. Cross-source joins need it.

### biosamples_attributes — export

- Consumer: NMDC K-BERDL parity ingest, measurement analysts, value-set curators
- Query: "Distinct values of `content` for `harmonized_name = 'env_medium'`, ranked by frequency."
- Reason: the long-format attribute table is the substrate everything else aggregates from. 812M rows; consumers need it pre-flattened, not re-derived.

### biosamples_flattened — export

- Consumer: NMDC lakehouse, biosample-level analysts
- Query: "Filter biosamples by collection_date / lat_lon / env_broad_scale; export the resulting accession list."
- Reason: one row per biosample with the most-queried fields surfaced (env triad, dates, location). Without it, every consumer redoes the same flatten.

### biosamples_ids — export

- Consumer: cross-source id-resolution (NMDC ↔ NCBI ↔ submitter aliases)
- Query: "Given submitter sample name X, find the NCBI accession."
- Reason: the only flat crosswalk of NCBI accession to alternate identifiers.

### biosamples_links — export

- Consumer: cross-source ID linkage (publication-to-sample, accession-to-URL)
- Query: "All biosamples linked to PMID 12345" / "All biosamples with a SRA run link."
- Reason: linking table for any external-resource enrichment.

### content_pairs_aggregated — export

- Consumer: NMDC K-BERDL parity (#405), measurement curation, value-set design
- Query: "All distinct `content` values for `harmonized_name = 'depth'` with biosample counts."
- Reason: deduplicates 712M rows to ~64M unique pairs. K-BERDL parity gap (#405) is the immediate driver; downstream curation needs the dedup to be cheap.

### env_triads_flattened — export

- Consumer: env-triad value-set development, NMDC lakehouse env-triad analytics, agentic ingest consumers (Sujay's `nmdc-ingest-agent` may read this for known resolutions; see #426 for a leaner sibling)
- Query: "All resolved CURIEs for env_medium component label `soil`, with source and ontology."
- Reason: the resolvable side of the env-triad pipeline; flat shape lets it be joined to biosample queries.

### harmonized_name_dimensional_stats — export

- Consumer: measurement curators, schema designers (you)
- Query: "What dimensional patterns (length, mass, etc.) does `harmonized_name = 'depth'` exhibit across NCBI?"
- Reason: small summary table; used for picking what to model in measurement work and for catching dimensional drift.

### harmonized_name_usage_stats — export

- Consumer: anyone deciding what to prioritize for harmonization, modeling, or curation
- Query: "Top 100 harmonized_names by unique_biosamples_count" / "Is this rare attribute used in any project?"
- Reason: the prevalence signal for every harmonized_name across both biosamples and bioprojects.

### measurement_evidence_percentages — export

- Consumer: measurement curators, slot prioritization
- Query: "Which harmonized_names have ≥X% unit-bearing values and ≥Y% mixed-content (numeric+text) prevalence?"
- Reason: the precomputed ratios that drive measurement-target selection.

### measurement_results_skip_filtered — export

- Consumer: measurement consumers (NMDC lakehouse, dimensional analysis)
- Query: "All parsed measurements for `depth` with their value, unit, and original_content."
- Reason: this is the value-add of the 4-8 hour quantulum3 pass. Currently has the "crazy units" problem (#363); export keeps the raw and parsed both so downstream can re-canonicalize.

### mixed_content_counts — export

- Consumer: measurement curators
- Query: "Which harmonized_names most frequently have alphanumeric content (likely value+unit)?"
- Reason: one of the signals feeding `measurement_evidence_percentages`. Cheap to keep around for ad-hoc analysis.

### ncbi_attributes_flattened — export

- Consumer: anyone interpreting harmonized_name semantics
- Query: "What is the NCBI-stated definition and synonym list for `harmonized_name = 'geo_loc_name'`?"
- Reason: the canonical NCBI attribute dictionary, flat. Reference data for downstream tools.

### ncbi_packages_flattened — export

- Consumer: voting-sheet workflow, NMDC submission-portal schema designers
- Query: "Which attributes are required by the `MIMS.me.soil` package?"
- Reason: package-to-attribute crosswalk; required for any "what should this submission contain?" question.

### sra_biosamples_bioprojects — export

- Consumer: NMDC lakehouse, JGI Dremio, anyone joining sequencing data to sample metadata
- Query: "Given BioSample accession X, list all SRA runs and their parent BioProjects."
- Reason: the cross-DB derive (PR #400) is the join key for sequencing-aware analytics.

### unit_assertion_counts — export

- Consumer: measurement curators, UCUM mapping work (#363)
- Query: "For `harmonized_name = 'depth'`, what unit strings have been asserted and how often?"
- Reason: the unit-frequency signal used both for picking measurement targets and for building UCUM mappings.

## Candidates not currently exported

### harmonized_name_biosample_counts — candidate

- Consumer: same as `measurement_evidence_percentages`, but at a finer grain
- Query: "Which harmonized_names have ≥X% `unit_coverage_percent` AND high `biosample_count`?"
- Reason to add: distinct fields from `harmonized_name_usage_stats` (carries the unit-coverage signal, which usage_stats does not). #274 (closed 2026-05-19) addressed the naming ambiguity. **Decision: probably export; collapses one consumer query that today needs to scan attributes.**

### global_mixs_slots, global_nmdc_slots — internal

- Consumer: dimensional validation, hybrid measurement-target selection (issue: TBD), measurement-record processing
- Query: "What's the range type and preferred units for MIxS slot `depth`?"
- Reason **not** to export: the upstream YAML is the source of truth and consumers should fetch from there; EMA uses these collections at processing time, but downstream consumers of the lakehouse shouldn't need them.
- Decision: keep loaded, don't export.

### bioprojects_submissions — internal

- Consumer: none currently
- Query: none
- Reason **not** to export: orphaned since load. Carries submission envelope (submitter, status, date). Keep loaded with minimal indexing per the in-conversation decision; revisit if a freshness-diff use case (#367) needs it.
- Decision: keep loaded, do not export.

## Open questions to resolve

1. **What gets `harmonized_name_biosample_counts` into FLAT_COLLECTIONS, and what gets the rename from #274 propagated through?** Both are blocked on #388 (naming umbrella).
2. **Is there a real external consumer for `sra_biosamples_bioprojects` in BERDL today, or is it speculative?** The cross-DB derive is recent (PR #400); we should verify consumer.
3. **For each "NMDC lakehouse" consumer claim above, which collections does BERDL actually ingest today vs aspirationally?** This doc is honest where we know; speculative where we don't. Verifying with the BERDL ingest config would tighten the rationale.
4. **Should `env_triads_flattened` keep its current shape or be reshaped per #426 (the deterministic CURIE lookup table for agent consumers)?** Different consumer profile.
