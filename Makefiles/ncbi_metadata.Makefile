# Configurable storage roots. Override per invocation, e.g.
#   make TARGET LOCAL_DIR=/Volumes/owc-nvme/local DOWNLOADS_DIR=/Volumes/owc-nvme/downloads
DOWNLOADS_DIR ?= downloads
LOCAL_DIR ?= local

RUN=poetry run
WGET=wget

# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running

# todo update dev and user documentation; share database and documentation at NERSC portal

# todo add poetry CLI aliases for python scripts

# todo what kind of logging/progress indication is really most useful?

# todo log don't print

# always "biosamples_" not "biosample_"

.PHONY: load-biosamples-into-mongo \
        purge \
        load_acceptable_sized_leaf_bioprojects_into_mongodb \
        flatten_bioprojects \
        flatten_biosamples_ids \
        flatten_biosamples_links \
        flatten_biosample_attributes \
        flatten_biosample_packages \
        biosamples-flattened \
        aggregate-biosample-package-usage

purge:
	rm -rf $(DOWNLOADS_DIR)/biosample_set.xml*
	rm -rf $(LOCAL_DIR)/biosample-count-mongodb.txt
	rm -rf $(LOCAL_DIR)/biosample-last-id-line.txt
	rm -rf $(LOCAL_DIR)/biosample-last-id-val.txt
	rm -rf $(LOCAL_DIR)/biosample_set.xml*
	rm -rf $(LOCAL_DIR)/oversize-bioprojects/*

$(DOWNLOADS_DIR)/biosample_set.xml.gz:
	date
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024
	date

# wget 2 minutes on MAM Ubuntu NUC

$(LOCAL_DIR)/biosample_set.xml: $(DOWNLOADS_DIR)/biosample_set.xml.gz
	date
	gunzip -c $< > $@
	date

# unzip 9 minutes on MAM Ubuntu NUC

# Default file for last ID
LAST_BIOSAMPLE_ID_FILE := $(LOCAL_DIR)/biosample-last-id-val.txt
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

# Only require building the last-id file when the caller hasn't supplied
# LAST_BIOSAMPLE_ID directly. Building it from the 154 GB biosample_set.xml
# is expensive (tac + grep) and uses GNU coreutils' `tac`, which isn't on
# default macOS; supplying LAST_BIOSAMPLE_ID lets users skip both costs.
ifdef LAST_BIOSAMPLE_ID
LAST_ID_PREREQS :=
else
LAST_ID_PREREQS := $(LAST_BIOSAMPLE_ID_FILE)
endif

# These rules generate the ID file, if possible
$(LOCAL_DIR)/biosample-last-id-line.txt: $(LOCAL_DIR)/biosample_set.xml
	@echo "Building $@"
	tac $< | grep -m 1 '<BioSample' > $@

$(LOCAL_DIR)/biosample-last-id-val.txt: $(LOCAL_DIR)/biosample-last-id-line.txt
	@echo "Building $@"
	sed -n 's/.*id="\([0-9]*\)".*/\1/p' $< > $@

load-biosamples-into-mongo: $(LOCAL_DIR)/biosample_set.xml $(LAST_ID_PREREQS)
	@date
	$(eval LAST_BIOSAMPLE_ID_VAL := $(if $(LAST_BIOSAMPLE_ID),$(LAST_BIOSAMPLE_ID),$(shell cat $(LAST_BIOSAMPLE_ID_FILE) 2>/dev/null)))
	@if [ -z "$(LAST_BIOSAMPLE_ID_VAL)" ]; then \
		echo "Error: No LAST_BIOSAMPLE_ID provided and no $(LAST_BIOSAMPLE_ID_FILE) available."; \
		exit 1; \
	fi
	$(eval FINAL_MAX_ELEMENTS := $(if $(MAX_ELEMENTS),$(MAX_ELEMENTS),$(LAST_BIOSAMPLE_ID_VAL)))
	@echo "Using LAST_BIOSAMPLE_ID=$(LAST_BIOSAMPLE_ID_VAL)"
	@echo "Using MAX_ELEMENTS=$(FINAL_MAX_ELEMENTS)"
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) xml-to-mongo \
	  --file-path $< \
	  --collection-name biosamples \
	  --node-type BioSample \
	  --id-field id \
	  --mongo-uri "$(MONGO_URI)" \
	  $(ENV_FILE_OPTION) \
	  --verbose \
	  --max-elements $(FINAL_MAX_ELEMENTS) \
	  --anticipated-last-id $(LAST_BIOSAMPLE_ID_VAL)
	@date

# sample usages:
# make load-biosamples-into-mongo MAX_ELEMENTS=100000
# make load-biosamples-into-mongo \
#    MAX_ELEMENTS=100000 \
#    MONGO_URI="mongodb://localhost:27778/ncbi_metadata?authMechanism=SCRAM-SHA-256&authSource=admin&directConnection=true" \
#    ENV_FILE=local/.env.mongo-ncbi-loadbalancer.mam

# status update frequency is currently hardcoded with "if processed_count % 10000 == 0"

$(LOCAL_DIR)/biosample_xpath_counts.json: $(LOCAL_DIR)/biosample_set.xml
	#  --stop-after 999999999
	# --interval is a number of seconds between updates
	poetry run count-xml-paths \
		--always-count-path '/BioSampleSet/BioSample' \
		--interval 10 \
		--output $@ \
		--xml-file $<

####

$(DOWNLOADS_DIR)/bioproject.xml:
	date
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB March 2025
	date

load_acceptable_sized_leaf_bioprojects_into_mongodb: $(DOWNLOADS_DIR)/bioproject.xml
	# Ensure necessary directories exist
	@mkdir -p $(LOCAL_DIR)/oversize-bioprojects
	@mkdir -p $(DOWNLOADS_DIR)

	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) load-bioprojects-into-mongodb \
       --clear-collections \
       --oversize-dir $(LOCAL_DIR)/oversize-bioprojects \
       --project-collection bioprojects \
       --submission-collection bioprojects_submissions \
       --mongo-uri "$(MONGO_URI)" \
       --verbose \
       --xml-file $< \
       $(ENV_FILE_OPTION)

$(LOCAL_DIR)/bioproject_xpath_counts.json: $(DOWNLOADS_DIR)/bioproject.xml
	# --stop-after 999999999
	poetry run count-xml-paths \
		--always-count-path '/PackageSet/Package/Project' \
		--interval 10 \
		--output $@ \
		--xml-file $<

flatten_bioprojects: mongo-js/flatten_bioprojects_minimal.js
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_bioprojects_minimal.js \
		--verbose && date

flatten_biosamples_ids:
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_biosamples_ids.js \
		--verbose && date

flatten_biosamples_links:
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_biosamples_links.js \
		--verbose && date

flatten_biosample_attributes:
	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) flatten-biosample-attributes \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--source-collection biosamples \
		--target-collection biosamples_attributes \
		--verbose \
		--batch-size 1000
	@date

# index all fields?
# currently have
#biosample_id
#harmonized_name

# IMPORTANT: biosamples_flattened is the collection used by both the
# measurement-discovery pipeline and the env-triads pipeline. Owning the
# target here (rather than in env_triads.Makefile) lets `make -f` invocations
# of NCBI-side aggregators resolve the prereq.
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

aggregate-biosample-package-usage: biosamples-flattened
	@date
	@echo "Aggregating biosample package usage counts..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/aggregate_biosample_package_usage.js \
		--verbose
	@date

# Analyze collection structure complexity (flatness scoring)
# Output: TSV with flatness scores (0-100), useful for identifying export-ready collections
$(LOCAL_DIR)/collection_flatness.tsv:
	@date
	@echo "Analyzing MongoDB collection flatness..."
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) analyze-collection-flatness \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--output-format tsv \
		--output-file $@ \
		--verbose
	@date

