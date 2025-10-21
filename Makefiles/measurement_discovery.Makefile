RUN = poetry run
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: count-biosamples-per-harmonized-name count-biosamples-step1 count-bioprojects-step2 \
count-bioprojects-step2a count-bioprojects-step2b count-bioprojects-step2c count-bioprojects-step2d \
merge-counts-step3 index-harmonized-name-counts count-biosamples-and-bioprojects-per-harmonized-name \
count-unit-assertions count-mixed-content count-measurement-evidence run-measurement-discovery \
create-dimensional-stats clean-discovery

# Phase 0: Baseline counting

# Atomic, resumable biosample counting (Issue #237)
# Each step checks if output exists and skips if already done

count-biosamples-per-hn-step1:
	@echo "Step 1: Counting biosamples per harmonized_name (dedupe)..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_biosamples_per_hn_step1.js \
		--verbose
	@date

count-biosamples-per-hn-step2:
	@echo "Step 2: Counting totals and unit coverage per harmonized_name..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_biosamples_per_hn_step2.js \
		--verbose
	@date

count-biosamples-per-hn-step3:
	@echo "Step 3: Joining temp tables and creating final collection..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_biosamples_per_hn_step3.js \
		--verbose
	@date

count-biosamples-per-hn-cleanup:
	@echo "Cleaning up temp collections..."
	mongosh "$(MONGO_URI)" --eval "db.getCollection('__tmp_hn_counts').drop(); db.getCollection('__tmp_hn_totals').drop(); print('Dropped __tmp_hn_counts and __tmp_hn_totals');"

# Meta-target: Run all steps in sequence
count-biosamples-per-harmonized-name-atomic: count-biosamples-per-hn-step1 count-biosamples-per-hn-step2 count-biosamples-per-hn-step3
	@$(MAKE) -f Makefiles/measurement_discovery.Makefile count-biosamples-per-hn-cleanup MONGO_URI="$(MONGO_URI)"
	@echo "✅ Biosample counting complete (atomic steps)"

# Original monolithic target (deprecated - prefer atomic version above)
count-biosamples-per-harmonized-name:
	@date
	@echo "Counting biosamples per harmonized_name..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_biosamples_per_harmonized_name.js \
		--verbose
	@date

# Step 1: Count unique biosamples per harmonized_name (uses JavaScript file to avoid $addToSet memory limit)
count-biosamples-step1:
	@date
	@echo "Step 1: Counting unique biosamples per harmonized_name..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_biosamples_usage_stats_step1.js \
		--verbose
	@date

# Step 2: Count unique bioprojects per harmonized_name (atomic sub-steps for performance)

count-bioprojects-step2a:
	@echo "Step 2a: Deduplicating harmonized_name + accession pairs..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_bioprojects_step2a_dedupe_accessions.js \
		--verbose
	@date

count-bioprojects-step2b:
	@echo "Step 2b: Creating index on temp collection..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_bioprojects_step2b_index_temp.js \
		--verbose
	@date

count-bioprojects-step2c:
	@echo "Step 2c: Joining with SRA and counting bioprojects..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_bioprojects_step2c_sra_join.js \
		--verbose
	@date

count-bioprojects-step2d:
	@echo "Step 2d: Cleaning up intermediate collection..."
	@date
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_bioprojects_step2d_cleanup.js \
		--verbose
	@date

# Meta-target: Run all Step 2 sub-steps in sequence
count-bioprojects-step2: count-bioprojects-step2a count-bioprojects-step2b count-bioprojects-step2c count-bioprojects-step2d
	@echo "✅ Bioproject counting complete (atomic steps)"

# Step 3: Merge biosample and bioproject counts
merge-counts-step3:
	@date
	@echo "Step 3: Creating final index and merging biosample and bioproject counts..."
	mongosh "$(MONGO_URI)" --eval "\
		print('[' + new Date().toISOString() + '] Ensuring indexes exist before merge'); \
		try { db.temp_bioproject_counts.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('temp index exists: ' + e.message); } \
		try { db.temp_biosample_counts.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('biosample temp index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Dropping final collection'); \
		db.harmonized_name_usage_stats.drop(); \
		print('[' + new Date().toISOString() + '] Merging counts'); \
		db.temp_biosample_counts.aggregate([ \
			{ \$$lookup: { from: 'temp_bioproject_counts', localField: 'harmonized_name', foreignField: 'harmonized_name', as: 'bioproject_data' } }, \
			{ \$$project: { harmonized_name: 1, unique_biosamples_count: 1, unique_bioprojects_count: { \$$ifNull: [{ \$$arrayElemAt: ['\$$bioproject_data.unique_bioprojects_count', 0] }, 0] } } }, \
			{ \$$sort: { unique_biosamples_count: -1 } }, \
			{ \$$out: 'harmonized_name_usage_stats' } \
		], { allowDiskUse: true }); \
		print('[' + new Date().toISOString() + '] Created ' + db.harmonized_name_usage_stats.countDocuments() + ' final stats'); \
		db.temp_biosample_counts.drop(); \
		db.temp_bioproject_counts.drop(); \
		print('[' + new Date().toISOString() + '] Cleaned up temp collections');"
	@date

# Index harmonized_name_usage_stats for efficient querying of biosample/bioproject counts per field
index-harmonized-name-counts:
	@echo "Creating indexes on harmonized_name_usage_stats collection..."
	mongosh "$(MONGO_URI)" --eval "\
		print('[' + new Date().toISOString() + '] Creating index on harmonized_name'); \
		try { db.harmonized_name_usage_stats.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('harmonized_name index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Creating index on unique_biosamples_count'); \
		try { db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: 1}, {background: true}); } catch(e) { print('biosamples_count index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Creating index on unique_bioprojects_count'); \
		try { db.harmonized_name_usage_stats.createIndex({unique_bioprojects_count: 1}, {background: true}); } catch(e) { print('bioprojects_count index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Creating compound index for sorting/filtering'); \
		try { db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: -1, unique_bioprojects_count: -1}, {background: true}); } catch(e) { print('compound index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] All indexes created successfully');"

# Combined target: all three steps plus indexing
count-biosamples-and-bioprojects-per-harmonized-name: count-biosamples-step1 count-bioprojects-step2 merge-counts-step3 index-harmonized-name-counts
	@echo "✅ Complete harmonized_name counts created and indexed"

# Phase 1: Discovery with file checkpoints

# Count unit assertions (harmonized_name + unit combinations)
count-unit-assertions:
	@date
	@echo "Counting unit assertions..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_unit_assertions.js \
		--verbose
	@date

# Count mixed content (harmonized_name with letters and numbers)
count-mixed-content:
	@date
	@echo "Counting mixed content..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_mixed_content.js \
		--verbose
	@date

# Metatarget: Run both counting operations
count-measurement-evidence: count-unit-assertions count-mixed-content
	@echo "✅ Measurement evidence counting complete"
	@echo "📊 Created collections: unit_assertion_counts, mixed_content_counts"

# Run quantulum3 measurement discovery (creates measurement_results_skip_filtered + content_pairs_aggregated)
# FULL PRODUCTION RUN: Processes all 64M (harmonized_name, content) pairs
# Options explained:
#   --save-aggregation: Saves all 64M pairs to content_pairs_aggregated (adds ~10-15 min)
#   --clear-output: Drops measurement_results_skip_filtered before starting
#   --min-count 1: Process all content values (even if only 1 biosample has it)
#   --progress-every 100: Show detailed output every 100 quantulum3 parses
# Performance: Phase 1 (aggregation) ~30-40 min, Phase 2 (save) ~10-15 min, Phase 3 (quantulum3) ~4-8 hours
run-measurement-discovery:
	@date
	@echo "Running quantulum3 measurement discovery..."
	@echo "Skip list: 224 harmonized_names"
	@echo "Input: biosamples_attributes (712M records)"
	@echo "Output: measurement_results_skip_filtered + content_pairs_aggregated"
	@echo "Estimated time: 4-8 hours for full dataset"
	$(RUN) measurement-discovery-efficient \
		--mongo-uri "$(MONGO_URI)" \
		--save-aggregation \
		--clear-output \
		--min-count 1 \
		--progress-every 100
	@date
	@echo "✅ Quantulum3 parsing complete"
	@echo "📊 Check measurement_results_skip_filtered for parsed measurements"

# Quick test run to validate pipeline and memory handling
# Uses --limit to process only 50k pairs instead of 64M (~1-2 minutes total)
# Useful for: Testing after code changes, validating no OOM errors, CI/CD checks
test-measurement-discovery:
	@date
	@echo "Running QUICK TEST of measurement discovery pipeline..."
	@echo "Limiting to 50,000 pairs (instead of 64M) for fast validation"
	@echo "Estimated time: 1-2 minutes"
	$(RUN) measurement-discovery-efficient \
		--mongo-uri "$(MONGO_URI)" \
		--save-aggregation \
		--clear-output \
		--limit 50000 \
		--progress-every 100
	@date
	@echo "✅ Quick test complete - pipeline working correctly"

# Focus on common measurements only (faster than full run)
# Uses --min-count 10 to process only values appearing in 10+ biosamples
# Reduces dataset from 64M to ~20M pairs (~2-3 hours instead of 4-8)
run-measurement-discovery-common:
	@date
	@echo "Running measurement discovery for COMMON values only..."
	@echo "Min count: 10 biosamples (reduces ~64M pairs to ~20M)"
	@echo "Estimated time: 2-3 hours"
	$(RUN) measurement-discovery-efficient \
		--mongo-uri "$(MONGO_URI)" \
		--save-aggregation \
		--clear-output \
		--min-count 10 \
		--progress-every 100
	@date
	@echo "✅ Common measurements discovery complete"

# Calculate measurement evidence percentages by joining count collections
calculate-measurement-percentages:
	@date
	@echo "Calculating measurement evidence percentages..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/calculate_measurement_evidence_ratios.js \
		--verbose
	@date

# Count attribute_name + harmonized_name pairings
count-attribute-harmonized-pairings:
	@date
	@echo "Counting attribute_name + harmonized_name pairings..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_attribute_harmonized_pairings.js \
		--verbose
	@date

# Load global MIxS slot definitions into MongoDB
load-global-mixs-slots:
	@date
	@echo "Loading global MIxS slot definitions into MongoDB..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/load_global_mixs_slots.js \
		--verbose
	@date


# Generate detailed report of NMDC range slot_usage modifications
report-nmdc-range-slot-usage:
	@date
	@echo "Generating detailed NMDC range slot_usage report..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/report_nmdc_range_slot_usage.js \
		--verbose
	@date

# Load global NMDC slot definitions into MongoDB
load-global-nmdc-slots:
	@date
	@echo "Loading global NMDC slot definitions into MongoDB..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/load_global_nmdc_slots.js \
		--verbose
	@date

# Create harmonized_name_dimensional_stats from measurement results
# Requires: measurement_results_skip_filtered collection (from run-measurement-discovery)
# Produces: harmonized_name_dimensional_stats collection
# See Issue #275 for methodology and comparison with 3M DuckDB version
create-dimensional-stats:
	@date
	@echo "Creating harmonized_name_dimensional_stats from measurement results..."
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/create_harmonized_name_dimensional_stats.js \
		--verbose
	@date



# Cleanup
clean-discovery:
	@echo "Cleaning measurement discovery collections..."
	@echo "Dropping MongoDB collections (preserving beneficial indexes)..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--command "db.measurement_results_skip_filtered.drop(); db.content_pairs_aggregated.drop()"
	@echo "Note: Preserving indexes on biosamples_attributes collection"
	@echo "✅ Cleanup complete - ready for fresh measurement discovery execution"