RUN=poetry run
WGET=wget

# todo add package info
# todo add taxonomy info?
# todo add readme table with date/time stamp (of XML download ideally)
# todo migrate voting sheet generation code into this repo
# todo what cpu/ram resources are really required? 4 cores and 128 gb ram in ec2 was probably excessive
#   but 32 gb 2020 macbook pro complains about swapping while running this code if many other "medium" apps are running

.PHONY:

downloads/biosample_set.xml.gz:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024

local/biosample_set.xml: downloads/biosample_set.xml.gz
	date
	gunzip -c $< > $@
	date

local/biosample-last-id-xml.txt: local/biosample_set.xml
	tac $< | grep -m 1 '<BioSample' > $@

# see also https://gitlab.com/wurssb/insdc_metadata
.PHONY: load-biosamples-into-mongo
load-biosamples-into-mongo: local/biosample_set.xml
	$(RUN) xml-to-mongo \
		--anticipated-last-id 43000000 \
		--collection-name biosamples \
		--db-name biosamples \
		--file-path $< \
		--id-field id \
		--max-elements 43000000

# see also https://gitlab.com/wurssb/insdc_metadata
.PHONY: load-biosamples-into-mongo-docker
load-biosamples-into-mongo-docker: local/biosample_set.xml
	date
	$(RUN) xml-to-mongo \
		--anticipated-last-id 50000000 \
		--collection-name biosamples \
		--db-name biosamples \
		--file-path $< \
		--id-field id \
		--max-elements 50000000 \
		--mongo-host mongo \
		--mongo-port 27017
	date

# no indexing necessary for the mongodb to duckdb convertion in notebooks/mongodb_biosamples_to_duckdb.ipynb

local/ncbi_biosamples.duckdb:
	date
	poetry run python \
		external_metadata_awareness/mongodb_biosamples_to_duckdb.py \
		extract \
		--batch_size 10000 \
		--collection biosamples \
		--db_name biosamples \
		--duckdb_file $@ \
		--max_docs 50000000 \
		--mongo_uri mongodb://mongo:27017/
	date

local/biosample-count-mongodb.txt:
	date && mongosh --eval 'db.getSiblingDB("biosamples").biosamples.countDocuments()' > $@ && date # 1 minute

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