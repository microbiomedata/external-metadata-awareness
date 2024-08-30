WGET=wget
RUN=poetry run

# preferable to use a tagged release, but theres good stuff in this commit that hasn't been released yet
MIXS_YAML_URL=https://raw.githubusercontent.com/GenomicsStandardsConsortium/mixs/b0b1e03b705cb432d08914c686ea820985b9cb20/src/mixs/schema/mixs.yaml
SUBMISSION_SCHEMA_URL=https://raw.githubusercontent.com/microbiomedata/submission-schema/v10.7.0/src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml

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

local/environmental-material-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i ENVO:00010483 > $@

local/aquatic-biome-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i ENVO:00002030 > $@  # --output-type tsv has lots of info but wrapped in square brackets

local/aquatic-biome-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships --output-type tsv --output $@ .desc//p=i ENVO:00002030

local/aquatic-biome.png:
	$(RUN) runoak --input sqlite:obo:envo viz --no-view --output $@ --gap-fill .desc//p=i ENVO:00002030

local/soil-env_broad_scale-algebraic.txt:
	$(RUN) runoak --input sqlite:obo:envo info [ [ [ [ [ .desc//p=i biome .not .desc//p=i 'aquatic biome' ] .not .desc//p=i 'forest biome' ] .not .desc//p=i 'grassland biome' ]  .not .desc//p=i 'desert biome' ] .not biome ]  .not 'cropland biome' > $@

local/soil-env_broad_scale-algebraic.csv: local/soil-env_broad_scale-algebraic.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@


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


# REPORT OF WHETHER A BIOSAMPLE USES A BIOME AS IT'S env_broad_scale VALUE
# joins pre-loaded (grouped) detected_annotations table with individual biosample env_broad_scale assertions
local/soil-water-env-broad-scale.tsv: sql/soil-water-env_broad_scale.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@

####

local/unused-terrestrial-biomes-prompt.txt: prompt-templates/unused-terrestrial-biomes-prompt.yaml \
local/soil-env_broad_scale-algebraic.txt local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/biome-relationships.csv
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

# suggested models: gpt-4, gpt-4o, gpt-4-turbo (?), claude-3-opus, claude-3.5-sonnet, gemini-1.5-pro-latest
# gemini models don't seem to take a temperature parameter
# cborg/claude-sonnet
local/unused-terrestrial-biomes-response.txt: local/unused-terrestrial-biomes-prompt.txt
	cat $(word 1,$^) | $(RUN) llm prompt --model claude-3.5-sonnet -o temperature 0.01 | tee $@

####

#local/env-local-scale-candidates.txt:
#	$(RUN) runoak --input sqlite:obo:envo info [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ [ .desc//p=i 'material entity' ] .not .desc//p=i 'biome' ] .not .desc//p=i 'environmental material' ] .not .desc//p=i 'chemical entity' ] .not .desc//p=i 'organic material' ] .not .desc//p=i 'anatomical entity' ] .not .desc//p=i 'organism' ] .not .desc//p=i 'plant anatomical entity' ] .not .desc//p=i 'healthcare facility' ] .not .desc//p=i 'fluid layer' ] .not .desc//p=i 'interface layer' ] .not .desc//p=i 'manufactured product' ] .not .desc//p=i 'anatomical entity environment' ] .not .desc//p=i 'ecosystem' ] .not .desc//p=i 'area protected according to IUCN guidelines' ] .not .desc//p=i 'astronomical body' ] .not .desc//p=i 'astronomical object' ] .not .desc//p=i 'cloud' ] .not .desc//p=i 'collection of organisms' ] .not .desc//p=i 'environmental system' ] .not .desc//p=i 'ecozone' ] .not .desc//p=i 'environmental zone' ] .not .desc//p=i 'water current' ] .not .desc//p=i 'mass of environmental material' ] .not .desc//p=i 'subatomic particle' ] .not .desc//p=i 'observing system' ] .not .desc//p=i 'particle' ] .not .desc//p=i 'planetary structural layer' ] .not .desc//p=i 'political entity' ] .not .desc//p=i 'meteor' ] .not .desc//p=i 'room' ] .not .desc//p=i 'transport feature' ] .not .desc//p=i 'mass of liquid' ] .not .desc//p=RO:0001025 'water body' ] .not .desc//p=BFO:0000050 'environmental monitoring area' ] .not .desc//p=BFO:0000050 'marine littoral zone' ] .not .desc//p=BFO:0000050 'marine environmental zone' ] .not .desc//p=RO:0002473 'sea floor' ] .not .desc//p=BFO:0000050 'saline water' ] .not .desc//p=BFO:0000050 'ice' ] .not .desc//p=RO:0001025 'water body' ] .not .desc//p=i 'administrative region' ] .not .desc//p=i 'protected area' ] .not .desc//p=i 'channel of a watercourse' ] .not .desc//p=i 'cryospheric layer' ] .not 'l~gaseous' ] .not 'l~marine' ] .not .desc//p=i 'material isosurface' ] .not 'l~undersea' ] .not .desc//p=i NCBITaxon:1 ] .not 'l~saline' ] .not 'l~brackish' ] .not .desc//p=i 'aeroform' > $@
# REPORT OF WHETHER A BIOSAMPLE USES A BIOME AS IT'S env_broad_scale VALUE
# joins pre-loaded (grouped) detected_annotations table with individual biosample env_broad_scale assertions
local/soil-water-env-broad-scale.tsv: sql/soil-water-env_broad_scale.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@

####

local/unused-terrestrial-biomes-prompt.txt: prompt-templates/unused-terrestrial-biomes-prompt.yaml \
local/soil-env_broad_scale-algebraic.txt local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/biome-relationships.csv
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

# suggested models: gpt-4, gpt-4o, gpt-4-turbo (?), claude-3-opus, claude-3.5-sonnet, gemini-1.5-pro-latest
# gemini models don't seem to take a temperature parameter
# cborg/claude-sonnet
local/unused-terrestrial-biomes-response.txt: local/unused-terrestrial-biomes-prompt.txt
	cat $(word 1,$^) | $(RUN) llm prompt --model claude-3.5-sonnet -o temperature 0.01 | tee $@

####

# remove .desc//p=BFO:0000050 'marine littoral zone' .or .desc//p=BFO:0000050 'saline water' .or .desc//p=RO:0001025 'water body' .or .desc//p=RO:0001025 'water body' .or .desc//p=RO:0002473 ' because of .or 'l~marine'
# remove .or .desc//p=i 'organic material' because of .or .desc//p=i 'environmental material'
# remove .or .desc//p=i 'mass of liquid' because of .or .desc//p=i 'mass of environmental material'
# removed  .or .desc//p=i NCBITaxon:1 because of .or .desc//p=i 'organism'
# .or .desc//p=i 'organic material' (.desc//p=i 'environmental material')
# .or .desc//p=i 'gas planet' (.desc//p=i 'environmental material')

local/env-local-scale-candidates-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships .desc//p=i 'material entity' .not [ .desc//p=i 'biome' .or .desc//p=i 'environmental material'  .or .desc//p=i 'meteorite'  .or .desc//p=i 'chemical entity' .or .desc//p=i 'organic material' .or .desc//p=i 'anatomical entity' .or .desc//p=i 'organism'  .or .desc//p=i 'plant anatomical entity'  .or .desc//p=i 'healthcare facility'  .or .desc//p=i 'fluid layer'  .or .desc//p=i 'interface layer'  .or .desc//p=i 'manufactured product'  .or .desc//p=i 'anatomical entity environment'  .or .desc//p=i 'ecosystem'  .or .desc//p=i 'area protected according to IUCN guidelines'  .or .desc//p=i 'astronomical body'  .or .desc//p=i 'astronomical object'  .or .desc//p=i 'cloud'  .or .desc//p=i 'collection of organisms'  .or .desc//p=i 'environmental system'  .or .desc//p=i 'ecozone'  .or .desc//p=i 'environmental zone'  .or .desc//p=i 'water current'  .or .desc//p=i 'mass of environmental material'  .or .desc//p=i 'subatomic particle'  .or .desc//p=i 'observing system'  .or .desc//p=i 'particle'  .or .desc//p=i 'planetary structural layer'  .or .desc//p=i 'political entity'  .or .desc//p=i 'meteor'  .or .desc//p=i 'room'  .or .desc//p=i 'transport feature'  .or .desc//p=i 'mass of liquid'  .or .desc//p=RO:0001025 'water body'  .or .desc//p=BFO:0000050 'environmental monitoring area'  .or .desc//p=BFO:0000050 'marine littoral zone'  .or .desc//p=BFO:0000050 'marine environmental zone'  .or .desc//p=RO:0002473 'sea floor'  .or .desc//p=BFO:0000050 'saline water'  .or .desc//p=BFO:0000050 'ice'  .or .desc//p=RO:0001025 'water body'  .or .desc//p=i 'administrative region'  .or .desc//p=i 'protected area'  .or .desc//p=i 'channel of a watercourse'  .or .desc//p=i 'cryospheric layer'  .or 'l~gaseous'  .or 'l~marine'  .or .desc//p=i 'material isosurface'  .or 'l~undersea'  .or .desc//p=i NCBITaxon:1  .or 'l~saline'  .or 'l~brackish'  .or .desc//p=i 'aeroform' ] > $@

local/envo-leaves.txt:
	$(RUN) runoak --input sqlite:obo:envo leafs > $@

local/envo-leaf-ids.txt: local/envo-leaves.txt
	cut -f1 -d' ' $< > $@

local/env-local-scale-candidate-ids.txt: local/env-local-scale-candidates.txt
	cut -f1 -d' ' $< > $@

local/env-local-scale-non-leaf.txt: local/env-local-scale-candidates.txt local/envo-leaf-ids.txt
	$(RUN) runoak --input sqlite:obo:envo info .idfile $(word 1,$^) .not [ .idfile $(word 2,$^) ] > $@

local/env-local-scale-non-leaf.csv: local/env-local-scale-non-leaf.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/env-local-scale-non-leaf.png: local/env-local-scale-candidates.txt local/envo-leaf-ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --gap-fill .idfile $(word 1,$^) .not [ .idfile $(word 2,$^) ]


###### SIERRA's STUFF #######

# local/env-local-scale-candidates.txt:
#	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i 'material entity' .not [ .desc//p=i 'biome'.or .desc//p=i 'environmental material' .or .desc//p=i 'anatomical entity' .or .desc//p=i 'chemical entity' .or .desc//p=i 'environmental system' .or .desc//p=i 'administrative region' .or .desc//p=i 'aeroform' .or .desc//p=i 'anatomical entity environment' .or .desc//p=i 'area protected according to IUCN guidelines' .or .desc//p=i 'astronomical object' .or .desc//p=i 'building part' .or .desc//p=i 'channel of a watercourse' .or .desc//p=i 'collection of organisms' .or .desc//p=i 'cryospheric layer' .or .desc//p=i 'ecozone' .or .desc//p=i 'environmental monitoring area' .or .desc//p=i 'fluid layer'  .or .desc//p=i 'healthcare facility' .or .desc//p=i 'interface layer' .or .desc//p=i 'manufactured product' .or .desc//p=i 'mass of biological material' .or .desc//p=i 'mass of fluid' .or .desc//p=i 'material isosurface' .or .desc//p=i 'meteor' .or .desc//p=i 'meteorite' .or .desc//p=i 'observing system' .or .desc//p=i 'organic object' .or .desc//p=i 'organism' .or .desc//p=i 'particle' .or .desc//p=i 'piece of plastic' .or .desc//p=i 'piece of rock' .or .desc//p=i 'planetary structural layer' .or .desc//p=i 'plant anatomical entity' .or .desc//p=i 'political entity' .or .desc//p=i 'protected area' .or .desc//p=i 'subatomic particle' .or .desc//p=i 'transport feature' .or .desc//p=i 'water current' .or .desc//p=i,p 'l~undersea' ] .or bridge .or road .or 'wildlife management area' .or .desc//p=i 'lake layer' .or .desc//p=i island > $@

generate-env-local-scale-candidates:
	# Ensure the poetry environment is activated and run the script with the specified config
	$(RUN) python external_metadata_awareness/envo_local_scale_extraction.py \
           --oak-config-file config/oak-config.yaml \
           --extraction-config-file config/env-local-scale-extraction-config.yaml

test:
	$(RUN) pytest tests/*
###### END SIERRA's STUFF #######
