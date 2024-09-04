RUN=poetry run
WGET=wget

# very complex documents; many are too large to load into a MongoDB document
downloads/bioproject.xml:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB August 2024

downloads/biosample_set.xml.gz:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024

local/biosample_set.xml: downloads/biosample_set.xml.gz
	gunzip -c $< > $@

.PHONY: load-biosamples-into-mongo

local/biosample-count-xml.txt: local/biosample_set.xml
	date && grep -c "</BioSample>" $< > $@ && date

# see also https://gitlab.com/wurssb/insdc_metadata
load-biosamples-into-mongo: local/biosample_set.xml
	$(RUN) xml-to-mongo \
		--file-path $< \
		--node-type BioSample \
		--id-field id \
		--db-name biosamples_dev \
		--collection-name biosamples_dev \
		--max-elements 100000 \
		--anticipated-last-id 100000

# see also https://www.npmjs.com/package/mongodb-schema/v/12.2.0?activeTab=versions

#local/mongodb-paths-10pct.txt: # 450000 -> ~ 4 minutes # 4.5 M -> heavy load, never finishes. Use streaming approach?
#	$(RUN) list-mongodb-paths \
#		--db-name ncbi_metadata \
#		--collection samples \
#		--sample-size 4500000 > $@

#local/ncbi_biosamples_inferred_schema.json: # ~ 2 minutes for 410,000 (1%) # ~ 1 hour for 13 million ~ 30%
#	$(RUN) python external_metadata_awareness/infer_schema_with_batching.py \
#		--host localhost \
#		--port 27017 \
#		--database ncbi_metadata \
#		--collection samples \
#		--total-samples 13000000 \
#		--batch-size 50000 \
#		--output $@

local/biosample-count-mongodb.txt:
	# depends on MongoDB having a ncbi_metadata database with a samples collection, running locally, with no access control
	date && mongosh --eval 'db.getSiblingDB("ncbi_metadata").samples.countDocuments()' > $@ && date # 1 minute

local/ncbi-biosamples-packages-counts.tsv: sql/packages-counts.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@

ncbi-biosamples-duckdb-overview:
	$(RUN) python external_metadata_awareness/first_n_attributes_duckdb.py \
		--connection-string "mongodb://localhost:27017/" \
		--db-name ncbi_metadata \
		--collection-name samples \
		--limit 41000000 \
		--batch-size 100000 \
		--duckdb-file local/ncbi_biosamples.duckdb \
		--table-name overview # no path # 40462422 biosamples in ~ 50 minutes

# add counts from duckdb; need to compile duckdb or download binary

ncbi-biosamples-duckdb-attributes:
	$(RUN) python external_metadata_awareness/first_n_attributes_duckdb.py \
		--connection-string "mongodb://localhost:27017/" \
		--db-name ncbi_metadata \
		--collection-name samples \
		--limit 41000000 \
		--batch-size 100000 \
		--duckdb-file local/ncbi_biosamples.duckdb \
		--table-name attributes \
		--path BioSample.Attributes.Attribute

ncbi-biosamples-duckdb-links:
	$(RUN) python external_metadata_awareness/first_n_attributes_duckdb.py \
		--connection-string "mongodb://localhost:27017/" \
		--db-name ncbi_metadata \
		--collection-name samples \
		--limit 41000000 \
		--batch-size 100000 \
		--duckdb-file local/ncbi_biosamples.duckdb \
		--table-name links \
		--path BioSample.Links.Link

  ## @click.option('--path', default="BioSample.Links.Link", required=True,
  ##               help="Path within the document to process (e.g., 'BioSample.Attributes.Attribute').")
  ## @click.option('--path', default="BioSample.Ids.Id", required=True,
  ##               help="Path within the document to process (e.g., 'BioSample.Attributes.Attribute').")
  ## @click.option('--path', default="BioSample.Description.Organism", required=True,
  ##               help="Path within the document to process (e.g., 'BioSample.Attributes.Attribute').")

NCBI_BIOSAMPLES_DUCKDB_PATH = local/ncbi_biosamples.duckdb

local/ncbi-mims-soil-biosamples-env_local_scale.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_local_scale' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

local/ncbi-mims-soil-biosamples-env_broad_scale.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_broad_scale' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

local/ncbi-mims-soil-biosamples-env_medium.csv:
	echo ".mode csv\nSELECT content, COUNT(1) AS sample_count FROM attributes WHERE harmonized_name = 'env_medium' AND package_content = 'MIMS.me.soil.6.0' GROUP BY content ORDER BY COUNT(1) DESC;" | duckdb $(NCBI_BIOSAMPLES_DUCKDB_PATH) > $@

local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv: local/ncbi-mims-soil-biosamples-env_local_scale.csv
	$(RUN) normalize-envo-data \
		--count-col-name sample_count \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@ \
		--val-col-name content

local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv: local/ncbi-mims-soil-biosamples-env_broad_scale.csv
	$(RUN) normalize-envo-data \
		--count-col-name sample_count \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@ \
		--val-col-name content

local/ncbi-mims-soil-biosamples-env_medium-normalized.csv: local/ncbi-mims-soil-biosamples-env_medium.csv
	$(RUN) normalize-envo-data \
		--count-col-name sample_count \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@ \
		--val-col-name content

local/ncbi-mims-soil-biosamples-env_local_scale-failures.csv: local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv
	$(RUN) find-envo-present-no-curie-extracted \
		--input-file $< \
		--output-file $@

local/ncbi-mims-soil-biosamples-env_broad_scale-failures.csv: local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv
	$(RUN) find-envo-present-no-curie-extracted \
		--input-file $< \
		--output-file $@

local/ncbi-mims-soil-biosamples-env_medium-failures.csv: local/ncbi-mims-soil-biosamples-env_medium-normalized.csv
	$(RUN) find-envo-present-no-curie-extracted \
		--input-file $< \
		--output-file $@

local/ncbi-mims-soil-biosamples-env_local_scale-real-labels.csv: local/ncbi-mims-soil-biosamples-env_local_scale-normalized.csv local/envo-info.csv
	$(RUN) merge-in-reference-data \
		--keep-file $(word 1,$^) \
		--keep-key normalized_curie \
		--reference-file $(word 2,$^) \
		--reference-key normalized_curie \
		--reference-addition normalized_label \
		--addition-rename real_label \
		--merged-file $@

local/ncbi-mims-soil-biosamples-env_broad_scale-real-labels.csv: local/ncbi-mims-soil-biosamples-env_broad_scale-normalized.csv local/envo-info.csv
	$(RUN) merge-in-reference-data \
		--keep-file $(word 1,$^) \
		--keep-key normalized_curie \
		--reference-file $(word 2,$^) \
		--reference-key normalized_curie \
		--reference-addition normalized_label \
		--addition-rename real_label \
		--merged-file $@

local/ncbi-mims-soil-biosamples-env_medium-real-labels.csv: local/ncbi-mims-soil-biosamples-env_medium-normalized.csv local/envo-info.csv
	$(RUN) merge-in-reference-data \
		--keep-file $(word 1,$^) \
		--keep-key normalized_curie \
		--reference-file $(word 2,$^) \
		--reference-key normalized_curie \
		--reference-addition normalized_label \
		--addition-rename real_label \
		--merged-file $@

local/ncbi-mims-soil-biosamples-env_local_scale-annotated.tsv: local/ncbi-mims-soil-biosamples-env_local_scale-real-labels.csv
	date ; $(RUN) runoak \
		--input sqlite:obo:envo annotate \
		--matches-whole-text \
		--output-type tsv \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date

local/ncbi-mims-soil-biosamples-env_broad_scale-annotated.tsv: local/ncbi-mims-soil-biosamples-env_broad_scale-real-labels.csv
	date ; $(RUN) runoak \
		--input sqlite:obo:envo annotate \
		--matches-whole-text \
		--output-type tsv \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date

local/ncbi-mims-soil-biosamples-env_medium-annotated.tsv: local/ncbi-mims-soil-biosamples-env_medium-real-labels.csv
	date ; $(RUN) runoak \
		--input sqlite:obo:envo annotate \
		--matches-whole-text \
		--output-type tsv \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date

# from duckdb, with counts
# normalized_curie/real_label and matched_id/matched_label