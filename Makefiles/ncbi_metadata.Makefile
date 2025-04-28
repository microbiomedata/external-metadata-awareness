RUN=poetry run
WGET=wget

# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running

# todo update dev and user documentation; share database and documentation at NERSC portal

# todo return to generating a wide table?

# todo add poetry CLI aliases for python scripts

# todo what kind of logging/progress indication is really most useful?

# todo log don't print

.PHONY: add-ncbi-biosample-package-attributes \
        add-ncbi-biosamples-xml-download-date \
        infer-env-triad-curies \
        load-biosamples-into-mongo \
        purge \
        split-env-triad-values

purge:
	rm -rf downloads/biosample_set.xml*
	rm -rf local/biosample-count-mongodb.txt
	rm -rf local/biosample-last-id-line.txt
	rm -rf local/biosample-last-id-val.txt
	rm -rf local/biosample_set.xml*
	rm -rf local/oversize-bioprojects/*

downloads/biosample_set.xml.gz:
	date
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024
	date

# wget 2 minutes on MAM Ubuntu NUC

local/biosample_set.xml: downloads/biosample_set.xml.gz
	date
	gunzip -c $< > $@
	date

# unzip 9 minutes on MAM Ubuntu NUC


# Default file for last ID
LAST_BIOSAMPLE_ID_FILE := local/biosample-last-id-val.txt
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

# These rules generate the ID file, if possible
local/biosample-last-id-line.txt: local/biosample_set.xml
	@echo "Building $@"
	tac $< | grep -m 1 '<BioSample' > $@

local/biosample-last-id-val.txt: local/biosample-last-id-line.txt
	@echo "Building $@"
	sed -n 's/.*id="\([0-9]*\)".*/\1/p' $< > $@

load-biosamples-into-mongo: local/biosample_set.xml
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

local/biosample_xpath_counts.json: local/biosample_set.xml
	#  --stop-after 999999999
	# --interval is a number of seconds between updates
	poetry run count-xml-paths \
		--always-count-path '/BioSampleSet/BioSample' \
		--interval 10 \
		--output $@ \
		--xml-file $<

####

downloads/bioproject.xml:
	date
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB March 2025
	date

load_acceptable_sized_leaf_bioprojects_into_mongodb: downloads/bioproject.xml
	# Ensure necessary directories exist
	@mkdir -p local/oversize-bioprojects
	@mkdir -p downloads

	@date
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) load-bioprojects-into-mongodb \
       --clear-collections \
       --oversize-dir local/oversize-bioprojects \
       --project-collection bioprojects \
       --submission-collection bioprojects_submissions \
       --uri $(MONGO_URI) \
       --verbose \
       --xml-file $< \
       $(ENV_FILE_OPTION)

local/bioproject_xpath_counts.json: downloads/bioproject.xml
	# --stop-after 999999999
	poetry run count-xml-paths \
		--always-count-path '/PackageSet/Package/Project' \
		--interval 10 \
		--output $@ \
		--xml-file $<

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
