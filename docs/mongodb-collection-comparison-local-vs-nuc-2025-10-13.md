# MongoDB Collection Comparison: Local vs NUC (192.168.0.204)

**Date**: 2025-10-13
**Database**: ncbi_metadata
**Local intent**: Subset of biosamples with non-null, non-empty values for: collection_date, lat_lon, env_broad_scale, env_local_scale, env_medium

---

## Collections ONLY on LOCAL (1 collection)

| Collection | Count |
|------------|-------|
| harmonized_name_dimensional_stats | 432 |

**Note**: Orphaned collection with no generation code

---

## Collections ONLY on NUC (6 collections)

| Collection | Count |
|------------|-------|
| bioprojects | 970,757 |
| bioprojects_flattened | 970,757 |
| bioprojects_submissions | 970,757 |
| biosample_package_usage | 210 |
| biosamples_attribute_name_counts_flat_gt_1 | 2,453 |
| harmonized_name_biosample_counts | 791 |

**Note**: harmonized_name_biosample_counts is the newly created collection with fixed unit coverage calculation

---

## Collections on BOTH - Document Count Comparison

| Collection | Local Count | NUC Count | Difference | Ratio |
|------------|-------------|-----------|------------|-------|
| attribute_harmonized_pairings | 20,937 | 92,752 | +71,815 | 4.43x |
| attributes | 960 | 960 | 0 | 1.00x |
| biosamples | 3,037,277 | 49,049,009 | +46,011,732 | 16.15x |
| biosamples_attributes | 52,518,729 | 712,619,063 | +660,100,334 | 13.57x |
| biosamples_env_triad_value_counts_gt_1 | 49,329 | 71,197 | +21,868 | 1.44x |
| biosamples_flattened | 3,037,277 | 41,979,384 | +38,942,107 | 13.82x |
| biosamples_ids | 7,871,449 | 121,607,068 | +113,735,619 | 15.45x |
| biosamples_links | 2,335,376 | 29,078,454 | +26,743,078 | 12.45x |
| content_pairs_aggregated | 2,331,732 | 63,999,329 | +61,667,597 | 27.45x |
| env_triad_component_curies_uc | 4,549 | 5,899 | +1,350 | 1.30x |
| env_triad_component_labels | 35,141 | 52,067 | +16,926 | 1.48x |
| env_triads | 3,037,277 | 6,264,662 | +3,227,385 | 2.06x |
| env_triads_flattened | 9,262,719 | 17,034,191 | +7,771,472 | 1.84x |
| global_mixs_slots | 772 | 772 | 0 | 1.00x |
| global_nmdc_slots | 841 | 847 | +6 | 1.01x |
| harmonized_name_usage_stats | 695 | 791 | +96 | 1.14x |
| measurement_evidence_percentages | 695 | 792 | +97 | 1.14x |
| measurement_results_skip_filtered | 87,466 | 1,322,161 | +1,234,695 | 15.12x |
| mixed_content_counts | 440 | 588 | +148 | 1.34x |
| ncbi_attributes_flattened | 960 | 960 | 0 | 1.00x |
| ncbi_packages_flattened | 229 | 229 | 0 | 1.00x |
| nmdc_range_slot_usage_report | 44 | 45 | +1 | 1.02x |
| packages | 229 | 229 | 0 | 1.00x |
| sra_biosamples_bioprojects | 31,809,491 | 31,809,491 | 0 | 1.00x |
| unit_assertion_counts | 13 | 404 | +391 | 31.08x |

---

## Key Observations

### Dataset Size
- **Local**: ~3M biosamples (subset with complete environmental metadata)
- **NUC**: ~49M biosamples (full NCBI dataset, 16x larger)

### Collections with Massive Differences (10x+ larger on NUC)
- biosamples: 16.15x
- biosamples_attributes: 13.57x
- biosamples_flattened: 13.82x
- biosamples_ids: 15.45x
- biosamples_links: 12.45x
- content_pairs_aggregated: 27.45x
- measurement_results_skip_filtered: 15.12x
- unit_assertion_counts: 31.08x

### Environmental Triad Collections (Moderate Differences)
- env_triads: 2.06x
- env_triads_flattened: 1.84x
- env_triad_component_labels: 1.48x
- biosamples_env_triad_value_counts_gt_1: 1.44x

**Note**: Environmental triad collections show smaller ratios (~1.4-2x) because the NUC dataset includes more biosamples but many lack complete environmental metadata

### Identical Collections (Reference Data)
- sra_biosamples_bioprojects: 31.8M (same on both)
- attributes: 960 (metadata definitions)
- packages: 229 (package definitions)
- ncbi_attributes_flattened: 960
- ncbi_packages_flattened: 229
- global_mixs_slots: 772

---

## Local Subset Criteria

Local database should contain only biosamples where ALL of the following harmonized_names have non-null, non-empty content:
1. collection_date
2. lat_lon
3. env_broad_scale
4. env_local_scale
5. env_medium

This explains why local has ~3M biosamples vs NUC's 49M (6.2% of total dataset meets all criteria).
