RUN = poetry run
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: count-biosamples-per-harmonized-name count-biosamples-step1 count-bioprojects-step2 merge-counts-step3 \
index-harmonized-name-counts count-biosamples-and-bioprojects-per-harmonized-name count-unit-assertions count-mixed-content \
count-measurement-evidence clean-discovery

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
	mongosh "$(MONGO_URI)" --eval "db.__tmp_hn_counts.drop(); db.__tmp_hn_totals.drop(); print('Dropped __tmp_hn_counts and __tmp_hn_totals');"

# Meta-target: Run all steps in sequence
count-biosamples-per-harmonized-name-atomic: count-biosamples-per-hn-step1 count-biosamples-per-hn-step2 count-biosamples-per-hn-step3
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

# Step 1: Count unique biosamples per harmonized_name
count-biosamples-step1:
	@date
	@echo "Step 1: Creating indexes and counting unique biosamples per harmonized_name..."
	mongosh "$(MONGO_URI)" --eval "\
		print('[' + new Date().toISOString() + '] Ensuring beneficial indexes exist for Step 1'); \
		try { db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('harmonized_name index exists: ' + e.message); } \
		try { db.biosamples_attributes.createIndex({accession: 1}, {background: true}); } catch(e) { print('accession index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Dropping temp collections'); \
		db.temp_biosample_counts.drop(); \
		print('[' + new Date().toISOString() + '] Starting biosample counts aggregation'); \
		db.biosamples_attributes.aggregate([ \
			{ \$$group: { _id: '\$$harmonized_name', unique_biosamples: { \$$addToSet: '\$$accession' } } }, \
			{ \$$project: { harmonized_name: '\$$_id', unique_biosamples_count: { \$$size: '\$$unique_biosamples' }, _id: 0 } }, \
			{ \$$out: 'temp_biosample_counts' } \
		], { allowDiskUse: true }); \
		print('[' + new Date().toISOString() + '] Created ' + db.temp_biosample_counts.countDocuments() + ' biosample counts');"
	@date

# Step 2: Count unique bioprojects per harmonized_name  
count-bioprojects-step2:
	@date
	@echo "Step 2: Creating critical index and counting unique bioprojects per harmonized_name..."
	mongosh "$(MONGO_URI)" --eval "\
		print('[' + new Date().toISOString() + '] Ensuring critical index exists for lookup join'); \
		try { db.sra_biosamples_bioprojects.createIndex({biosample_accession: 1}, {background: true}); } catch(e) { print('Index already exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Dropping temp bioproject collection'); \
		db.temp_bioproject_counts.drop(); \
		print('[' + new Date().toISOString() + '] Starting bioproject counts aggregation'); \
		db.biosamples_attributes.aggregate([ \
			{ \$$group: { _id: '\$$harmonized_name', unique_biosamples: { \$$addToSet: '\$$accession' } } }, \
			{ \$$unwind: '\$$unique_biosamples' }, \
			{ \$$lookup: { from: 'sra_biosamples_bioprojects', localField: 'unique_biosamples', foreignField: 'biosample_accession', as: 'bioproject_info' } }, \
			{ \$$unwind: { path: '\$$bioproject_info', preserveNullAndEmptyArrays: false } }, \
			{ \$$group: { _id: '\$$_id', unique_bioprojects: { \$$addToSet: '\$$bioproject_info.bioproject_accession' } } }, \
			{ \$$project: { harmonized_name: '\$$_id', unique_bioprojects_count: { \$$size: '\$$unique_bioprojects' }, _id: 0 } }, \
			{ \$$out: 'temp_bioproject_counts' } \
		], { allowDiskUse: true }); \
		print('[' + new Date().toISOString() + '] Created ' + db.temp_bioproject_counts.countDocuments() + ' bioproject counts');"
	@date

# Step 3: Merge biosample and bioproject counts
merge-counts-step3:
	@date
	@echo "Step 3: Creating final index and merging biosample and bioproject counts..."
	mongosh "$(MONGO_URI)" --eval "\
		print('[' + new Date().toISOString() + '] Ensuring indexes exist before merge'); \
		try { db.temp_bioproject_counts.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('temp index exists: ' + e.message); } \
		try { db.temp_biosample_counts.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('biosample temp index exists: ' + e.message); } \
		print('[' + new Date().toISOString() + '] Dropping final collection'); \
		db.harmonized_name_counts.drop(); \
		print('[' + new Date().toISOString() + '] Merging counts'); \
		db.temp_biosample_counts.aggregate([ \
			{ \$$lookup: { from: 'temp_bioproject_counts', localField: 'harmonized_name', foreignField: 'harmonized_name', as: 'bioproject_data' } }, \
			{ \$$project: { harmonized_name: 1, unique_biosamples_count: 1, unique_bioprojects_count: { \$$ifNull: [{ \$$arrayElemAt: ['\$$bioproject_data.unique_bioprojects_count', 0] }, 0] } } }, \
			{ \$$sort: { unique_biosamples_count: -1 } }, \
			{ \$$out: 'harmonized_name_counts' } \
		], { allowDiskUse: true }); \
		print('[' + new Date().toISOString() + '] Created ' + db.harmonized_name_counts.countDocuments() + ' final stats'); \
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