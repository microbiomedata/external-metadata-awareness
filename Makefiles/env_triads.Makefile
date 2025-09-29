RUN = poetry run
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# todo ?
# env_triads_component_curies_uc instead of env_triad_component_curies_uc ?
# env_triads_component_labels instead of env_triad_component_labels ?

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: count-harmonizable-attribs purge-derived-repos env-triads biosamples-flattened env-triad-value-counts

# make load-biosamples-into-mongo
# Processed 44750000 BioSample nodes (95.56%), elapsed time: 34960.22 seconds
  #date
  #Sat Apr  5 21:12:43 EDT 2025

purge-derived-repos:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Purging biosamples_env_triad_value_counts_gt_1 collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.biosamples_env_triad_value_counts_gt_1.drop()"
	@echo "Purging env_triad_component_labels collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.env_triad_component_labels.drop()"
	@echo "Purging env_triad_component_curies_uc collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.env_triad_component_curies_uc.drop()"
	@echo "Purging biosamples_flattened collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.biosamples_flattened.drop()"
	@echo "Purging env_triads collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.env_triads.drop()"
	@date

count-harmonizable-attribs: mongo-js/count_harmonizable_biosample_attribs.js
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Ensuring index on Attributes.Attribute.harmonized_name..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.biosamples.createIndex({"Attributes.Attribute.harmonized_name": 1})' # 30? minutes
	@echo "Running aggregation script..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file $< \
		--verbose # 30? minutes
	@date


env-triads: biosamples-flattened env-triad-value-counts

# Step 1: Flatten biosamples collection into biosamples_flattened  
# IMPORTANT: This target creates the biosamples_flattened collection used by measurement discovery pipeline
biosamples-flattened:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Flattening biosamples collection into biosamples_flattened..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_biosamples.js \
		--verbose
	@echo "Creating index on env field in biosamples_flattened..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.biosamples_flattened.createIndex({ env_broad_scale: 1, env_local_scale: 1, env_medium: 1 })'
	@date

# Step 2: Extract unique environmental triad values with counts
env-triad-value-counts: 
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Extracting env triad values with counts to biosamples_env_triad_value_counts_gt_1..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/enriched_biosamples_env_triad_value_counts_gt_1.js \
		--verbose
	@echo "Creating index on env_triad_value..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.biosamples_env_triad_value_counts_gt_1.createIndex({env_triad_value: 1}, {unique: true})'
	@date
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) env-triad-values-splitter \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--collection biosamples_env_triad_value_counts_gt_1 \
		--field env_triad_value \
		--min-length 3 \
		--verbose # < 1 minute # FAILS IF BIOPORTAL KEY NOT IN local/.env # works best if expanded_envo_po_lexical_index.yaml present
	@echo "Creating index on components.label, components.label_digits_only, components.label_length, count..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.biosamples_env_triad_value_counts_gt_1.createIndex({ "components.label": 1, "components.label_digits_only": 1, "components.label_length": 1, "count": 1 })'
	@echo "Running aggregation to generate label components..."
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/aggregate_env_triad_label_components.js \
		--verbose && date # fast
	@echo "Creating index on label_digits_only and label_length..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.env_triad_component_labels.createIndex({label_digits_only: 1, label_length: 1})'
	date && time $(RUN) env-triad-oak-annotator \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--verbose && date # 3 minutes, local, non-web API
	date && time $(RUN) env-triad-ols-annotator \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--verbose && date # 7 minutes, running mostly off of cache; 7 hours without cache
	@echo "Creating index on components.curie_uc and count..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.biosamples_env_triad_value_counts_gt_1.createIndex({ "components.curie_uc": 1, "count": 1 })'
	@echo "Running aggregation to generate CURIEs..."
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/aggregate_env_triad_curies.js \
		--verbose && date
	@echo "Creating index on prefix_uc..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.env_triad_component_curies_uc.createIndex({ prefix_uc: 1 })'
	date && time $(RUN) env-triad-check-semsql-curies \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--verbose && date
	@echo "Creating index on prefix_uc and curie_uc..."
	time $(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command 'db.env_triad_component_curies_uc.createIndex({ prefix_uc: 1, curie_uc: 1 })'
	date && time $(RUN) env-triad-bioportal-curie-mapper \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--verbose && date # 2 minutes, mostly running off of cache; 13 minutes without cache
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) populate-env-triads-collection \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) # creates its own indices # 30 minutes + 6 for indexing

####

# duplicative
split-env-triad-values:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) env-triad-values-splitter \
			--mongo-uri "$(MONGO_URI)" \
			--collection biosamples_env_triad_value_counts_gt_1 \
			--field env_triad_value \
			--min-length 3 \
			--verbose \
			$(ENV_FILE_OPTION)
	@date

# Usage examples:
# make split-env-triad-values
# make split-env-triad-values MONGO_URI="mongodb://mongo-ncbi-loadbalancer.mam.production.svc.spin.nersc.org:27017/ncbi_metadata?authMechanism=SCRAM-SHA-256&authSource=admin&directConnection=true"

