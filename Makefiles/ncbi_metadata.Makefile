RUN=poetry run
WGET=wget

# todo add package info
# todo add taxonomy info?
# todo add readme table with date/time stamp (of XML download ideally)
# todo migrate voting sheet generation code into this repo
# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running


.PHONY:load-biosamples-into-mongo duck-all purge add-ncbi-biosample-package-attributes

purge:
	rm -rf local/biosample_set.xml*

duck-all: purge local/biosample-last-id-xml.txt load-biosamples-into-mongo local/ncbi_biosamples.duckdb

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

MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=biosamples
MONGO_COLLECTION=biosamples
#BIOSAMPLES_MAX_DOCS=50000000
BIOSAMPLES_MAX_DOCS=500000
MONGO2DUCK_BATCH_SIZE=10000

# see also https://gitlab.com/wurssb/insdc_metadata
.PHONY: load-biosamples-into-mongo
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

local/ncbi-biosample-packages.tsv: downloads/ncbi-biosample-packages.xml
	poetry run python external_metadata_awareness/extract_all_ncbi_packages_fields.py \
		--xml-file $< \
		--output-file $@


add-ncbi-biosample-package-attributes: downloads/ncbi-biosample-packages.xml local/biosamples_from_mongo.duckdb
	date
	poetry run python external_metadata_awareness/ncbi_package_info_to_duck_db.py \
		--db-path $(word 2, $^) \
		--table-name ncbi_package_info \
		--xml-file $(word 1, $^) \
		--overwrite
	date


NCBI_BIOSAMPLES_DUCKDB_PATH = local/ncbi_biosamples.duckdb

local/ncbi-mims-soil-biosamples-env_local_scale.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_local_scale' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

local/ncbi-mims-soil-biosamples-env_broad_scale.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_broad_scale' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

local/ncbi-mims-soil-biosamples-env_medium.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_medium' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

#local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv: local/ncbi-mims-soil-biosamples-env_local_scale.csv
#	$(RUN) normalize-envo-data \
#		--count-col-name sample_count \
#		--input-file $< \
#		--ontology-prefix ENVO \
#		--output-file $@ \
#		--val-col-name content
#
#local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv: local/ncbi-mims-soil-biosamples-env_broad_scale.csv
#	$(RUN) normalize-envo-data \
#		--count-col-name sample_count \
#		--input-file $< \
#		--ontology-prefix ENVO \
#		--output-file $@ \
#		--val-col-name content
#
#local/ncbi-mims-soil-biosamples-env_medium-normalized.csv: local/ncbi-mims-soil-biosamples-env_medium.csv
#	$(RUN) normalize-envo-data \
#		--count-col-name sample_count \
#		--input-file $< \
#		--ontology-prefix ENVO \
#		--output-file $@ \
#		--val-col-name content
#
#local/ncbi-mims-soil-biosamples-env_local_scale-failures.csv: local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv
#	$(RUN) find-envo-present-no-curie-extracted \
#		--input-file $< \
#		--output-file $@
#
#local/ncbi-mims-soil-biosamples-env_broad_scale-failures.csv: local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv
#	$(RUN) find-envo-present-no-curie-extracted \
#		--input-file $< \
#		--output-file $@
#
#local/ncbi-mims-soil-biosamples-env_medium-failures.csv: local/ncbi-mims-soil-biosamples-env_medium-normalized.csv
#	$(RUN) find-envo-present-no-curie-extracted \
#		--input-file $< \
#		--output-file $@
#
#local/ncbi-mims-soil-biosamples-env_local_scale-real-labels.csv: local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv local/envo-info.csv
#	$(RUN) merge-in-reference-data \
#		--keep-file $(word 1,$^) \
#		--keep-key normalized_curie \
#		--reference-file $(word 2,$^) \
#		--reference-key normalized_curie \
#		--reference-addition normalized_label \
#		--addition-rename real_label \
#		--merged-file $@
#
#local/ncbi-mims-soil-biosamples-env_broad_scale-real-labels.csv: local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv local/envo-info.csv
#	$(RUN) merge-in-reference-data \
#		--keep-file $(word 1,$^) \
#		--keep-key normalized_curie \
#		--reference-file $(word 2,$^) \
#		--reference-key normalized_curie \
#		--reference-addition normalized_label \
#		--addition-rename real_label \
#		--merged-file $@
#
#local/ncbi-mims-soil-biosamples-env_medium-real-labels.csv: local/ncbi-mims-soil-biosamples-env_medium-normalized.csv local/envo-info.csv
#	$(RUN) merge-in-reference-data \
#		--keep-file $(word 1,$^) \
#		--keep-key normalized_curie \
#		--reference-file $(word 2,$^) \
#		--reference-key normalized_curie \
#		--reference-addition normalized_label \
#		--addition-rename real_label \
#		--merged-file $@
#
#local/ncbi-mims-soil-biosamples-env_local_scale-annotated.tsv: local/ncbi-mims-soil-biosamples-env_local_scale-real-labels.csv
#	date ; $(RUN) runoak \
#		--input sqlite:obo:envo annotate \
#		--matches-whole-text \
#		--output-type tsv \
#		--output $@ \
#		--text-file $< \
#		--match-column normalized_label ; date
#
#local/ncbi-mims-soil-biosamples-env_broad_scale-annotated.tsv: local/ncbi-mims-soil-biosamples-env_broad_scale-real-labels.csv
#	date ; $(RUN) runoak \
#		--input sqlite:obo:envo annotate \
#		--matches-whole-text \
#		--output-type tsv \
#		--output $@ \
#		--text-file $< \
#		--match-column normalized_label ; date
#
#local/ncbi-mims-soil-biosamples-env_medium-annotated.tsv: local/ncbi-mims-soil-biosamples-env_medium-real-labels.csv
#	date ; $(RUN) runoak \
#		--input sqlite:obo:envo annotate \
#		--matches-whole-text \
#		--output-type tsv \
#		--output $@ \
#		--text-file $< \
#		--match-column normalized_label ; date

local/ncbi-biosamples-packages-counts.tsv: sql/packages-counts.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@