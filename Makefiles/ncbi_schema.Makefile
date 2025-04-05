RUN=poetry run
WGET=wget

# find code for converting to table in other repos
# or convert to duckdb
downloads/ncbi-biosample-attributes.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/attributes/?format=xml"

# also mentioned in ncbi_schema.Makefile
downloads/ncbi-biosample-packages.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"

local/ncbi-biosample-packages.csv: downloads/ncbi-biosample-packages.xml
	$(RUN) ncbi-packages-csv-report \
	--xml-file $< \
	--output-file $@

.PHONY: load-packages-into-mongo
load-packages-into-mongo: downloads/ncbi-biosample-packages.xml
	date
	$(RUN) xml-to-mongo \
		--node-type Package \
		--collection-name packages \
		--db-name $(MONGO_DB) \
		--file-path $< \
		--max-elements 999999 \
		--mongo-host $(MONGO_HOST) \
		--mongo-port $(MONGO_PORT)
	date

.PHONY: load-packages-into-mongo
load-attributes-into-mongo: downloads/ncbi-biosample-attributes.xml
	date
	$(RUN) xml-to-mongo \
		--node-type Attribute \
		--collection-name attributes \
		--db-name $(MONGO_DB) \
		--file-path $< \
		--max-elements 999999 \
		--mongo-host $(MONGO_HOST) \
		--mongo-port $(MONGO_PORT)
	date
