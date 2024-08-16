WGET=wget
RUN=poetry run

# preferable to use a tagged release, but theres good stuff in this commit that hasn't been released yet
MIXS_YAML_URL=https://raw.githubusercontent.com/GenomicsStandardsConsortium/mixs/b0b1e03b705cb432d08914c686ea820985b9cb20/src/mixs/schema/mixs.yaml
SUBMISSION_SCHEMA_URL=https://raw.githubusercontent.com/microbiomedata/submission-schema/v10.7.0/src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml


# very complex documents; many are too large to load into a MongoDB BSON document
downloads/bioproject.xml:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB August 2024

downloads/biosample_set.xml.gz:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024

local/biosample_set.xml: downloads/biosample_set.xml.gz
	gunzip -c $< > $@

# for development
downloads/books.xml:
	$(WGET) -O $@ "https://www.w3schools.com/xml/books.xml"

# 8 years old. seems very incomplete.
downloads/biosample.xsd:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/biosample/biosample.xsd?view=co"

# find code for converting to tabel in other repos
# or convert to duckdb
downloads/ncbi-biosample-attributes.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/attributes/?format=xml"

downloads/ncbi-biosample-packages.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"

local/ncbi-biosample-packages.csv: downloads/ncbi-biosample-packages.xml
	$(RUN) ncbi-packages-csv-report \
	--xml-file $< \
	--output-file $@

local/mongodb-paths-1pct.txt:
	$(RUN) list-mongodb-paths \
		--db-name biosamples \
		--collection biosamples \
		--sample-size 500000 > $@

load-biosamples-into-mongo: local/biosample_set.xml
	$(RUN) xml-to-mongo \
		--file-path $< \
		--node-type BioSample \
		--id-field id \
		--db-name biosamples_dev \
		--collection-name biosamples_dev \
		--max-elements 100000 \
		--anticipated-last-id 100000

# ENVO STUFF
# getting fragments of EnvO because the whole thing is too large to feed into an LLM
# our guideline is that env_broad_scale should be answered with an EnvO biome subclass

# these OAK commands fetch the latest EnvO SQLite file from a BBOP S3 bucket
# it may be a few days behind the envo.owl file form the EnvO GH repo
# use `runoak cache-ls` to see where the SQLite files are cached
local/biome-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships .desc//p=i ENVO:00000428 > $@
	# !!! pivot? include entailment? --include-entailed / --no-include-entailed; --non-redundant-entailed / --no-non-redundant-entailed
	# LLM web interfaces might want CSVs

local/biome-relationships.csv: local/biome-relationships.tsv
	sed 's/\t/,/g' $< > $@
	#awk 'BEGIN {FS="\t"; OFS=","} {print $$0}' $< > $@
	rm -rf $<

local/biome-metadata.yaml:
	$(RUN) runoak --input sqlite:obo:envo term-metadata .desc//p=i ENVO:00000428 > $@
	 # !!! try different formats? or predicate list?

local/biome-metadata.json: local/biome-metadata.yaml
	yq ea '[.]' $< -o=json | cat > $@
	rm -rf $<

# our guideline is that env_medium should be answered with an EnvO biome subclass
local/environmental-materials-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships .desc//p=i ENVO:00010483 > $@

local/environmental-materials-relationships.csv: local/environmental-materials-relationships.tsv
	sed 's/\t/,/g' $< > $@
	rm -rf $<

local/environmental-materials-metadata.yaml:
	$(RUN) runoak --input sqlite:obo:envo term-metadata .desc//p=i ENVO:00010483 > $@

local/environmental-materials-metadata.json: local/environmental-materials-metadata.yaml
	yq ea '[.]' $< -o=json | cat > $@
	rm -rf $<

# the guidance for env_local_scale is less concrete so I am skipping for now.

# MIXS STUFF
downloads/mixs.yaml:
	wget -O $@ $(MIXS_YAML_URL)

# getting fragments of MIxS because the whole thing is too large to feed into an LLM
local/mixs-extensions-with-slots.json: downloads/mixs.yaml
	yq -o=json e '.classes | with_entries(select(.value.is_a == "Extension") | .value |= del(.slot_usage))' $< | cat > $@

local/mixs-extensions.json: downloads/mixs.yaml
	yq -o=json e '.classes | with_entries(select(.value.is_a == "Extension") | .value |= del(.slots, .slot_usage))' $< | cat > $@

local/mixs-extension-unique-slots.json: local/mixs-extensions-with-slots.json
	$(RUN) get-extension-unique-slots \
		--input-file $< \
		--output-file $@

local/mixs-env-triad.json: downloads/mixs.yaml
	yq -o=json e '{"slots": {"env_broad_scale": .slots.env_broad_scale, "env_local_scale": .slots.env_local_scale, "env_medium": .slots.env_medium}}' $< | cat > $@

# NMDC SCHEMA STUFF
downloads/nmdc_submission_schema.yaml:
	wget -O $@ $(SUBMISSION_SCHEMA_URL)

local/established-value-sets-from-submission-schema.json: downloads/nmdc_submission_schema.yaml
	yq -o=json e '{"enums": {"EnvBroadScaleSoilEnum": .enums.EnvBroadScaleSoilEnum, "EnvLocalScaleSoilEnum": .enums.EnvLocalScaleSoilEnum, "EnvMediumSoilEnum": .enums.EnvMediumSoilEnum}}' $< | cat > $@ # ~ 48

local/nmdc-submission-schema-enums-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums | keys | .[]' $< | sort  > $@

local/EnvBroadScaleSoilEnum-pvs-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums.EnvBroadScaleSoilEnum.permissible_values | keys | .[]' $< | cat > $@

local/EnvBroadScaleSoilEnum-pvs-keys-parsed.csv: local/EnvBroadScaleSoilEnum-pvs-keys.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv: local/EnvBroadScaleSoilEnum-pvs-keys-parsed.csv
	cut -f3,4 -d, $< | head -n 1 > $<.header.csv
	tail -n +2 $< | cut -f3,4 -d, | sort | uniq > $@.tmp
	cat $<.header.csv $@.tmp > $@
	rm -rf $<.header.csv $@.tmp

# NMDC METADATA STUFF
downloads/nmdc-production-studies.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/study_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

downloads/nmdc-production-biosamples.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-5pct.json: downloads/nmdc-production-biosamples.json
	$(RUN) random-sample-resources \
		--input-file $< \
		--output-file $@ \
		--sample-percentage 5

local/nmdc-production-biosamples-json-to-context.tsv: downloads/nmdc-production-biosamples.json
	$(RUN) biosample-json-to-context-tsv \
		--input-file $< \
		--output-file $@

####

# biosamples that are part of a particular study
downloads/sty-11-ev70y104_biosamples.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/biosample_set?filter=%7B%22part_of%22%3A%20%22nmdc%3Asty-11-ev70y104%22%7D&max_page_size=999999'
	yq -o=json e '.resources' $@.bak | cat > $@
	rm -rf $@.bak

# metadata about a particular study
downloads/sty-11-ev70y104_study.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/ids/nmdc%3Asty-11-ev70y104'
	yq -o=json e '.' $@.bak | cat > $@
	rm -rf $@.bak


####

local/environmental-material-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i ENVO:00010483 > $@

local/aquatic-biome-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i ENVO:00002030 > $@

#local/aquatic-biome-info.tsv:
#	$(RUN) runoak --input sqlite:obo:envo info --output-type tsv --output $@ .desc//p=i ENVO:00002030
#
#local/aquatic-biome-tree.txt:
#	$(RUN) runoak --input sqlite:obo:envo tree --gap-fill .desc//p=i ENVO:00002030 > $@

local/aquatic-biome-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships --output-type tsv --output $@ .desc//p=i ENVO:00002030

local/aquatic-biome-viz.png:
	$(RUN) runoak --input sqlite:obo:envo viz --no-view --output $@ --gap-fill .desc//p=i ENVO:00002030

local/biome-minus-aquatic.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i ENVO:00000428  .not .desc//p=i ENVO:00002030 > $@ # ~ 72

#local/biome-minus-aquatic.tsv: # includes lots of columns, but ids are wrapped in arrays
#	$(RUN) runoak --input sqlite:obo:envo info --output-type tsv  .desc//p=i ENVO:00000428 .not .desc//p=i ENVO:00002030  > $@

local/ncbi-biosamples-packages-counts.tsv: sql/packages-counts.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@

local/nmdc-production-biosamples-env-package.json:
	curl -X 'GET' \
		'https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999&projection=env_package' \
		-H 'accept: application/json' > $@.bak
	yq '.resources' -o=json $@.bak | cat > $@ # ENVO:00001998 is also soil
	rm -rf $@.bak

####

valid-env_broad_scale-biosample-all: valid-env_broad_scale-biosample-clean \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv \
local/ncbi-biosamples-context-value-counts-failures.csv

valid-env_broad_scale-biosample-clean:
	rm -rf local/biome-info.txt \
		local/envo-info.csv \
		local/envo-info.txt \
		local/ncbi-biosamples-context-value-counts.csv \
		local/ncbi-biosamples-context-value-counts-normalized.csv \
		local/ncbi-biosamples-context-value-counts-real-labels.csv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv

local/ncbi-biosamples-context-value-counts.csv:
	$(RUN) count-biosample-context-vals-from-postgres \
		--output-file $@ \
		--min-count 2

local/ncbi-biosamples-context-value-counts-normalized.csv: local/ncbi-biosamples-context-value-counts.csv
	$(RUN) normalize-envo-data \
		--count-col-name total_count \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@ \
		--val-col-name value

local/ncbi-biosamples-context-value-counts-failures.csv: local/ncbi-biosamples-context-value-counts-normalized.csv
	$(RUN) find-envo-present-no-curie-extracted \
		--input-file $< \
		--output-file $@

local/envo-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i continuant > $@ # or .ALL

local/envo-info.csv: local/envo-info.txt
	$(RUN) normalize-envo-data \
			--input-file $< \
			--ontology-prefix ENVO \
			--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels.csv: local/ncbi-biosamples-context-value-counts-normalized.csv local/envo-info.csv
	$(RUN) merge-in-reference-data \
		--keep-file $(word 1,$^) \
		--keep-key normalized_curie \
		--reference-file $(word 2,$^) \
		--reference-key normalized_curie \
		--reference-addition normalized_label \
		--addition-rename real_label \
		--merged-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv: local/ncbi-biosamples-context-value-counts-real-labels.csv
	date ; $(RUN) runoak \
		--input sqlite:obo:envo annotate \
		--matches-whole-text \
		--output-type tsv \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date

local/biome-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i ENVO:00000428 > $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv: local/biome-info.txt \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv
	$(RUN) detect-curies-in-subset \
		--tsv-file $(word 2,$^) \
		--class-info-file $(word 1,$^)  \
		--tsv-column-name normalized_curie \
		--subset-label biome \
		--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv: local/biome-info.txt \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv
	$(RUN) detect-curies-in-subset \
		--tsv-file $(word 2,$^) \
		--class-info-file $(word 1,$^)  \
		--tsv-column-name matched_id \
		--subset-label biome \
		--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv: local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv
	$(RUN) or-boolean-columns \
		--input-file $< \
		--output-file $@ \
		--column1 "normalized_curie_biome" \
		--column2 "matched_id_biome"

## for env medium
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-3.csv: local/environmental-material-info.txt \
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.csv
#	$(RUN) detect-curies-in-subset \
#		--tsv-file $(word 2,$^) \
#		--class-info-file $(word 1,$^)  \
#		--tsv-column-name normalized-curie \
#		--subset-label environmental-material \
#		--output-file $@
#
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-4.csv: local/environmental-material-info.txt \
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-3.csv
#	$(RUN) detect-curies-in-subset \
#		--tsv-file $(word 2,$^) \
#		--class-info-file $(word 1,$^)  \
#		--tsv-column-name matched_id \
#		--subset-label environmental_material \
#		--output-file $@

detected-annotations-to-postgres: local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv
	$(RUN) load-tsv-into-postgres \
	--tsv-file $< \
	--table-name detected_annotations

# joins pre-loaded (grouped) detected_annotations table with individual biosample env_broad_scale assertions
local/soil-water-env-broad-scale.tsv: sql/soil-water-env_broad_scale.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@

#####

local/unused-terrestrial-biomes-prompt.txt: prompt-templates/unused-terrestrial-biomes-prompt.yaml \
local/biome-minus-aquatic.txt local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/biome-relationships.csv
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

# suggested models: gpt-4, gpt-4o, gpt-4-turbo (?), claude-3-opus, claude-3.5-sonnet, gemini-1.5-pro-latest
# gemini models don't seem to take a temperature parameter
local/unused-terrestrial-biomes-response.txt: local/unused-terrestrial-biomes-prompt.txt
	cat $(word 1,$^) | $(RUN) llm prompt --model 4o  -o temperature 0.01 | tee $@

####

local/microbiomedata-repos.csv:
	. ./report-microbiomedata-repos.sh > $@
