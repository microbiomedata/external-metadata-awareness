RUN=poetry run
WGET=wget

MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=ncbi_metadata
MONGO_BIOSAMPLES_COLLECTION=biosamples
BIOSAMPLES_MAX_DOCS=50000000
#BIOSAMPLES_MAX_DOCS=500000 # initial 1%
MONGO2DUCK_BATCH_SIZE=10000

# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running

# todo switch to more consistent mongodb connection strings

# todo add a count from duckdb step

# todo (efficiently) pre-count the number of biosamples in the XML file?

# todo (long term) annotate with more ontologies. uberon is slow. ncbitaxon might take days with this implementation
#   do other normalizations, like quantity values

# todo update dev and user documentation; share database and documentation at NERSC portal
#   document paths not included in duckdb
#   document limitations of using DBeaver with large DuckDBs

# todo warn about conflicting duckdb locks even when both processes are just reading
# todo warn about apparent error messages when creating annotator

# todo reassess duckdb table names

# todo return to generating a wide table?

# todo add poetry CLI aliases for python scripts

# todo what kind of logging/progress indication is really most useful?

# todo parameterize annotation ontologies in new re-annotator script infer_biosample_env_context_obo_curies

# todo add all labels table? or include label in annotation results?

# todo curies_asserted and curies_ner have inconsistent casing for their prefix columns

# todo log don't print

# todo add ranking of re-annotation predicates and prefixes


.PHONY: add-ncbi-biosample-package-attributes \
add-ncbi-biosamples-xml-download-date \
duck-all \
infer-env-triad-curies \
load-biosamples-into-mongo \
purge

duck-all: purge \
local/biosample-last-id-xml.txt \
load-biosamples-into-mongo local/biosample-count-mongodb.txt \
local/ncbi_biosamples.duckdb \
add-ncbi-biosample-package-attributes add-ncbi-biosamples-xml-download-date infer-env-triad-curies

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
		--collection-name $(MONGO_BIOSAMPLES_COLLECTION) \
		--db-name $(MONGO_DB) \
		--file-path $< \
		--id-field id \
		--max-elements $(BIOSAMPLES_MAX_DOCS) \
		--mongo-host $(MONGO_HOST) \
		--mongo-port $(MONGO_PORT)
	date


load-biosamples-into-remote-mongo: local/biosample_set.xml
	date
	$(RUN) xml-to-mongo \
		--file-path $< \
		--id-field id \
		--mongo-uri 'mongodb://localhost:27778/staging?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin' \
		--collection-name biosamples \
		--anticipated-last-id $(BIOSAMPLES_MAX_DOCS) \
		--max-elements $(BIOSAMPLES_MAX_DOCS)
	date

local/biosample-count-mongodb.txt:
	date && mongosh --eval "db.getSiblingDB('$(MONGO_DB)').biosamples.countDocuments()" > $@ && date # 1 minute # how to use Makefile variables here?

# no indexing necessary for the mongodb to duckdb convertion in notebooks/mongodb_biosamples_to_duckdb.ipynb
# 1% MongoDB load 8 minutes on MAM Ubuntu NUC

local/ncbi_biosamples.duckdb:
	date
	$(RUN) mongodb-biosamples-to-duckdb \
		extract \
		--batch_size $(MONGO2DUCK_BATCH_SIZE) \
		--collection $(MONGO_BIOSAMPLES_COLLECTION) \
		--db_name $(MONGO_DB) \
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

#downloads/ncbi-biosample-packages.xml:
#	date
#	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"
#	date

local/ncbi-biosample-packages.tsv: downloads/ncbi-biosample-packages.xml
	$(RUN) extract-ncbi-packages-fields \
		--xml-file $< \
		--output-file $@

add-ncbi-biosample-package-attributes: downloads/ncbi-biosample-packages.xml local/ncbi_biosamples.duckdb
	date
	$(RUN) ncbi-package-info-to-duckdb \
		--db-path $(word 2, $^) \
		--table-name ncbi_package_info \
		--xml-file $(word 1, $^) \
		--overwrite
	date

add-ncbi-biosamples-xml-download-date: local/ncbi_biosamples.duckdb downloads/biosample_set.xml.gz
	$(RUN) add-duckdb-key-value-row \
		--db-path $< \
		--table-name etl_log \
		--key ncbi-biosamples-xml-download-date \
    --value `stat -c %y downloads/biosample_set.xml.gz | cut -d ' ' -f 1`

infer-env-triad-curies: local/ncbi_biosamples.duckdb
	# ~ 15 minutes with envo and po. add bto and uberon: ~ 70 minutes. still running after 24 hours with NCBITaxon.
	date
	$(RUN) infer-biosample-env-context-curies \
		--biosamples-duckdb-file $<
	date

####

SRA_BIGQUERY_PROJECT = nmdc-377118
SRA_BIGQUERY_DATASET = nih-sra-datastore.sra
SRA_BIGQUERY_TABLE = metadata
SRA_BIGQUERY_BATCH_SIZE = 100000
SRA_BIGQUERY_LIMIT = 30000000 # expect ~ 30000000

# Preview mode: analyze the dataset without exporting
biosample-bioproject-preview:
	$(RUN) export-sra-accession-pairs \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--report-nulls \
		--preview \
		--verbose

# Production mode: full export of accession pairs
downloads/sra_accession_pairs.tsv:
	$(RUN) export-sra-accession-pairs \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--batch-size $(SRA_BIGQUERY_BATCH_SIZE) \
		--limit $(SRA_BIGQUERY_LIMIT) \
		--exclude-nulls \
		--output $@

downloads/sra_metadata_table_schema.tsv:
	$(RUN) dump-sra-metadata-schema \
		--project $(SRA_BIGQUERY_PROJECT) \
		--dataset $(SRA_BIGQUERY_DATASET) \
		--table $(SRA_BIGQUERY_TABLE) \
		--output $@ \
		--format tsv

.PHONY: biosample-bioproject-preview sra_accession_pairs_tsv_to_mongo analyze_bioproject_paths load_acceptable_sized_leaf_bioprojects_into_mongodb

sra_accession_pairs_tsv_to_mongo: downloads/sra_accession_pairs.tsv
	$(RUN) sra-accession-pairs-to-mongo \
		--file-path $< \
		--mongo-host $(MONGO_HOST) \
		--mongo-port $(MONGO_PORT)  \
		--database $(MONGO_DB) \
		--collection sra_biosamples_bioprojects \
		--batch-size 100000 \
		--report-interval 500000

load_acceptable_sized_leaf_bioprojects_into_mongodb: downloads/bioproject.xml
	$(RUN) load-bioprojects-into-mongodb \
       --xml-file $< \
       --uri 'mongodb://localhost:27017/ncbi_metadata' \
       --project-collection bioprojects \
       --submission-collection bioprojects_submissions \
       --clear-collections \
       --oversize-dir local/oversize-bioprojects \
       --verbose

load_acceptable_sized_leaf_bioprojects_into_remote_mongodb: downloads/bioproject.xml
	$(RUN) load-bioprojects-into-mongodb \
       --xml-file $< \
       --uri 'mongodb://localhost:27778/ncbi_metadata?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin' \
       --project-collection bioprojects \
       --submission-collection bioprojects_submissions \
       --clear-collections \
       --env-file local/.env.27778.minimal \
       --oversize-dir local/oversize-bioprojects \
       --verbose

local/bioproject_xpath_counts.json: downloads/bioproject.xml
	poetry run count-xml-paths \
		--xml-file $< \
		--interval 10 \
		--always-count-path '/PackageSet/Package/Project' \
		--stop-after 999999999 \
		--output $@

local/bioproject_packageset_xpath_counts.json: downloads/bioproject.xml
	poetry run count-xml-paths \
		--xml-file $< \
		--interval 10 \
		--always-count-path '/PackageSet' \
		--stop-after 999999999 \
		--output $@

local/biosample_xpath_counts.json: local/biosample_set.xml
	poetry run count-xml-paths \
		--xml-file $< \
		--interval 10 \
		--always-count-path '/BioSampleSet/BioSample' \
		--stop-after 999999999 \
		--output $@

downloads/bioproject.xml:
	date
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB March 2025
	date

.PHONY: fetch_sra_metadata_parquet_from_s3_to_perlmutter load_sra_metadata_parquet_into_mongo
# cd into desired directory
fetch_sra_metadata_parquet_from_s3_to_perlmutter: local/sra_metadata_parquet
	shifter --image=amazon/aws-cli:latest aws s3 cp s3://sra-pub-metadata-us-east-1/sra/metadata/ $< --recursive --no-sign-request

load_sra_metadata_parquet_into_mongo: local/sra_metadata_parquet
	# todo may need to fix .env path
	# todo may want to change requests cache location
	$(RUN) sra-parquet-to-mongodb \
		--parquet-dir $< \
		--drop-collection \
		--progress-interval 1000
# [2025-03-21 22:53:08] Completed processing 30 files in 1935.58 minutes. Total inserted: 35567948 records.


.PHONY:  split_env_triad_values_from_perlmutter split_env_triad_values_from_local
split_env_triad_values_from_perlmutter:
	# todo may need to fix .env path
	$(RUN) env-triad-values-splitter \
		--db ncbi_metadata \
		--collection biosamples_env_triad_value_counts_gt_1 \
		--min-length 3

split_env_triad_values_from_local:
	# todo may need to fix .env path
	$(RUN) env-triad-values-splitter \
		--host localhost \
		--port 27017 \
		--db ncbi_metadata \
		--collection biosamples_env_triad_value_counts_gt_1 \
		--no-authenticate \
		--field env_triad_value \
		--min-length 3
