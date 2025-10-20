# NCBI MongoDB to DuckDB Migration Makefile
# Dumps 100% flat collections from ncbi_metadata MongoDB to DuckDB

# Default configuration - can be overridden at runtime
MONGO_HOST ?= localhost
MONGO_PORT ?= 27017
MONGO_DB ?= ncbi_metadata
MONGO_URI ?= mongodb://$(MONGO_HOST):$(MONGO_PORT)/$(MONGO_DB)

# BioProjects source database
BIOPROJECTS_DB ?= ncbi_metadata_20250919

# Output configuration
OUTPUT_DIR ?= ./local/ncbi_duckdb_export
DATE_STAMP := $(shell date +%Y%m%d)
# Dated files for archival
DUCKDB_FILE_DATED ?= $(OUTPUT_DIR)/ncbi_metadata_flat_$(DATE_STAMP).duckdb
BIOPROJECTS_DUCKDB_FILE_DATED ?= $(OUTPUT_DIR)/ncbi_bioprojects_$(DATE_STAMP).duckdb
# Symlinks to latest (avoids date rollover issues)
DUCKDB_FILE ?= $(OUTPUT_DIR)/ncbi_metadata_flat_latest.duckdb
BIOPROJECTS_DUCKDB_FILE ?= $(OUTPUT_DIR)/ncbi_bioprojects_latest.duckdb

# List of 100% flat collections (flatness_score = 100.0)
FLAT_COLLECTIONS := \
	attribute_harmonized_pairings \
	biosamples_attributes \
	biosamples_flattened \
	biosamples_ids \
	biosamples_links \
	content_pairs_aggregated \
	env_triads_flattened \
	harmonized_name_dimensional_stats \
	harmonized_name_usage_stats \
	measurement_evidence_percentages \
	measurement_results_skip_filtered \
	mixed_content_counts \
	ncbi_attributes_flattened \
	ncbi_packages_flattened \
	sra_biosamples_bioprojects \
	unit_assertion_counts

# Create output directory
$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

# Export flattened BioProjects to DuckDB (requires bioprojects_flattened collection to exist)
export-bioprojects-to-duckdb: $(OUTPUT_DIR)
	@echo "Exporting bioprojects_flattened to DuckDB..."
	@mongoexport --uri="mongodb://$(MONGO_HOST):$(MONGO_PORT)/$(BIOPROJECTS_DB)" \
		--collection="bioprojects_flattened" \
		--type=json \
		--out="$(OUTPUT_DIR)/bioprojects_flattened.json"
	@echo "Loading into DuckDB: $(BIOPROJECTS_DUCKDB_FILE)"
	@duckdb "$(BIOPROJECTS_DUCKDB_FILE)" -c "CREATE OR REPLACE TABLE bioprojects_flattened AS SELECT * EXCLUDE _id FROM read_json('$(OUTPUT_DIR)/bioprojects_flattened.json', auto_detect=true, union_by_name=true, maximum_object_size=16777216);"
	@echo "✓ BioProjects exported to $(BIOPROJECTS_DUCKDB_FILE)"
	@echo ""
	@echo "Summary:"
	@duckdb "$(BIOPROJECTS_DUCKDB_FILE)" -c "SELECT COUNT(*) as row_count FROM bioprojects_flattened;"
	@duckdb "$(BIOPROJECTS_DUCKDB_FILE)" -c "SELECT COUNT(*) as column_count FROM (SELECT * FROM pragma_table_info('bioprojects_flattened'));"

# List all flat collections
list-flat-collections:
	@echo "100% flat collections in ncbi_metadata database:"
	@for collection in $(FLAT_COLLECTIONS); do \
		echo "  $$collection"; \
	done

# Export single collection to JSON
export-collection-json: $(OUTPUT_DIR)
	@if [ -z "$(COLLECTION)" ]; then \
		echo "Error: COLLECTION variable must be set"; \
		echo "Usage: make -f Makefiles/ncbi_to_duckdb.Makefile export-collection-json COLLECTION=collection_name"; \
		exit 1; \
	fi
	@echo "Exporting collection '$(COLLECTION)' to JSON..."
	mongoexport --uri="$(MONGO_URI)" \
		--collection="$(COLLECTION)" \
		--type=json \
		--out="$(OUTPUT_DIR)/$(COLLECTION).json"
	@echo "Exported to: $(OUTPUT_DIR)/$(COLLECTION).json"

# Load JSON into DuckDB table
json-to-duckdb: $(OUTPUT_DIR)
	@if [ -z "$(COLLECTION)" ]; then \
		echo "Error: COLLECTION variable must be set"; \
		echo "Usage: make -f Makefiles/ncbi_to_duckdb.Makefile json-to-duckdb COLLECTION=collection_name"; \
		exit 1; \
	fi
	@if [ ! -f "$(OUTPUT_DIR)/$(COLLECTION).json" ]; then \
		echo "Error: JSON file $(OUTPUT_DIR)/$(COLLECTION).json not found"; \
		echo "Run 'make -f Makefiles/ncbi_to_duckdb.Makefile export-collection-json COLLECTION=$(COLLECTION)' first"; \
		exit 1; \
	fi
	@echo "Loading $(COLLECTION).json into DuckDB table..."
	@table_name=$$(echo "$(COLLECTION)" | sed 's/\./_/g'); \
	duckdb "$(DUCKDB_FILE)" -c "CREATE OR REPLACE TABLE $$table_name AS SELECT * EXCLUDE _id FROM read_json('$(OUTPUT_DIR)/$(COLLECTION).json', auto_detect=true, union_by_name=true, maximum_object_size=16777216);"
	@echo "Loaded into table: $$table_name"

# Process single collection (export + convert)
process-collection: export-collection-json json-to-duckdb

# Dump all flat collections to JSON only
dump-json: $(OUTPUT_DIR)
	@echo "Dumping all 16 flat collections to JSON..."
	@for collection in $(FLAT_COLLECTIONS); do \
		echo "Exporting collection: $$collection"; \
		mongoexport --uri="$(MONGO_URI)" \
			--collection="$$collection" \
			--type=json \
			--out="$(OUTPUT_DIR)/$$collection.json"; \
		echo "  ✓ Exported to: $(OUTPUT_DIR)/$$collection.json"; \
	done
	@echo "All collections exported to JSON!"

# Create DuckDB database from existing JSON files
make-duckdb: $(OUTPUT_DIR)
	@echo "Creating DuckDB database from JSON files..."
	@echo "Database: $(DUCKDB_FILE_DATED)"
	@echo ""
	@for collection in $(FLAT_COLLECTIONS); do \
		json_file="$(OUTPUT_DIR)/$$collection.json"; \
		if [ ! -f "$$json_file" ]; then \
			echo "Warning: $$json_file not found, skipping..."; \
			continue; \
		fi; \
		echo "Loading $$collection into DuckDB..."; \
		table_name=$$(echo "$$collection" | sed 's/\./_/g'); \
		duckdb "$(DUCKDB_FILE_DATED)" -c "CREATE OR REPLACE TABLE $$table_name AS SELECT * EXCLUDE _id FROM read_json('$$json_file', auto_detect=true, union_by_name=true, maximum_object_size=16777216);"; \
		echo "  ✓ Table created: $$table_name"; \
	done
	@echo ""
	@echo "DuckDB database created successfully!"
	@echo "Creating symlink to latest database..."
	@cd $(OUTPUT_DIR) && ln -sf $$(basename $(DUCKDB_FILE_DATED)) $$(basename $(DUCKDB_FILE))
	@echo "✓ Symlink created: $(DUCKDB_FILE) -> $(DUCKDB_FILE_DATED)"
	@$(MAKE) -f Makefiles/ncbi_to_duckdb.Makefile show-summary

# Process all collections (JSON + DuckDB) - primary target
# Space-optimized: Exports, loads, then deletes JSON for each collection
make-database: $(OUTPUT_DIR)
	@echo "=== NCBI Metadata to DuckDB Export ==="
	@echo "Source: $(MONGO_URI)"
	@echo "Target: $(DUCKDB_FILE_DATED)"
	@echo "Symlink: $(DUCKDB_FILE)"
	@echo "Strategy: Export → Load → Clean (space-optimized)"
	@echo ""
	@for collection in $(FLAT_COLLECTIONS); do \
		echo "Processing $$collection..."; \
		json_file="$(OUTPUT_DIR)/$$collection.json"; \
		echo "  [1/3] Exporting to JSON..."; \
		mongoexport --uri="$(MONGO_URI)" \
			--collection="$$collection" \
			--type=json \
			--out="$$json_file" 2>&1 | grep -v "connected to"; \
		echo "  [2/3] Loading into DuckDB..."; \
		table_name=$$(echo "$$collection" | sed 's/\./_/g'); \
		duckdb "$(DUCKDB_FILE_DATED)" -c "CREATE OR REPLACE TABLE $$table_name AS SELECT * EXCLUDE _id FROM read_json('$$json_file', auto_detect=true, union_by_name=true, maximum_object_size=16777216);"; \
		echo "  [3/3] Cleaning up JSON..."; \
		rm -f "$$json_file"; \
		json_size=$$(du -h "$(OUTPUT_DIR)" 2>/dev/null | tail -1 | awk '{print $$1}'); \
		echo "  ✓ $$collection complete (temp files cleaned, DuckDB size: $$json_size)"; \
		echo ""; \
	done
	@echo "=== Export Complete! ==="
	@echo "Creating symlink to latest database..."
	@cd $(OUTPUT_DIR) && ln -sf $$(basename $(DUCKDB_FILE_DATED)) $$(basename $(DUCKDB_FILE))
	@echo "✓ Symlink created: $(DUCKDB_FILE) -> $(DUCKDB_FILE_DATED)"
	@$(MAKE) -f Makefiles/ncbi_to_duckdb.Makefile show-summary

# Export satisfying biosamples to CSV (biosamples meeting all quality criteria)
export-satisfying-biosamples:
	@if [ ! -f "$(DUCKDB_FILE)" ]; then \
		echo "Error: DuckDB file not found: $(DUCKDB_FILE)"; \
		echo "Run 'make -f Makefiles/ncbi_to_duckdb.Makefile make-database' first"; \
		exit 1; \
	fi
	@echo "Exporting satisfying biosamples to CSV..."
	@echo "Query: sql/satisfying_biosamples.sql"
	@duckdb "$(DUCKDB_FILE)" < sql/satisfying_biosamples.sql -csv > local/satisfying_biosamples.csv
	@echo "✓ Exported to: local/satisfying_biosamples.csv"
	@wc -l local/satisfying_biosamples.csv | awk '{printf "  %s biosamples (including header)\n", $$1}'
	@ls -lh local/satisfying_biosamples.csv | awk '{printf "  File size: %s\n", $$5}'

# Normalize satisfying biosamples (dates to YYYY-MM-DD, coordinates to separate lat/lon columns)
normalize-satisfying-biosamples:
	@if [ ! -f "local/satisfying_biosamples.csv" ]; then \
		echo "Error: local/satisfying_biosamples.csv not found"; \
		echo "Run 'make -f Makefiles/ncbi_to_duckdb.Makefile export-satisfying-biosamples' first"; \
		exit 1; \
	fi
	@echo "Normalizing biosample dates and coordinates..."
	@poetry run normalize-satisfying-biosamples \
		--input-file local/satisfying_biosamples.csv \
		--output-file local/satisfying_biosamples_normalized.csv
	@echo ""
	@echo "✓ Normalized file created: local/satisfying_biosamples_normalized.csv"
	@wc -l local/satisfying_biosamples_normalized.csv | awk '{printf "  %s biosamples (including header)\\n", $$1}'
	@ls -lh local/satisfying_biosamples_normalized.csv | awk '{printf "  File size: %s\\n", $$5}'

# Show summary of tables in DuckDB
show-summary:
	@if [ ! -f "$(DUCKDB_FILE)" ]; then \
		echo "DuckDB file not found: $(DUCKDB_FILE)"; \
		exit 1; \
	fi
	@echo "=== Database Summary ==="
	@echo "Database: $(DUCKDB_FILE)"
	@file_size=$$(ls -lLh "$(DUCKDB_FILE)" | awk '{print $$5}'); \
	echo "File size: $$file_size"
	@echo ""
	@echo "Tables:"
	@for table in $$(duckdb "$(DUCKDB_FILE)" -noheader -list -c "SELECT table_name FROM duckdb_tables() ORDER BY table_name;" 2>/dev/null); do \
		row_count=$$(duckdb "$(DUCKDB_FILE)" -noheader -list -c "SELECT COUNT(*) FROM $$table;" 2>/dev/null); \
		col_count=$$(duckdb "$(DUCKDB_FILE)" -noheader -list -c "SELECT COUNT(*) FROM pragma_table_info('$$table');" 2>/dev/null); \
		printf "  %-40s %15s rows, %4s columns\n" "$$table" "$$row_count" "$$col_count"; \
	done
	@echo ""
	@total_rows=$$(duckdb "$(DUCKDB_FILE)" -noheader -list -c "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM attribute_harmonized_pairings UNION ALL SELECT COUNT(*) FROM biosamples_attributes UNION ALL SELECT COUNT(*) FROM biosamples_flattened UNION ALL SELECT COUNT(*) FROM biosamples_ids UNION ALL SELECT COUNT(*) FROM biosamples_links UNION ALL SELECT COUNT(*) FROM content_pairs_aggregated UNION ALL SELECT COUNT(*) FROM env_triads_flattened UNION ALL SELECT COUNT(*) FROM harmonized_name_dimensional_stats UNION ALL SELECT COUNT(*) FROM harmonized_name_usage_stats UNION ALL SELECT COUNT(*) FROM measurement_evidence_percentages UNION ALL SELECT COUNT(*) FROM measurement_results_skip_filtered UNION ALL SELECT COUNT(*) FROM mixed_content_counts UNION ALL SELECT COUNT(*) FROM ncbi_attributes_flattened UNION ALL SELECT COUNT(*) FROM ncbi_packages_flattened UNION ALL SELECT COUNT(*) FROM sra_biosamples_bioprojects UNION ALL SELECT COUNT(*) FROM unit_assertion_counts);" 2>/dev/null); \
	echo "Total rows across all tables: $$total_rows"

# Clean up JSON dumps
clean-json:
	@echo "Removing JSON dumps..."
	rm -f $(OUTPUT_DIR)/*.json
	@echo "JSON dumps removed."

# Clean up DuckDB database
clean-duckdb:
	@echo "Removing DuckDB database..."
	rm -f $(OUTPUT_DIR)/*.duckdb
	@echo "DuckDB database removed."

# Clean up all generated files
clean: clean-json clean-duckdb
	@echo "Removing output directory if empty..."
	@rmdir $(OUTPUT_DIR) 2>/dev/null || true
	@echo "Cleanup complete."

# Show current configuration
show-config:
	@echo "Current Configuration:"
	@echo "  MONGO_URI: $(MONGO_URI)"
	@echo "  MONGO_DB: $(MONGO_DB)"
	@echo "  OUTPUT_DIR: $(OUTPUT_DIR)"
	@echo "  DUCKDB_FILE: $(DUCKDB_FILE)"
	@echo "  Collections: $(words $(FLAT_COLLECTIONS)) flat collections"

# Help target
help:
	@echo "NCBI MongoDB to DuckDB Migration"
	@echo ""
	@echo "Primary targets:"
	@echo "  make-database                    - Export all flat collections and create DuckDB"
	@echo "  export-bioprojects-to-duckdb     - Export bioprojects_flattened to separate DuckDB"
	@echo "  export-satisfying-biosamples     - Export biosamples meeting quality criteria to CSV"
	@echo "  normalize-satisfying-biosamples  - Normalize dates and split coordinates into lat/lon columns"
	@echo ""
	@echo "Note: To flatten BioProjects first, use:"
	@echo "  make -f Makefiles/ncbi_metadata.Makefile flatten_bioprojects MONGO_URI=mongodb://host:port/db"
	@echo "  dump-json                  - Export all collections to JSON only"
	@echo "  make-duckdb                - Create DuckDB from existing JSON files"
	@echo ""
	@echo "Single collection targets:"
	@echo "  export-collection-json COLLECTION=name  - Export single collection to JSON"
	@echo "  json-to-duckdb COLLECTION=name          - Load single JSON into DuckDB"
	@echo "  process-collection COLLECTION=name      - Export + load single collection"
	@echo ""
	@echo "Information targets:"
	@echo "  list-flat-collections      - List all 16 flat collections"
	@echo "  show-summary               - Show table counts in DuckDB"
	@echo "  show-config                - Show current configuration"
	@echo ""
	@echo "Cleanup targets:"
	@echo "  clean-json                 - Remove JSON dumps"
	@echo "  clean-duckdb               - Remove DuckDB database"
	@echo "  clean                      - Remove all generated files"
	@echo ""
	@echo "Configuration variables (set with VAR=value):"
	@echo "  MONGO_HOST                 - MongoDB host (default: localhost)"
	@echo "  MONGO_PORT                 - MongoDB port (default: 27017)"
	@echo "  MONGO_DB                   - MongoDB database (default: ncbi_metadata)"
	@echo "  OUTPUT_DIR                 - Output directory (default: ./local/ncbi_duckdb_export)"
	@echo ""
	@echo "Example usage:"
	@echo "  make -f Makefiles/ncbi_to_duckdb.Makefile make-database"
	@echo "  make -f Makefiles/ncbi_to_duckdb.Makefile show-summary"

.PHONY: list-flat-collections export-collection-json json-to-duckdb process-collection \
        dump-json make-duckdb make-database export-bioprojects-to-duckdb export-satisfying-biosamples \
        normalize-satisfying-biosamples show-summary clean clean-json clean-duckdb show-config help
