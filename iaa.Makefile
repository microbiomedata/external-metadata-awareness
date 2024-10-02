RUN=poetry run

env-triad-voting-data/with-iaa/soil-ebs-with-iaa.csv: env-triad-voting-data/consolidated-additional-columns/Consolidated_soil-env-broad-scale-evidence-table-additional-booleans.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

env-triad-voting-data/with-iaa/soil-els-with-iaa.csv: env-triad-voting-data/consolidated-additional-columns/Consolidated_soil-env-local-scale-evidence-table-additional-booleans.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

env-triad-voting-data/with-iaa/soil-em-with-iaa.csv: env-triad-voting-data/consolidated-additional-columns/Consolidated_soil-env-medium-evidence-table-additional-booleans.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

