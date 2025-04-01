RUN=poetry run
WGET=wget

# getting fragments of EnvO because the whole thing is too large to feed into an LLM
# our guideline is that env_broad_scale should be answered with an EnvO biome subclass

# these OAK commands fetch the latest EnvO SQLite file from a BBOP S3 bucket
# it may be a few days behind the envo.owl file form the EnvO GH repo
# use `runoak cache-ls` to see where the SQLite files are cached

local/biome-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships .desc//p=i ENVO:00000428 > $@

local/biome-metadata.yaml:
	$(RUN) runoak --input sqlite:obo:envo term-metadata .desc//p=i ENVO:00000428 > $@
	 # !!! try different formats? or predicate list?

# our guideline is that env_medium should be answered with an EnvO biome subclass
local/environmental-materials-relationships.tsv:
	$(RUN) runoak --input sqlite:obo:envo relationships .desc//p=i ENVO:00010483 > $@

local/environmental-materials-metadata.yaml:
	$(RUN) runoak --input sqlite:obo:envo term-metadata .desc//p=i ENVO:00010483 > $@

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

local/envo-leaves.txt: local/env-local-scale-candidate-ids.txt
	$(RUN) runoak --input sqlite:obo:envo leafs > $@

local/envo-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i continuant > $@ # or .ALL

local/biome-info.txt:
	$(RUN) runoak --input sqlite:obo:envo info  .desc//p=i ENVO:00000428 > $@

local/unused-terrestrial-biomes-prompt.txt: prompt-templates/unused-terrestrial-biomes-prompt.yaml \
local/soil-env_broad_scale-algebraic.txt local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/biome-relationships.csv
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

