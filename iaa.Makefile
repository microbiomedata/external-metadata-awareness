RUN=poetry run

soil-ebs-with-iaa.csv: Consolidated_soil-env-broad-scale-evidence-table.xlsx-soil-env-broad-scale-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@

soil-em-with-iaa.csv: Consolidated_soil-env-medium-evidence-table.xlsx-soil-env-medium-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@


soil-els-with-iaa.csv: Consolidated_soil-env-local-scale-evidence-table.xlsx-soil-env-local-scale-evidence.csv
	poetry run python iaa.py  \
		--input-file $< \
		--vote-columns CJM_Vote \
		--vote-columns 'MAM vote' \
		--vote-columns MLS_vote \
		--vote-columns NMW_vote \
		--vote-columns SM_vote \
		--output-file $@


