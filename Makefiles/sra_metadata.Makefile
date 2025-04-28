RUN=poetry run

# Default MongoDB connection
MONGO_URI ?= mongodb://localhost:27017/sra_metadata  # this conflicts with earlier imports into the root Makefile, so always user make -f

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: biosample-bioproject-preview sra_accession_pairs_tsv_to_mongo \
        fetch_sra_metadata_parquet_from_s3 load-sra-parquet-to-mongo \
        purge-sra dump-sra-metadata-schema extract-sra-biosample-bioproject-pairs

# SRA BigQuery parameters
SRA_BIGQUERY_PROJECT = nmdc-377118
SRA_BIGQUERY_DATASET = nih-sra-datastore.sra
SRA_BIGQUERY_TABLE = metadata
SRA_BIGQUERY_BATCH_SIZE = 100000
SRA_BIGQUERY_LIMIT = 30000000 # expect ~ 30000000

# Target: purge-sra
# Removes all SRA data files and temporary directories
purge-sra:
	rm -rf downloads/sra_accession_pairs.tsv
	rm -rf downloads/sra_metadata_table_schema.tsv
	rm -rf local/sra_metadata_parquet

# Target: dump-sra-metadata-schema
# Dumps the BigQuery SRA metadata table schema to a TSV file
dump-sra-metadata-schema: downloads/sra_metadata_table_schema.tsv

downloads/sra_metadata_table_schema.tsv:
	@echo "Dumping SRA metadata schema from BigQuery..."
	$(RUN) dump-sra-metadata-schema \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--output $@ \
		--format tsv

# Target: biosample-bioproject-preview
# Preview mode: analyze the dataset without exporting
biosample-bioproject-preview:
	@echo "Previewing BioSample-BioProject relationships in SRA data..."
	$(RUN) export-sra-accession-pairs \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--report-nulls \
		--preview \
		--verbose

# Target: sra_accession_pairs_tsv_to_mongo
# Exports BioSample-BioProject pairs from SRA to MongoDB
downloads/sra_accession_pairs.tsv:
	@echo "Exporting SRA accession pairs to TSV..."
	$(RUN) export-sra-accession-pairs \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--batch-size $(SRA_BIGQUERY_BATCH_SIZE) \
		--limit $(SRA_BIGQUERY_LIMIT) \
		--exclude-nulls \
		--output $@

sra_accession_pairs_tsv_to_mongo: downloads/sra_accession_pairs.tsv
	@echo "Loading SRA accession pairs into MongoDB..."
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) sra-accession-pairs-to-mongo \
		--file-path $< \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--collection sra_biosamples_bioprojects \
		--batch-size 100000 \
		--report-interval 500000

# Target: fetch_sra_metadata_parquet_from_s3
# Fetches SRA metadata Parquet files from S3
local/sra_metadata_parquet:
	mkdir -p $@

# Default setup (set a flag for Perlmutter or local execution)
USE_SHIFTER ?= 0  # Default to local (0 means not using shifter)

fetch_sra_metadata_parquet_from_s3: local/sra_metadata_parquet
	# Ensure necessary directories exist
	@mkdir -p local/sra_metadata_parquet

	@date
	@if [ "$(USE_SHIFTER)" -eq 1 ]; then \
		echo "Running on Perlmutter, using shifter..."; \
		shifter --image=amazon/aws-cli:latest aws s3 cp s3://sra-pub-metadata-us-east-1/sra/metadata/ $< --recursive --no-sign-request; \
	else \
		echo "Running locally, skipping shifter..."; \
		aws s3 cp s3://sra-pub-metadata-us-east-1/sra/metadata/ $< --recursive --no-sign-request; \
	fi
	@date

# Target: load-sra-parquet-to-mongo
# Loads SRA Parquet data into MongoDB

# SRA Parquet collection variables
SRA_PARQUET_MAX_ROWS ?=

# Define row limit option if SRA_PARQUET_MAX_ROWS is set
ifdef SRA_PARQUET_MAX_ROWS
  SRA_PARQUET_ROWS_OPTION := --nrows $(SRA_PARQUET_MAX_ROWS)
endif

load-sra-parquet-to-mongo: local/sra_metadata_parquet
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) sra-parquet-to-mongodb \
			--parquet-dir $< \
			--drop-collection \
			--progress-interval 1000 \
			--mongo-uri "$(MONGO_URI)" \
			--mongo-collection sra_metadata \
			$(SRA_PARQUET_ROWS_OPTION) \
			$(ENV_FILE_OPTION) \
			--verbose
	@date

# Target: extract-sra-biosample-bioproject-pairs
# Extracts biosample-bioproject pairs from SRA metadata and stores them in a separate collection
extract-sra-biosample-bioproject-pairs:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/extract_sra_biosample_bioproject_pairs_simple.js \
		--verbose
	@date

# Usage examples:
# make -f Makefiles/sra_metadata.Makefile load-sra-parquet-to-mongo
# make -f Makefiles/sra_metadata.Makefile sra_accession_pairs_tsv_to_mongo
# make -f Makefiles/sra_metadata.Makefile extract-sra-biosample-bioproject-pairs
# make -f Makefiles/sra_metadata.Makefile load-sra-parquet-to-mongo MONGO_URI="mongodb://host:port/database" ENV_FILE=local/.env.auth

count_sra_metadata_keys:
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/count_sra_metadata_keys.js \
		--verbose && date
