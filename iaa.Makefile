RUN=poetry run

env-triad-voting-data/with-iaa/soil-ebs-with-iaa.csv: env-triad-voting-data/raw-curated/Consolidated_soil-env-broad-scale-evidence-table.xlsx-soil-env-broad-scale-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

env-triad-voting-data/with-iaa/soil-els-with-iaa.csv: triad-voting-data/raw-curated/Consolidated_soil-env-local-scale-evidence-table.xlsx-soil-env-local-scale-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

env-triad-voting-data/with-iaa/soil-em-with-iaa.csv: triad-voting-data/raw-curated/Consolidated_soil-env-medium-evidence-table.xlsx-soil-env-medium-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

