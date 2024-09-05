WGET=wget
RUN=poetry run

include Makefiles/env_broad_scale.Makefile
#include Makefiles/env_broad_scale.Makefile
#include Makefiles/soil-env_medium.Makefile
include Makefiles/envo.Makefile
include Makefiles/gold.Makefile
include Makefiles/mixs.Makefile
include Makefiles/ncbi_metadata.Makefile
include Makefiles/ncbi_schema.Makefile
include Makefiles/nmdc_metadata.Makefile
include Makefiles/nmdc_schema.Makefile
include Makefiles/soil-env_broad_scale.Makefile
include Makefiles/soil-env_local_scale.Makefile
include Makefiles/soil-env_medium.Makefile

# suggested LLM models: gpt-4, gpt-4o, gpt-4-turbo (?), claude-3-opus, claude-3.5-sonnet, gemini-1.5-pro-latest
# gemini models don't seem to take a temperature parameter
# cborg/claude-sonnet
# check cborg for recent model name changes

# NMDC microbiomedata GitHub STUFF
local/microbiomedata-repos.csv:
	. ./report-microbiomedata-repos.sh > $@

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

local/EnvBroadScaleSoilEnum.png: local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv
	cat $< | tail -n +2  | cut -f1 -d, > $@.ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --no-view --output $@ --gap-fill [ .idfile $@.ids.txt ] .or biome
	rm -rf $@.ids.txt

local/EnvMediumSoilEnum-pvs-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums.EnvMediumSoilEnum.permissible_values | keys | .[]' $< | cat > $@

local/EnvMediumSoilEnum-pvs-keys-parsed.csv: local/EnvMediumSoilEnum-pvs-keys.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/EnvMediumSoilEnum-pvs-keys-parsed-unique.csv: local/EnvMediumSoilEnum-pvs-keys-parsed.csv
	cut -f3,4 -d, $< | head -n 1 > $<.header.csv
	tail -n +2 $< | cut -f3,4 -d, | sort | uniq > $@.tmp
	cat $<.header.csv $@.tmp > $@
	rm -rf $<.header.csv $@.tmp

local/EnvMediumSoilEnum.png: local/EnvMediumSoilEnum-pvs-keys-parsed-unique.csv
	cat $< | tail -n +2  | cut -f1 -d, > $@.ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --gap-fill --no-view --output $@ .idfile $@.ids.txt
	rm -rf $@.ids.txt

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

local/nmdc-production-biosamples-env-package.json:
	curl -X 'GET' \
		'https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999&projection=env_package' \
		-H 'accept: application/json' > $@.bak
	yq '.resources' -o=json $@.bak | cat > $@ # ENVO:00001998 is also soil
	rm -rf $@.bak

local/nmdc-production-studies-images.csv: downloads/nmdc-production-studies.json
	$(RUN) python external_metadata_awareness/study-image-table.py \
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

detected-annotations-to-postgres: local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv
	$(RUN) load-tsv-into-postgres \
	--tsv-file $< \
	--table-name detected_annotations
local/envo_goldterms.db:
	$(RUN) runoak --input sqlite:obo:envo ontology-metadata --all > /dev/null # ensure semsql file is cached
	$(RUN) runoak --input sqlite:obo:goldterms ontology-metadata --all > /dev/null # ensure semsql file is cached
	cp ~/.data/oaklib/envo.db local/
	poetry run python external_metadata_awareness/sem_sql_combine.py \
		--primary-db local/envo.db \
		--secondary-db ~/.data/oaklib/goldterms.db
	mv local/envo.db $@
