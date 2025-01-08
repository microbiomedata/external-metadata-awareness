WGET=wget
RUN=poetry run

#include Makefiles/env_broad_scale.Makefile
#include Makefiles/soil-env_medium.Makefile
include Makefiles/envo.Makefile
include Makefiles/gold.Makefile
include Makefiles/mixs.Makefile
include Makefiles/ncbi_metadata.Makefile
include Makefiles/ncbi_schema.Makefile
include Makefiles/nmdc_metadata.Makefile
include Makefiles/nmdc_schema.Makefile

# suggested LLM models: gpt-4, gpt-4o, gpt-4-turbo (?), claude-3-opus, claude-3.5-sonnet, gemini-1.5-pro-latest
# gemini models don't seem to take a temperature parameter
# cborg/claude-sonnet
# check cborg for recent model name changes

# NMDC microbiomedata GitHub STUFF

local/envo_goldterms.db:
	$(RUN) runoak --input sqlite:obo:envo ontology-metadata --all > /dev/null # ensure semsql file is cached
	$(RUN) runoak --input sqlite:obo:goldterms ontology-metadata --all > /dev/null # ensure semsql file is cached
	cp ~/.data/oaklib/envo.db local/
	poetry run python external_metadata_awareness/sem_sql_combine.py \
		--primary-db local/envo.db \
		--secondary-db ~/.data/oaklib/goldterms.db
	mv local/envo.db $@


