# MongoDB Collection Creation Scripts

Based on the missing collections, here are the scripts you should run to create them, in a logical sequence:

1. First, flatten biosample measurements:
   ```
   mongo-js/flatten_biosamples_measurements.js
   ```
   This will create the `biosamples_measurements_flattened` collection.

2. Generate attribute name counts:
   ```
   mongo-js/count_harmonizable_biosample_attribs.js
   ```
   This should create the `biosamples_attribute_name_counts_flat_gt_1` collection.

3. Create env triad component prefixes:
   ```
   mongo-js/count_env_triad_components_prefixes_lc.js
   ```
   This should generate the `biosamples_env_triad_components_prefix_lc_counts` collection.

4. Create in-scope CURIEs:
   ```
   mongo-js/count_env_triad_in_scope_prefixes_lc.js
   ```
   This will create the `env_triad_component_in_scope_curies_lc` collection.

5. Generate measurement evidence:
   ```
   mongo-js/measurement_evidence_by_harmonized_name.js
   ```
   This creates the `measurement_evidence_by_harmonized_name` collection.

6. Create unit counts by harmonized names:
   ```
   mongo-js/measurements_inferred_units_counts_by_harmonized_names.js
   ```
   This generates the `measurements_inferred_units_counts_by_harmonized_names` collection.

7. Finally, create inferred units totals:
   ```
   mongo-js/measurements_inferred_units_totals.js
   ```
   This will create the `measurements_inferred_units_totals` collection.

You can run these scripts using the mongo-js-executor from your Makefile:

```bash
poetry run mongo-js-executor --mongo-uri "mongodb://localhost:27017/ncbi_metadata" --js-file mongo-js/script_name.js --verbose
```

Or via the mongosh shell directly:

```bash
mongosh "mongodb://localhost:27017/ncbi_metadata" --file mongo-js/script_name.js
```

These scripts should be run in this specific order because some later scripts may depend on the collections created by earlier ones.

## Missing Collections Summary

Collection name | Status
--- | ---
env_triad_component_in_scope_curies_lc | ❌ Missing
measurements_inferred_units_totals | ❌ Missing
measurements_inferred_units_counts_by_harmonized_names | ❌ Missing
biosamples_measurements_flattened | ❌ Missing
biosamples_attribute_name_counts_flat_gt_1 | ❌ Missing
biosamples_env_triad_components_prefix_lc_counts | ❌ Missing
measurement_evidence_by_harmonized_name | ❌ Missing