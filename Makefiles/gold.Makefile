RUN=poetry run

# see also https://github.com/microbiomedata/sample-annotator/blob/b48b62d2cd83d57dff4c56342b4b5bf7154c9ade/make-gold-cache.Makefile

.PHONY: flatten-gold-biosamples

MONGO_URI ?= mongodb://localhost:27017/gold_metadata # this conflicts with earlier imports into the root Makefile, so always user make -f

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --dotenv-path $(ENV_FILE)
endif

local/goldData.xlsx:
	curl -o $@ "https://gold.jgi.doe.gov/download?mode=site_excel"

# The flatten-gold-biosamples target will flatten GOLD biosamples stored in MongoDB and create
# normalized collections with environmental context fields.
#
# It depends on populating a gold_metadata collection with the sample-annotator repo
#
# It performs the following tasks:
# 1. Connects to MongoDB for gold_metadata database
# 2. Flattens each biosample document, especially the environmental fields
# 3. Converts environmental IDs to canonical CURIEs
# 4. Looks up canonical labels and checks for obsolete terms
# 5. Creates flattened_biosamples and flattened_biosample_contacts collections

flatten-gold-biosamples:
	@echo "Using MONGO_URI=$(MONGO_URI)"
	$(RUN) flatten-gold-biosamples \
		$(ENV_FILE_OPTION) \
		--mongo-uri "$(MONGO_URI)" \
		--source-collection biosamples \
		--target-collection flattened_biosamples \
		--contacts-collection flattened_biosample_contacts
