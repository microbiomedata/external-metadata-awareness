RUN = poetry run
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

.PHONY: normalize-measurements flatten-measurements flattened-measurements-processing \
purge-measurements purge-flattened-measurements purge-measurements-aggregations
normalize-measurements:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) normalize-biosample-measurements \
		--mongodb-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--overwrite \
		--field age \
		--field elev \
		--field samp_size

flatten-measurements:
	@date
	@echo "flattening biosample measurements..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_biosamples_measurements.js \
		--verbose
	@date

flattened-measurements-processing:
	@date
	@echo "aggregating measurement evidence by harmonized name..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/measurement_evidence_by_harmonized_name.js \
		--verbose
	@date
	@echo "indexing biosamples_measurements.parsed_quantity..."
	$(RUN) mongo-connect \
			--uri "$(MONGO_URI)" \
			$(ENV_FILE_OPTION) \
			--connect \
			--verbose \
			--command "db.biosamples_measurements.createIndex({ parsed_quantity: 1 })"
	@date
	@echo "counting inferred units by harmonized name..."
	time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/measurements_inferred_units_counts_by_harmonized_names.js \
		--verbose
	@date
	@echo "counting total inferred units..."
		time $(RUN) mongo-js-executor \
			--mongo-uri "$(MONGO_URI)" \
			$(ENV_FILE_OPTION) \
			--js-file mongo-js/measurements_inferred_units_totals.js \
			--verbose
		@date

# Target: purge-measurements
# Removes MongoDB collections related to biosample measurements
purge-measurements:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Purging biosamples_measurements collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.biosamples_measurements.drop()"
	@date

purge-flattened-measurements:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Purging biosamples_measurements collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.biosamples_measurements_flattened.drop()"
	@date

purge-measurements-aggregations:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	@echo "Purging measurement_evidence_by_harmonized_name collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.measurement_evidence_by_harmonized_name.drop()"
	@echo "Purging measurements_inferred_units_counts collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.measurements_inferred_units_counts.drop()"
	@echo "Purging measurements_inferred_units_counts_by_harmonized_names collection..."
	$(RUN) mongo-connect \
		--uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--connect \
		--verbose \
		--command "db.measurements_inferred_units_counts_by_harmonized_names.drop()"
	@date