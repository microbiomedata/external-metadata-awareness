# Test Workflow Makefile
# Create, export, and restore biosample samples for testing
#
# Fully parameterized - no hardcoded ports or database names

# MongoDB connection parameters
MONGO_HOST ?= localhost
SOURCE_PORT ?= 27017
TARGET_PORT ?= 27018
SOURCE_DB ?= ncbi_metadata
TARGET_DB ?= ncbi_metadata_test

SOURCE_URI = mongodb://$(MONGO_HOST):$(SOURCE_PORT)/$(SOURCE_DB)
TARGET_URI = mongodb://$(MONGO_HOST):$(TARGET_PORT)/$(TARGET_DB)

# Override MONGO_URI for included Makefiles to use test database
MONGO_URI = $(TARGET_URI)

# Standard pattern for running JS
RUN = poetry run

# Optional environment file
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
else
  ENV_FILE_OPTION :=
endif

# Sample parameters
SAMPLE_PCT ?= 1
SAMPLE_COLLECTION ?= biosamples_sample_$(SAMPLE_PCT)pct

# Export/import file paths - override DUMP_DIR to change output location
DUMP_DIR ?= ./local/dumps/$(SOURCE_DB)
BSON_FILE ?= $(DUMP_DIR)/$(SAMPLE_COLLECTION).bson
JSON_FILE ?= $(DUMP_DIR)/$(SAMPLE_COLLECTION).json

# Include other Makefiles to reuse their targets
include Makefiles/ncbi_metadata.Makefile
include Makefiles/ncbi_schema.Makefile
include Makefiles/env_triads.Makefile
include Makefiles/measurement_discovery.Makefile
include Makefiles/sra_metadata.Makefile

.PHONY: help create-sample export-json export-bson load-json load-bson show-sample \
        load-biosamples-and-sra load-and-flatten-schema \
        run-full-workflow flatten-test-biosamples process-env-triads process-measurements

help:
	@echo "Test Workflow Makefile - Sample Creation & Management"
	@echo ""
	@echo "Current Configuration:"
	@echo "  SOURCE: $(SOURCE_URI)"
	@echo "  TARGET: $(TARGET_URI)"
	@echo "  SAMPLE: $(SAMPLE_PCT)% -> $(SAMPLE_COLLECTION)"
	@echo ""
	@echo "Targets:"
	@echo "  create-sample    Create $(SAMPLE_PCT)% random sample"
	@echo "  export-json      Export to JSON (slower restore)"
	@echo "  export-bson      Export to BSON (faster restore) ✓ RECOMMENDED"
	@echo "  load-json        Load JSON into biosamples"
	@echo "  load-bson        Load BSON into biosamples ✓ RECOMMENDED"
	@echo "  show-sample      Show sample info"

# Create random sample collection
create-sample:
	@echo "Creating $(SAMPLE_PCT)% sample in $(SOURCE_DB)..."
	@date
	SAMPLE_COLLECTION=$(SAMPLE_COLLECTION) \
	SAMPLE_PCT=$(SAMPLE_PCT) \
	SOURCE_DB=$(SOURCE_DB) \
	SOURCE_PORT=$(SOURCE_PORT) \
	$(RUN) mongo-js-executor \
	  --mongo-uri "$(SOURCE_URI)" \
	  $(ENV_FILE_OPTION) \
	  --js-file mongo-js/create_sample_with_metadata.js \
	  --verbose
	@date

# Export to JSON
export-json:
	@echo "Exporting to: $(JSON_FILE)"
	@mkdir -p $(DUMP_DIR)
	@mongoexport --uri="$(SOURCE_URI)" \
	  --collection="$(SAMPLE_COLLECTION)" \
	  --out="$(JSON_FILE)"
	@ls -lh "$(JSON_FILE)"

# Export to BSON (RECOMMENDED - faster, preserves types)
export-bson:
	@echo "Exporting sample and metadata..."
	@mkdir -p $(DUMP_DIR)
	@echo "  Exporting $(SAMPLE_COLLECTION)..."
	@mongodump --uri="$(SOURCE_URI)" \
	  --collection="$(SAMPLE_COLLECTION)" \
	  --out="$(DUMP_DIR)"
	@echo "  Exporting notes..."
	@mongodump --uri="$(SOURCE_URI)" \
	  --collection="notes" \
	  --out="$(DUMP_DIR)"
	@echo ""
	@echo "Exported to: $(DUMP_DIR)/$(SOURCE_DB)/"
	@ls -lh "$(DUMP_DIR)/$(SOURCE_DB)/"*.bson

# Load JSON into target biosamples collection
load-json:
	@echo "Loading $(JSON_FILE) -> $(TARGET_URI)/biosamples"
	@mongoimport --uri="$(TARGET_URI)" \
	  --collection=biosamples \
	  --file="$(JSON_FILE)" \
	  --drop
	@mongosh "$(TARGET_URI)" --quiet --eval "print('✓ Loaded', db.biosamples.countDocuments(), 'documents')"

# Load BSON into target biosamples collection (RECOMMENDED)
load-bson:
	@echo "Loading $(BSON_FILE) -> $(TARGET_URI)/biosamples"
	@mongorestore --uri="$(TARGET_URI)" \
	  --collection=biosamples \
	  --drop \
	  "$(BSON_FILE)"
	@mongosh "$(TARGET_URI)" --quiet --eval "print('✓ Loaded', db.biosamples.countDocuments(), 'documents')"

# Show sample collection info
show-sample:
	@echo "Collection: $(SAMPLE_COLLECTION)"
	@mongosh "$(SOURCE_URI)" --quiet --eval \
	  "if (db.$(SAMPLE_COLLECTION).findOne()) { \
	    print('Documents:', db.$(SAMPLE_COLLECTION).countDocuments()); \
	    print('Size:', (db.$(SAMPLE_COLLECTION).stats().size / 1024 / 1024).toFixed(2), 'MB'); \
	  } else { print('Not found'); }"

# ==============================================================================
# Data Loading Targets - Load source data needed for test workflow
# ==============================================================================

# Load biosample sample from BSON export
load-biosample-sample:
	@echo "Loading biosample sample from BSON..."
	make -f Makefiles/test_workflow.Makefile load-bson \
	  BSON_FILE=local/dumps/ncbi_metadata/ncbi_biosamples_20251008_1pct.bson
	@echo "✓ Biosample sample loaded (490K biosamples)"

# Load SRA linkages from existing TSV (skip BigQuery re-export)
load-sra-linkages:
	@if [ ! -f downloads/sra_accession_pairs.tsv ]; then \
	  echo "ERROR: downloads/sra_accession_pairs.tsv not found"; \
	  echo "Run: make -f Makefiles/sra_metadata.Makefile sra_accession_pairs_tsv_to_mongo"; \
	  exit 1; \
	fi
	@echo "Loading SRA linkages from existing TSV (skipping BigQuery export)..."
	$(RUN) sra-accession-pairs-to-mongo \
	  --file-path downloads/sra_accession_pairs.tsv \
	  --mongo-uri "$(TARGET_URI)" \
	  --collection sra_biosamples_bioprojects \
	  --batch-size 100000 \
	  --report-interval 500000
	@echo "Creating indexes on sra_biosamples_bioprojects..."
	@mongosh "$(TARGET_URI)" --quiet --eval "\
	  print('Creating biosample_accession index...'); \
	  db.sra_biosamples_bioprojects.createIndex({biosample_accession: 1}, {background: true}); \
	  print('Creating bioproject_accession index...'); \
	  db.sra_biosamples_bioprojects.createIndex({bioproject_accession: 1}, {background: true}); \
	  print('✓ Indexes created');"
	@echo "✓ SRA biosample-bioproject linkages loaded (~32M pairs)"

# Load biosamples and SRA linkages (the two main source datasets)
load-biosamples-and-sra: load-biosample-sample load-sra-linkages
	@echo ""
	@echo "✓ Biosamples and SRA linkages loaded"
	@echo "  - biosamples: 490K"
	@echo "  - sra_biosamples_bioprojects: ~32M"

# Load and flatten NCBI schema collections (attributes and packages)
load-and-flatten-schema: downloads/ncbi-biosample-attributes.xml downloads/ncbi-biosample-packages.xml
	@echo "Loading NCBI attributes and packages into MongoDB..."
	@$(MAKE) -f Makefiles/ncbi_schema.Makefile load-attributes-into-mongo MONGO_URI="$(MONGO_URI)"
	@$(MAKE) -f Makefiles/ncbi_schema.Makefile load-packages-into-mongo MONGO_URI="$(MONGO_URI)"
	@echo "Flattening attributes and packages collections..."
	@$(MAKE) -f Makefiles/ncbi_schema.Makefile flatten-attributes-collection MONGO_URI="$(MONGO_URI)"
	@$(MAKE) -f Makefiles/ncbi_schema.Makefile flatten-packages-collection MONGO_URI="$(MONGO_URI)"
	@echo "✓ NCBI schema collections loaded and flattened"
	@echo "  - attributes + ncbi_attributes_flattened"
	@echo "  - packages + ncbi_packages_flattened"

# ==============================================================================
# Full Workflow Targets - Process Test Data Through Complete Pipeline
# ==============================================================================

# Run complete test workflow on test database
# Prerequisites: load-biosamples-and-sra must be run first
# Uses targets from included Makefiles with MONGO_URI pointing to test DB
run-full-workflow: load-and-flatten-schema flatten-test-biosamples process-env-triads process-measurements
	@echo ""
	@echo "=== Test Workflow Complete ==="
	@echo "Collections created in $(TARGET_DB):"
	@mongosh "$(TARGET_URI)" --quiet --eval \
	  "db.getCollectionNames().sort().forEach(c => { \
	    var count = db.getCollection(c).countDocuments(); \
	    print('  ' + c + ': ' + count); \
	  })" 
# Step 1: Flatten biosamples (reuses targets from ncbi_metadata.Makefile)
flatten-test-biosamples: flatten_biosample_attributes flatten_biosamples_ids flatten_biosamples_links aggregate-biosample-package-usage
	@echo "✓ Biosample flattening complete"

# Step 2: Process environmental triads with full annotation pipeline (reuses targets from env_triads.Makefile)
# This includes OAK, OLS, and BioPortal annotation - requires API key and cache
process-env-triads: biosamples-flattened env-triad-value-counts split-env-triad-values env-triads-flattened count-harmonizable-attribs
	@echo "✓ Environmental triads processing complete (with OAK/OLS/BioPortal annotation)"

# Step 3: Run measurement discovery and stats (reuses targets from measurement_discovery.Makefile)
# Order optimized: prospective collections (before quantulum3) → run-measurement-discovery → retrospective collections
process-measurements: count-unit-assertions count-mixed-content count-biosamples-and-bioprojects-per-harmonized-name calculate-measurement-percentages run-measurement-discovery create-dimensional-stats count-attribute-harmonized-pairings count-biosamples-per-harmonized-name-atomic load-global-mixs-slots load-global-nmdc-slots report-nmdc-range-slot-usage
	@echo "✓ Measurement discovery complete"

