RUN=poetry run
WGET=wget

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

local/envo-leaves.txt: local/env-local-scale-candidate-ids.txt
	$(RUN) runoak --input sqlite:obo:envo leafs > $@

local/envo-leaf-ids.txt: local/envo-leaves.txt
	cut -f1 -d' ' $< > $@

local/envo-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i continuant > $@ # or .ALL

local/envo-info.csv: local/envo-info.txt
	$(RUN) normalize-envo-data \
			--input-file $< \
			--ontology-prefix ENVO \
			--output-file $@

local/biome-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i ENVO:00000428 > $@

local/unused-terrestrial-biomes-prompt.txt: prompt-templates/unused-terrestrial-biomes-prompt.yaml \
local/soil-env_broad_scale-algebraic.txt local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/biome-relationships.csv
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

local/unused-terrestrial-biomes-response.txt: local/unused-terrestrial-biomes-prompt.txt
	cat $(word 1,$^) | $(RUN) llm prompt --model claude-3.5-sonnet -o temperature 0.01 | tee $@