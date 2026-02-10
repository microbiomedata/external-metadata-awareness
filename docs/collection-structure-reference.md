# Collection Structure Reference

Quick reference for every collection in the `ncbi_metadata` database. Describes nesting, sparsity, and field inventories.

Last verified: 2026-02-08 (51.7M biosamples, 1M bioprojects).

## Terminology

- **Flat**: All fields are scalar values (strings, numbers, booleans, dates). No embedded documents or arrays.
- **Nested/hierarchical**: Contains embedded documents or arrays of documents. Reflects XML or YAML source structure.
- **Sparse**: Not all documents in the collection have the same fields. Some fields appear only after enrichment or only for certain source records. MongoDB's flexible schema allows this — analogous to nullable columns in relational databases.
- **Mixed-structure**: Some documents are flat while others have nested fields, typically because an enrichment step adds arrays/objects to qualifying documents.

## Collections by Pipeline Stage

### Stage 1: Raw Source Data (nested, from XML)

| Collection | Structure | Docs | Notes |
|---|---|---|---|
| `biosamples` | **Nested** | 51.7M | 8 nested objects: Ids, Description, Owner, Models, Package, Attributes, Links, Status. Direct XML-to-MongoDB load. |
| `bioprojects` | **Nested** | 1M | 3 nested objects: ProjectID, ProjectDescr, ProjectType. |
| `bioprojects_submissions` | **Nested** | 1M | 2 nested objects + 1 array (bioproject_accessions). |

### Stage 2: SRA Linkage

| Collection | Structure | Docs | Notes |
|---|---|---|---|
| `sra_biosamples_bioprojects` | **Flat** | 33.7M | Fields: `biosample_accession`, `bioproject_accession`. |

### Stage 3: Flattened Biosamples

| Collection | Structure | Docs | Sparse? | Fields |
|---|---|---|---|---|
| `biosamples_flattened` | **Flat** | 51.7M | **Yes** — 39 possible fields, many null per doc | accession, id, submission_date, last_update, publication_date, access, package_content, status_status, status_when, is_reference, curation_date, curation_status, owner_abbreviation, owner_name, owner_url, description_title, organism_name, taxonomy_id, taxonomy_name, description_comment, plus attribute fields (collection_date, geo_loc_name, env_broad_scale, env_local_scale, env_medium, host, etc.) |
| `biosamples_attributes` | **Flat** | 756M | **Yes** — `harmonized_name`, `display_name`, `unit` not always present | biosample_id, accession, attribute_name, content, [harmonized_name], [display_name], [unit] |
| `biosamples_ids` | **Flat** | 128M | Minimal | biosample_id, accession, db, db_label, id_value |
| `biosamples_links` | **Flat** | 30.6M | Minimal | biosample_id, accession, type, label, target |
| `bioprojects_flattened` | **Flat** | 1M | No | 17 fields |

### Stage 4: NCBI Schema

| Collection | Structure | Docs | Sparse? | Fields |
|---|---|---|---|---|
| `attributes` | **Nested** | 960 | **Yes** | Raw XML load of NCBI biosample attribute definitions. Contains nested Name, Description, Format, Synonym, Package elements. |
| `packages` | **Nested** | 229 | **Yes** | Raw XML load of NCBI biosample package definitions. Contains nested Name, DisplayName, ShortName, Description, Attribute elements. |
| `ncbi_attributes_flattened` | **Flat** | 960 | Slightly — synonyms/packages may be empty | name, harmonized_name, description, format, synonyms (concatenated string), packages (concatenated string) |
| `ncbi_packages_flattened` | **Flat** | 229 | **Yes** — several fields optional | name, display_name, short_name, env_package, env_package_display, description, example, not_appropriate_for, group, antibiogram |

### Stage 5: Environmental Triads

| Collection | Structure | Docs | Sparse? | Notes |
|---|---|---|---|---|
| `biosamples_env_triad_value_counts_gt_1` | **Mixed-structure** | 82K | **Yes** | Base docs are flat (count, env_triad_value, length, envo_count, boolean flags). After enrichment, gains `components` array. |
| `env_triad_component_labels` | **Mixed-structure** | 60K | **Yes** | Base docs are flat (count, label_length, label_digits_only, label). Annotated docs gain `oak_text_annotations` (array of objects) and/or `ols_text_annotations` (array of objects). |
| `env_triad_component_curies_uc` | **Flat** | 6.9K | **Yes** — `label`, `obsolete` only on resolved CURIEs | count, uses_obo_prefix, uses_bioportal_prefix, prefix_uc, curie_uc, [label], [obsolete] |
| `env_triads` | **Nested** | 7.7M | No | accession, plus 3 nested objects: env_broad_scale, env_local_scale, env_medium (each containing annotation details). |
| `env_triads_flattened` | **Flat** | 20.7M | No | accession, attribute, instance, raw_original, raw_component, id, label, prefix, source (one row per component). |

### Stage 6: Measurement Discovery

| Collection | Structure | Docs | Sparse? | Fields |
|---|---|---|---|---|
| `unit_assertion_counts` | **Flat** | 230 | No | harmonized_name, unit, count |
| `mixed_content_counts` | **Flat** | 595 | No | harmonized_name, count |
| `content_pairs_aggregated` | **Flat** | 66.4M | No | harmonized_name, content, biosample_count |
| `measurement_results_skip_filtered` | **Flat** | 1.34M | No | harmonized_name, original_content, biosample_count, value, unit, entity, span_start, span_end, surface_text, coverage_pct, content_length |
| `attribute_harmonized_pairings` | **Flat** | 96K | No | attribute_name, harmonized_name, count |

### Stage 7: Statistics and Reports

| Collection | Structure | Docs | Sparse? | Fields |
|---|---|---|---|---|
| `harmonized_name_usage_stats` | **Flat** | 810 | No | harmonized_name, unique_biosamples_count, unique_bioprojects_count |
| `measurement_evidence_percentages` | **Flat** | 811 | No | harmonized_name, total_attributes, unique_biosamples_count, unique_bioprojects_count, attributes_with_units, unique_units_count, attributes_with_mixed_content, unit_assertion_percentage, mixed_content_percentage, avg_evidence_percentage |
| `harmonized_name_dimensional_stats` | **Flat** | 354 | No | harmonized_name, total_content_pairs, total_quantities_found, dimensional_quantities, dimensionless_quantities, unique_content_with_any_units, unique_content_with_dimensional_units, unique_units_total, unique_dimensional_units, content_extraction_rate_pct, dimensional_content_rate_pct, dimensional_of_extracted_pct |
| `global_mixs_slots` | **Nested** | 788 | **Yes** | slot_name + variable MIxS YAML properties (domain, range, unit, description, annotations [nested], minimum_value, maximum_value, etc.) |
| `global_nmdc_slots` | **Nested** | 846 | **Yes** | slot_name + variable NMDC YAML properties (domain, range, unit, description, slot_uri, annotations [nested], minimum_value, maximum_value, etc.) |
| `nmdc_range_slot_usage_report` | **Nested** | 55 | Slightly | slot_name, global_range, global_slot_uri, class_name, slot_usage_range, slot_usage_slot_uri, is_override, is_same_range, other_slot_usage_properties [nested object] |

## Summary

- **Naming convention**: Collections with `_flattened` in the name are always flat. But many flat collections don't have `_flattened` in the name.
- **Mixed-structure collections**: `biosamples_env_triad_value_counts_gt_1` and `env_triad_component_labels` start flat and gain nested arrays during enrichment.
- **Sparsity is common**: Even flat collections like `biosamples_attributes` and `biosamples_flattened` have documents with different field sets. This reflects the heterogeneity of NCBI biosample submissions.
- **Schema slot collections** (`global_mixs_slots`, `global_nmdc_slots`): Structure is inherited from source YAML and varies per slot definition.

## DuckDB / Parquet Export

17 flat collections (Stages 2-4, 6-7 above, plus `env_triads_flattened` and `bioprojects_flattened`) are exportable to DuckDB and Parquet via `ncbi_to_duckdb.Makefile`. Nested/mixed-structure collections (Stage 1, Stage 5 enriched collections, schema slot collections) are **not** exported — they require MongoDB's document model.

Exported flat collections: `attribute_harmonized_pairings`, `bioprojects_flattened`, `biosamples_attributes`, `biosamples_flattened`, `biosamples_ids`, `biosamples_links`, `content_pairs_aggregated`, `env_triads_flattened`, `harmonized_name_dimensional_stats`, `harmonized_name_usage_stats`, `measurement_evidence_percentages`, `measurement_results_skip_filtered`, `mixed_content_counts`, `ncbi_attributes_flattened`, `ncbi_packages_flattened`, `sra_biosamples_bioprojects`, `unit_assertion_counts`.

Export commands:
```bash
make -f Makefiles/ncbi_to_duckdb.Makefile export-all    # DuckDB + Parquet in one step
make -f Makefiles/ncbi_to_duckdb.Makefile make-database  # DuckDB only
make -f Makefiles/ncbi_to_duckdb.Makefile export-parquet # Parquet from existing DuckDB
```

Distribution: NERSC portal at `https://portal.nersc.gov/project/m3408/biosamples_duckdb/` hosts both monolithic DuckDB files and per-table Parquet files.

For full data product inventory with sizes, see `docs/data-products-inventory.md`.
