RUN=poetry run
WGET=wget

# todo wget or curl?

downloads/ncbi-biosample-attributes.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/attributes/?format=xml"

downloads/ncbi-biosample-packages.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"

.PHONY: load-packages-into-mongo load-attributes-into-mongo

MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

load-packages-into-mongo: downloads/ncbi-biosample-packages.xml
	date
	$(RUN) xml-to-mongo \
		--anticipated-last-id 250 \
		--collection-name packages \
		--file-path $< \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--node-type Package
	date


load-attributes-into-mongo: downloads/ncbi-biosample-attributes.xml
	date
	$(RUN) xml-to-mongo \
		--anticipated-last-id 1000 \
		--collection-name attributes \
		--file-path $< \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--node-type Attribute
	date

# Extract comprehensive package fields to TSV
local/ncbi_packages_fields.tsv: downloads/ncbi-biosample-packages.xml
	@date
	@echo "Extracting comprehensive NCBI package fields to TSV..."
	@mkdir -p local
	$(RUN) extract-ncbi-packages-fields \
		--xml-file $< \
		--output-file $@
	@date

# Flatten packages collection directly in MongoDB
flatten-packages-collection:
	@date
	@echo "Flattening packages collection directly in MongoDB..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_ncbi_packages.js \
		--verbose
	@date

# Flatten attributes collection directly in MongoDB
flatten-attributes-collection:
	@date
	@echo "Flattening attributes collection directly in MongoDB..."
	$(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_ncbi_attributes.js \
		--verbose
	@date

.PHONY: extract-package-fields flatten-packages-collection flatten-attributes-collection

