WGET=wget
RUN=poetry run

# should include everything from Makefiles/

include Makefiles/env_triads.Makefile
include Makefiles/github.Makefile
include Makefiles/gold.Makefile
include Makefiles/mixs.Makefile
include Makefiles/ncbi_biosample_measurements.Makefile
include Makefiles/ncbi_metadata.Makefile
include Makefiles/ncbi_schema.Makefile
include Makefiles/nmdc_metadata.Makefile
include Makefiles/nmdc_schema.Makefile
include Makefiles/sra_metadata.Makefile

local/envo_goldterms.db:
	$(RUN) runoak --input sqlite:obo:envo ontology-metadata --all > /dev/null # ensure semsql file is cached
	$(RUN) runoak --input sqlite:obo:goldterms ontology-metadata --all > /dev/null # ensure semsql file is cached
	cp ~/.data/oaklib/envo.db local/
	poetry run python external_metadata_awareness/sem_sql_combine.py \
		--primary-db local/envo.db \
		--secondary-db ~/.data/oaklib/goldterms.db
	mv local/envo.db $@
