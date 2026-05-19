RUN=poetry run
WGET=wget
MONGO_URI ?= mongodb://localhost:27017/nmdc
NMDC_EXPORT_DIR ?= ./local/nmdc_export
NMDC_PARQUET_DIR ?= $(NMDC_EXPORT_DIR)/parquet
NMDC_CSV_DIR ?= $(NMDC_EXPORT_DIR)/csv
NMDC_DUCKDB_FILE ?= $(NMDC_EXPORT_DIR)/nmdc_flattened.duckdb

OUTPUT_FILE ?= $(NMDC_EXPORT_DIR)/biosample_coverage_results.json

NMDC_FLATTENED_COLLECTIONS = \
	flattened_biosample \
	flattened_biosample_chem_administration \
	flattened_biosample_field_counts \
	flattened_study \
	flattened_study_associated_dois \
	flattened_study_has_credit_associations

## Load environment variables from local/.env file if it exists
#ifneq (,$(wildcard local/.env))
#    include local/.env
#    export $(shell sed 's/=.*//' local/.env)
#endif

downloads/nmdc-production-studies.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/study_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

downloads/nmdc-production-biosamples.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-5pct.json: downloads/nmdc-production-biosamples.json
	$(RUN) random-sample-resources \
		--input-file $< \
		--output-file $@ \
		--sample-percentage 5

local/nmdc-production-biosamples-env-context-columns.tsv: downloads/nmdc-production-biosamples.json
	$(RUN) biosample-json-to-context-tsv \
		--input-file $< \
		--output-file $@

local/nmdc-production-biosamples-env-context-authoritative-labels.tsv: local/nmdc-production-biosamples-env-context-columns.tsv
	$(RUN) python external_metadata_awareness/get_authoritative_labels_only_for_nmdc_context_columns.py \
		--input-file $< \
		--output-file $@ \
		--oak-adapter-string 'sqlite:obo:envo'

local/nmdc-production-biosamples-env_package-predictions.tsv: local/nmdc-production-biosamples-env-context-authoritative-labels.tsv \
downloads/nmdc-production-studies.json
	$(RUN) python external_metadata_awareness/predict_env_package_from_nmdc_context_authoritative_labels.py \
		--input-file $(word 1,$^) \
		--output-file $@ \
		--oak-adapter-string 'sqlite:obo:envo' \
		--heterogeneity-file 'local/env-package-heterogeneity.tsv' \
		--override-file 'contributed/mam-env-package-overrides.tsv' \
		--override-biosample-column 'id' \
		--override-env-package-column 'mam_inferred_env_package' \
		--studies-json $(word 2,$^)

# no header?
local/nmdc-production-biosamples-env_local_scale.tsv: local/nmdc-production-biosamples-env-context-columns.tsv
	cut -f5 $< | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@

local/nmdc-production-biosamples-soil-env_local_scale.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f5 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-soil-env_broad_scale.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f3 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-soil-env_medium.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f7 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-env_local_scale-ids.txt: local/nmdc-production-biosamples-env_local_scale.tsv
	cut -f1 $< > $@

local/nmdc-production-biosamples-env-package.json:
	curl -X 'GET' \
		'https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999&projection=env_package' \
		-H 'accept: application/json' > $@.bak
	yq '.resources' -o=json $@.bak | cat > $@ # ENVO:00001998 is also soil
	rm -rf $@.bak

local/nmdc-production-studies-images.csv: downloads/nmdc-production-studies.json
	$(RUN) python external_metadata_awareness/study_image_table.py \
		--input-file $< \
		--output-file $@

####

# biosamples that are part of a particular study
downloads/sty-11-ev70y104_biosamples.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/biosample_set?filter=%7B%22part_of%22%3A%20%22nmdc%3Asty-11-ev70y104%22%7D&max_page_size=999999'
	yq -o=json e '.resources' $@.bak | cat > $@
	rm -rf $@.bak

# metadata about a particular study
downloads/sty-11-ev70y104_study.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/ids/nmdc%3Asty-11-ev70y104'
	yq -o=json e '.' $@.bak | cat > $@
	rm -rf $@.bak

####

local/nmdc-schema-known-collections.txt:
	curl \
		-sSL 'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/tags/v11.5.1/nmdc_schema/nmdc_materialized_patterns.yaml' | \
		yq '.classes.Database.slots.[]' | sort > $@

local/nmdc-prod-api-advertised-collections.txt:
	curl \
		-sSL 'https://api.microbiomedata.org/nmdcschema/collection_stats' | \
			jq -r '.[].ns' | sed 's/nmdc\.//' | sort > $@

# this doesn't tell us anything  about the size of the collections!
local/nmdc-consensus-collections.txt: local/nmdc-prod-api-advertised-collections.txt local/nmdc-schema-known-collections.txt
	comm -12 $^ | sort > $@

local/nmdc-prod-api-advertised-collection-stats.json:
	curl -sSL 'https://api.microbiomedata.org/nmdcschema/collection_stats' | jq . > $@

NMDC_SUBMISSIONS_ENV ?= local/.env.nmdc-submissions
NMDC_SUBMISSIONS_TSV ?= $(NMDC_EXPORT_DIR)/flattened_submission_biosamples.tsv
NMDC_SUBMISSIONS_BASE_URL ?= https://data.microbiomedata.org

# Data-dev environment config
NMDC_SUBMISSIONS_DEV_ENV ?= local/.env.nmdc-submissions-data-dev
NMDC_SUBMISSIONS_DEV_TSV ?= $(NMDC_EXPORT_DIR)/flattened_submission_biosamples_data_dev.tsv
NMDC_DATA_DEV_MONGO_URI ?= mongodb://localhost:27017/nmdc_data_dev
NMDC_SUBMISSIONS_DEV_BASE_URL ?= https://data-dev.microbiomedata.org

.PHONY: nmdc-submissions-to-mongo
nmdc-submissions-to-mongo:
	@if [ ! -f "$(NMDC_SUBMISSIONS_ENV)" ]; then \
		echo "Error: $(NMDC_SUBMISSIONS_ENV) not found."; \
		echo "Create it with: NMDC_DATA_SUBMISSION_REFRESH_TOKEN=<your-token>"; \
		exit 1; \
	fi
	@mkdir -p $(NMDC_EXPORT_DIR)
	$(RUN) python external_metadata_awareness/nmdc-submissions-to-mongo.py \
		run-all \
		--mongo-url "$(MONGO_URI)" \
		--env-path "$(NMDC_SUBMISSIONS_ENV)" \
		--output-file "$(NMDC_SUBMISSIONS_TSV)" \
		--base-url "$(NMDC_SUBMISSIONS_BASE_URL)"

.PHONY: nmdc-submissions-to-mongo-dev
nmdc-submissions-to-mongo-dev:
	@if [ ! -f "$(NMDC_SUBMISSIONS_DEV_ENV)" ]; then \
		echo "Error: $(NMDC_SUBMISSIONS_DEV_ENV) not found."; \
		echo "Create it with: NMDC_DATA_SUBMISSION_REFRESH_TOKEN=<your-token>"; \
		echo "Token source: https://data-dev.microbiomedata.org (Local Storage after ORCID login)"; \
		exit 1; \
	fi
	@mkdir -p $(NMDC_EXPORT_DIR)
	$(RUN) python external_metadata_awareness/nmdc-submissions-to-mongo.py \
		run-all \
		--mongo-url "$(NMDC_DATA_DEV_MONGO_URI)" \
		--env-path "$(NMDC_SUBMISSIONS_DEV_ENV)" \
		--output-file "$(NMDC_SUBMISSIONS_DEV_TSV)" \
		--base-url "$(NMDC_SUBMISSIONS_DEV_BASE_URL)"

NMDC_SUBMISSIONS_DUCKDB ?= local/nmdc_submissions.duckdb
NMDC_EVAL_INPUT_TARGET_TSV ?= $(NMDC_EXPORT_DIR)/eval_input_target_pairs.tsv

.PHONY: export-submissions-to-duckdb
export-submissions-to-duckdb:
	@mkdir -p $(dir $(NMDC_SUBMISSIONS_DUCKDB))
	$(RUN) export-submissions-to-duckdb --output "$(NMDC_SUBMISSIONS_DUCKDB)"
	@echo "Written: $(NMDC_SUBMISSIONS_DUCKDB)"

.PHONY: eval-input-target-tsv
eval-input-target-tsv: export-submissions-to-duckdb
	@mkdir -p $(NMDC_EXPORT_DIR)
	duckdb "$(NMDC_SUBMISSIONS_DUCKDB)" -csv -separator '	' < sql/eval_input_target_pairs.sql > "$(NMDC_EVAL_INPUT_TARGET_TSV)"
	@echo "Written: $(NMDC_EVAL_INPUT_TARGET_TSV) ($$(wc -l < "$(NMDC_EVAL_INPUT_TARGET_TSV)") lines)"

NMDC_SUBMISSION_COLLECTIONS = nmdc_submissions flattened_submission_biosamples submission_biosample_rows submission_biosample_slot_counts

.PHONY: drop-nmdc-submissions
drop-nmdc-submissions:
	@echo "Dropping submission collections from $(MONGO_URI)..."
	@for coll in $(NMDC_SUBMISSION_COLLECTIONS); do \
		mongosh "$(MONGO_URI)" --quiet --eval "db.getCollection('$$coll').drop(); print('Dropped: $$coll');" ; \
	done
