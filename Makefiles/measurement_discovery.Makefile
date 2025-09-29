RUN = poetry run
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: count-biosamples-per-harmonized-name count-biosamples-step1 count-bioprojects-step2 merge-counts-step3 \
index-harmonized-name-counts count-biosamples-and-bioprojects-per-harmonized-name count-unit-assertions count-mixed-content \
count-measurement-evidence calculate-measurement-ratios prioritize-targets process-priority-measurements export-flat-measurements clean-discovery \
rank-measurement-attributes rank-unified-measurement-attributes

# Phase 0: Baseline counting

# Count biosamples per harmonized_name (foundation for all measurement discovery)
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

# Analyze NMDC schema slot_usage statements with range assertions
analyze-nmdc-slot-usage:
	@date
	@echo "Analyzing NMDC schema slot_usage statements..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/analyze_nmdc_slot_usage.js \
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

# Comprehensive ranking of measurement-like attributes across all sources
rank-measurement-attributes:
	@date
	@echo "Ranking measurement attributes across NCBI, MIxS, and NMDC sources..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/rank_measurement_attributes.js \
		--verbose
	@date

# Unified ranking that consolidates same attributes across sources  
rank-unified-measurement-attributes:
	@date
	@echo "Creating unified measurement attribute rankings (consolidating overlaps)..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/rank_unified_measurement_attributes.js \
		--verbose
	@date

# Phase 2: Target prioritization from file checkpoints → priority list
prioritize-targets: local/priority_measurement_fields.json

local/priority_measurement_fields.json: local/measurement_fields_with_units.json local/numeric_content_fields.json
	@date
	@echo "Prioritizing measurement targets from discovery checkpoints..."
	$(RUN) prioritize-measurement-targets \
		--units-file local/measurement_fields_with_units.json \
		--numeric-file local/numeric_content_fields.json \
		--output-file $@ \
		--min-count 100 \
		--verbose
	@date

# Phase 3: Process priority measurements with unit correction
process-priority-measurements: local/priority_measurement_fields.json
	@date
	@echo "Processing priority measurement fields with unit correction..."
	$(RUN) normalize-biosample-measurements \
		--mongodb-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--input-collection biosamples_flattened \
		--output-collection biosamples_measurements \
		$(shell jq -r '.[].harmonized_name' local/priority_measurement_fields.json | sed 's/^/--field /' | tr '\n' ' ') \
		--overwrite
	@date

# Phase 4: Export flat measurement tuples
export-flat-measurements: local/flat_measurements.tsv

local/flat_measurements.tsv:
	@date
	@echo "Exporting flat measurement tuples..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/export_flat_measurements.js \
		--verbose
	@echo "Exporting to TSV checkpoint..."
	mongosh "$(MONGO_URI)" \
		--eval 'db.flat_measurements.find({}, {_id: 0}).forEach(doc => print([doc.biosample_id, doc.harmonized_name, doc.value, doc.unit].join("\t")))' \
		> $@
	@date

# Complete pipeline
measurement-pipeline: discover-measurement-fields discover-numeric-fields prioritize-targets process-priority-measurements export-flat-measurements
	@echo "✅ Complete measurement discovery pipeline completed"
	@echo "📊 Checkpoints saved:"
	@echo "   - local/measurement_fields_with_units.json"
	@echo "   - local/numeric_content_fields.json" 
	@echo "   - local/priority_measurement_fields.json"
	@echo "   - local/flat_measurements.tsv"

# Cleanup
clean-discovery:
	@echo "Cleaning all measurement/unit discovery files and collections..."
	@echo "Removing local checkpoint files..."
	rm -f local/measurement_fields_with_units.json
	rm -f local/numeric_content_fields.json
	rm -f local/priority_measurement_fields.json
	rm -f local/flat_measurements.tsv
	@echo "Dropping MongoDB collections (preserving beneficial indexes)..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--command "db.measurement_fields_with_units.drop(); db.numeric_content_fields.drop(); db.flat_measurements.drop(); db.biosamples_measurements.drop()"
	@echo "Note: Preserving indexes on biosamples_flattened and biosamples_attributes collections"
	@echo "✅ Cleanup complete - ready for fresh pipeline execution"