RUN=poetry run
WGET=wget

# Load environment variables from local/.env file if it exists
ifneq (,$(wildcard local/.env))
    include local/.env
    export $(shell sed 's/=.*//' local/.env)
endif

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

.PHONY: local_mongodb_restore
local_nmdc_mongodb_restore: downloads/nmdc_select_mongodb_dump.gz
	mongorestore \
		--gzip \
		--archive=$< \
		--db nmdc

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

local/nmdc-prod-mongodb-empirical-collection-names.txt:
	( \
	  set -a && . local/.env.nmdc-production && set +a && \
	  mongosh "mongodb://localhost:$$MONGO_PORT/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
	    --username "$$MONGO_USERNAME" \
	    --password "$$MONGO_PASSWORD" \
	    --quiet \
	    --eval 'db = db.getSiblingDB("nmdc"); print(JSON.stringify(db.getCollectionNames()))' \
	    | jq -r '.[]' | sort > $@ \
	)

local/nmdc-prod-api-advertised-collection-stats.json:
	curl -sSL 'https://api.microbiomedata.org/nmdcschema/collection_stats' | jq . > $@

local/dumped-from-authenticated: local/nmdc-consensus-collections.txt # 06:31 -
	mkdir -p $@
	( \
	  set -a && . local/.env.nmdc-production && set +a && \
	  while read collection; do \
	    echo "Dumping $$collection..."; \
	    mongodump \
	      --uri="mongodb://localhost:$$MONGO_PORT/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
	      --username="$$MONGO_USERNAME" \
	      --password="$$MONGO_PASSWORD" \
	      --db="$$MONGO_DB" \
	      --collection="$$collection" \
	      --out="$@"; \
	  done < $< \
	)

.PHONY: restore-to-unauthenticated
restore-to-unauthenticated: local/dumped-from-authenticated
	( \
	  set -a && . local/.env.nmdc-production && set +a && \
	  echo "Dropping database $$MONGO_DB..."; \
	  mongosh "mongodb://localhost:27017" --quiet --eval 'db.getSiblingDB("'"$$MONGO_DB"'").dropDatabase()'; \
	  for bson_file in $</$${MONGO_DB}/*.bson; do \
	    collection=$$(basename $$bson_file .bson); \
	    echo "Restoring $$collection into $$MONGO_DB..."; \
	    mongorestore \
	      --host=localhost \
	      --port=27017 \
	      --db="$$MONGO_DB" \
	      --collection="$$collection" \
	      "$$bson_file"; \
	  done \
	)

.PHONY: flatten-nmdc
flatten-nmdc:
	$(RUN) python external_metadata_awareness/flatten_nmdc_collections.py \
		--mongo-uri mongodb://localhost:27017/nmdc

# Use authenticated connection from .env file
.PHONY: flatten-nmdc-auth
flatten-nmdc-auth:
	$(RUN) python external_metadata_awareness/flatten_nmdc_collections.py \
		--auth \
		--env-file local/.env \
		--mongo-db nmdc

# These collections are created by the flatten-nmdc target
# NON _agg/_set COLLECTIONS
#  flattened_biosample
#  flattened_biosample_chem_administration
#  flattened_biosample_field_counts
#  flattened_study
#  flattened_study_associated_dois
#  flattened_study_has_credit_associations

  #notes

####

.PHONY: nmdc-prod-to-other
nmdc-prod-to-other:
	mkdir -p local/nmdc-prod-to-other


downloads/nmdc_select_mongodb_dump.gz:
	# requires opening a ssh tunnel to the NMDC MongoDB, which requires NERSC credentials
	#   and NMDC MongoDB credentials
	mongodump \
		--uri "mongodb://$(NMDC_MONGO_USER):$(NMDC_MONGO_PASSWORD)@localhost:27777/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
		--db nmdc \
		--archive=$@ \
		--gzip \
		--excludeCollection EMP_soil_project_run_counts \
		--excludeCollection _migration_events \
		--excludeCollection _migration_latest_schema_version \
		--excludeCollection _runtime.analytics \
		--excludeCollection _runtime.api.allow \
		--excludeCollection _runtime.healthcheck \
		--excludeCollection _tmp__get_file_size_bytes \
		--excludeCollection alldocs \
		--excludeCollection capabilities \
		--excludeCollection date_created \
		--excludeCollection etl_software_version \
		--excludeCollection file_type_enum \
		--excludeCollection fs.chunks \
		--excludeCollection fs.files \
		--excludeCollection id_records \
		--excludeCollection ids \
		--excludeCollection ids_nmdc_fk0 \
		--excludeCollection ids_nmdc_fk4 \
		--excludeCollection ids_nmdc_gfs0 \
		--excludeCollection ids_nmdc_mga0 \
		--excludeCollection ids_nmdc_mta0 \
		--excludeCollection ids_nmdc_sys0 \
		--excludeCollection jobs \
		--excludeCollection metap_gene_function_aggregation \
		--excludeCollection minter.id_records \
		--excludeCollection minter.requesters \
		--excludeCollection minter.schema_classes \
		--excludeCollection minter.services \
		--excludeCollection minter.shoulders \
		--excludeCollection minter.typecodes \
		--excludeCollection nmdc_schema_version \
		--excludeCollection notes \
		--excludeCollection object_types \
		--excludeCollection objects \
		--excludeCollection operations \
		--excludeCollection page_tokens \
		--excludeCollection queries \
		--excludeCollection query_runs \
		--excludeCollection requesters \
		--excludeCollection run_events \
		--excludeCollection schema_classes \
		--excludeCollection services \
		--excludeCollection shoulders \
		--excludeCollection sites \
		--excludeCollection system.views \
		--excludeCollection triggers \
		--excludeCollection txn_log \
		--excludeCollection typecodes \
		--excludeCollection users \
		--excludeCollection workflows

 #functional_annotation_agg,4543621539
 #workflow_execution_set,196286407
 #data_object_set,46924773
 #biosample_set,15580460
 #data_generation_set,5206299
 #material_processing_set,2037568
 #processed_sample_set,808302
 #study_set,169372
 #field_research_site_set,12705
 #configuration_set,5287
 #instrument_set,2224
 #calibration_set,1476
 #manifest_set,678
 #storage_process_set,0
 #collecting_biosamples_from_site_set,0
 #protocol_execution_set,0
 #chemical_entity_set,0

# 		--excludeCollection chemical_entity_set \
# 		--excludeCollection collecting_biosamples_from_site_set \
# 		--excludeCollection storage_process_set \
#		--excludeCollection material_sample_set \
#		--excludeCollection omics_processing_set \
#		--excludeCollection planned_process_set \
#		--excludeCollection protocol_execution_set \
#		--excludeCollection functional_annotation_agg \