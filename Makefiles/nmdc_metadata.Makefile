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

# Submissions fetch: the .env file is the canonical per-environment config.
# It holds NMDC_DATA_SUBMISSION_REFRESH_TOKEN plus MONGO_URI, BASE_URL, and
# OUTPUT_FILE for that environment. The dev target overrides only which env
# file to load; everything else lives inside the file.
NMDC_SUBMISSIONS_ENV ?= local/.env.nmdc-submissions

nmdc-submissions-to-mongo-dev: NMDC_SUBMISSIONS_ENV := local/.env.nmdc-submissions-data-dev

.PHONY: nmdc-submissions-to-mongo nmdc-submissions-to-mongo-dev
nmdc-submissions-to-mongo nmdc-submissions-to-mongo-dev:
	@if [ ! -f "$(NMDC_SUBMISSIONS_ENV)" ]; then \
		echo "Error: $(NMDC_SUBMISSIONS_ENV) not found."; \
		echo "Required:"; \
		echo "  NMDC_DATA_SUBMISSION_REFRESH_TOKEN=<token from data[-dev].microbiomedata.org Local Storage>"; \
		echo "  MONGO_URI=mongodb://<user>:<pw>@<host>:<port>/<db>?authSource=admin"; \
		echo "Optional (the CLI supplies defaults when omitted):"; \
		echo "  BASE_URL=https://data.microbiomedata.org   (or https://data-dev.microbiomedata.org)"; \
		echo "  OUTPUT_FILE=local/nmdc_export/flattened_submission_biosamples.tsv  (under the default NMDC_EXPORT_DIR)"; \
		exit 1; \
	fi
	@mkdir -p $(NMDC_EXPORT_DIR)
	$(RUN) python external_metadata_awareness/nmdc-submissions-to-mongo.py \
		run-all \
		--env-path "$(NMDC_SUBMISSIONS_ENV)"

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

# Reads MONGO_URI from $(NMDC_SUBMISSIONS_ENV) with a non-executing dotenv
# parser (not shell sourcing, which would mishandle URIs containing '&' and
# would run any code in the file) and passes it to mongosh through the
# environment rather than as an argv parameter, so the credential is not
# visible in process listings or echoed recipes. Dev target overrides which
# file is loaded, same as the fetch targets above.
nmdc-submissions-drop-dev: NMDC_SUBMISSIONS_ENV := local/.env.nmdc-submissions-data-dev

.PHONY: drop-nmdc-submissions nmdc-submissions-drop-dev
drop-nmdc-submissions nmdc-submissions-drop-dev:
	@if [ ! -f "$(NMDC_SUBMISSIONS_ENV)" ]; then \
		echo "Error: $(NMDC_SUBMISSIONS_ENV) not found."; \
		exit 1; \
	fi
	@echo "Dropping submission collections from MongoDB configured by $(NMDC_SUBMISSIONS_ENV) ..."
	@MONGO_URI="$$($(RUN) python -c 'from dotenv import dotenv_values; print(dotenv_values("$(NMDC_SUBMISSIONS_ENV)").get("MONGO_URI") or "")')"; \
	if [ -z "$$MONGO_URI" ]; then echo "Error: MONGO_URI not set in $(NMDC_SUBMISSIONS_ENV)"; exit 1; fi; \
	MONGO_URI="$$MONGO_URI" NMDC_SUBMISSION_COLLECTIONS="$(NMDC_SUBMISSION_COLLECTIONS)" \
		mongosh --nodb --quiet --eval 'const db = connect(process.env.MONGO_URI); process.env.NMDC_SUBMISSION_COLLECTIONS.split(/\s+/).forEach(function (c) { db.getCollection(c).drop(); print("Dropped: " + c); });'

# ---------- MIxS required-slot gap report ----------
# Two phases; see docs/mixs-required-slot-report.md.

# Phase 1 (deterministic), offline baked weight snapshot.
local/mixs_required_slot_report.tsv:
	@mkdir -p local
	$(RUN) mixs-required-slot-report -o $@

.PHONY: mixs-required-slot-report
mixs-required-slot-report: local/mixs_required_slot_report.tsv

# Phase 1 with live weights from prod biosample_set. Open the jump-dev tunnel
# first (docs/nmdc-prod-mongo-tunnel.md). Override MIXS_REPORT_ENV_FILE if the
# prod credentials live in a different .env.
MIXS_REPORT_ENV_FILE ?= local/.env
.PHONY: mixs-required-slot-report-live
mixs-required-slot-report-live:
	@mkdir -p local
	$(RUN) mixs-required-slot-report --weight-source env-package --refresh-weights --env-file $(MIXS_REPORT_ENV_FILE) -o local/mixs_required_slot_report.tsv

# Phase 2 (agentic layer): merge curated priority/comment annotations. Produce
# MIXS_GAP_ANNOTATIONS with the mixs-gap-comments skill, or start from the seed
# at .claude/skills/mixs-gap-comments/mixs_gap_annotations.seed.tsv.
MIXS_GAP_ANNOTATIONS ?= local/mixs_gap_annotations.tsv
.PHONY: mixs-required-slot-report-annotated
mixs-required-slot-report-annotated:
	@mkdir -p local
	$(RUN) mixs-required-slot-report --annotations $(MIXS_GAP_ANNOTATIONS) -o local/mixs_required_slot_report_annotated.tsv

# Cleanup: generated report outputs (regenerable). The working annotations TSV
# is curated Phase-2 input, so it has its own explicit target.
.PHONY: mixs-required-slot-report-clean
mixs-required-slot-report-clean:
	rm -f local/mixs_required_slot_report.tsv local/mixs_required_slot_report_annotated.tsv

.PHONY: mixs-gap-annotations-clean
mixs-gap-annotations-clean:
	rm -f local/mixs_gap_annotations.tsv
