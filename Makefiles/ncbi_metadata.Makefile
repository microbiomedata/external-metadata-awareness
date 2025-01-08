RUN=poetry run
WGET=wget

MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=biosamples
MONGO_COLLECTION=biosamples
#BIOSAMPLES_MAX_DOCS=50000000
BIOSAMPLES_MAX_DOCS=500000 # initial 1%
MONGO2DUCK_BATCH_SIZE=10000

# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running

# todo switch to more consistent mongodb connection strings

# todo add a count from duckdb step

# todo add purge of MongoDB

.PHONY: add-ncbi-biosample-package-attributes \
add-ncbi-biosamples-xml-download-date \
duck-all \
load-biosamples-into-mongo \
purge \
re-annotate-biosample-contexts

duck-all: purge \
local/biosample-last-id-xml.txt \
load-biosamples-into-mongo local/biosample-count-mongodb.txt \
local/ncbi_biosamples.duckdb \
add-ncbi-biosample-package-attributes add-ncbi-biosamples-xml-download-date re-annotate-biosample-contexts

purge:
	rm -rf downloads/biosample_set.xml*
	rm -rf downloads/ncbi-biosample-packages.xml
	rm -rf local/biosample-count-mongodb.txt
	rm -rf local/biosample-last-id-xml.txt
	rm -rf local/biosample_set.xml*
	rm -rf local/ncbi-biosample-packages.tsv
	rm -rf local/ncbi_biosamples.duckdb
	@echo "Attempting to delete MongoDB database: $(MONGO_DB)"
	mongosh --quiet --eval "db.getSiblingDB('$(MONGO_DB)').dropDatabase()" || true
	@echo "MongoDB database $(MONGO_DB) deletion attempted."

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

local/biosample-last-id-xml.txt: local/biosample_set.xml
	tac $< | grep -m 1 '<BioSample' > $@

# see also https://gitlab.com/wurssb/insdc_metadata
load-biosamples-into-mongo: local/biosample_set.xml
	date
	$(RUN) xml-to-mongo \
		--anticipated-last-id $(BIOSAMPLES_MAX_DOCS) \
		--collection-name $(MONGO_COLLECTION) \
		--db-name $(MONGO_DB) \
		--file-path $< \
		--id-field id \
		--max-elements $(BIOSAMPLES_MAX_DOCS) \
		--mongo-host $(MONGO_HOST) \
		--mongo-port $(MONGO_PORT)
	date

# no indexing necessary for the mongodb to duckdb convertion in notebooks/mongodb_biosamples_to_duckdb.ipynb
# 1% MongoDB load 8 minutes on MAM Ubuntu NUC

local/ncbi_biosamples.duckdb:
	date
	poetry run python \
		external_metadata_awareness/mongodb_biosamples_to_duckdb.py \
		extract \
		--batch_size $(MONGO2DUCK_BATCH_SIZE) \
		--collection biosamples \
		--db_name biosamples \
		--duckdb_file $@ \
		--max_docs $(BIOSAMPLES_MAX_DOCS) \
		--mongo_uri mongodb://$(MONGO_HOST):$(MONGO_PORT)/
	date
# 1% DuckDB dump started at 2024-12-19T16:11:22; X minutes on MAM Ubuntu NUC
# 2024-12-19T16:45:37.896939: Flushed batch for biosample, total 500000 docs processed for this path so far.
# ~ 14k biosamples/minute
# 800/hour?
# 20 million/day?
# also running many web browser tabs, one PyCharm window, compass (and Zoom for aprt of the time)
# 18GB RAM used; no swappping;
# 1 core in use @ 1 to 3 GHz out of 4.7 GHz max?
# everything on one Samsung SSD 980 PRO, which is supposed to write 5 GB/s. looks like less than 1 MB/s write and wya less read
# CPU bound?

local/biosample-count-mongodb.txt:
	date && mongosh --eval 'db.getSiblingDB("biosamples").biosamples.countDocuments()' > $@ && date # 1 minute

downloads/ncbi-biosample-packages.xml:
	date
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"
	date

local/ncbi-biosample-packages.tsv: downloads/ncbi-biosample-packages.xml
	poetry run python external_metadata_awareness/extract_all_ncbi_packages_fields.py \
		--xml-file $< \
		--output-file $@

add-ncbi-biosample-package-attributes: downloads/ncbi-biosample-packages.xml local/ncbi_biosamples.duckdb
	date
	poetry run python external_metadata_awareness/ncbi_package_info_to_duck_db.py \
		--db-path $(word 2, $^) \
		--table-name ncbi_package_info \
		--xml-file $(word 1, $^) \
		--overwrite
	date

add-ncbi-biosamples-xml-download-date: local/ncbi_biosamples.duckdb
	poetry run python external_metadata_awareness/add_duckdb_key_value_row.py \
		--db-path $< \
		--table-name etl_log \
		--key ncbi-biosamples-xml-download-date \
		--value `stat -c %y downloads/biosample_set.xml.gz | cut -d ' ' -f 1`

re-annotate-biosample-contexts: local/ncbi_biosamples.duckdb
	poetry run biosample-duckdb-reannotation \
		--db-path $< \
		--ontologies envo \
		--ontologies po
