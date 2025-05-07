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

