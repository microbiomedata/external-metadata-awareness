RUN=poetry run
WGET=wget

local/soil-env-medium-evidence-table.tsv: config/soil-env_medium-evidence-config.yaml \
local/EnvMediumSoilEnum-pvs-keys-parsed-unique.csv \
local/nmdc-production-biosamples-soil-env_medium.tsv \
local/ncbi-mims-soil-biosamples-env_medium-annotated.tsv \
local/goldData_biosamples-inferred-soil-env_medium-counts.tsv
	$(RUN) python external_metadata_awareness/extract_value_set_evidence.py \
		--config $< \
		--downsample-uncounted \
		--output-file $@

#.PHONY: aggressive-soil-env-broad-scale-cleanup
#aggressive-soil-env-broad-scale-cleanup:
#	rm -rf local/EnvBroadScaleSoilEnum*
#	rm -rf local/env-package-heterogeneity.tsv
#	rm -rf local/envo-info*
#	rm -rf local/goldData*
#	rm -rf local/goldterms*
#	rm -rf local/ncbi-mims-soil-biosamples-env_broad_scale*
#	rm -rf local/ncbi-mims-soil-biosamples-env_broad_scale-annotated.tsv
#	rm -rf local/nmdc-production-biosamples*
#	rm -rf local/soil-env-broad-scale-evidence-table.tsv
