RUN=poetry run
WGET=wget

local/soil-env-broad-scale-evidence-table.tsv: config/soil-env_broad_scale-evidence-config.yaml \
local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv \
local/nmdc-production-biosamples-soil-env_broad_scale.tsv \
local/ncbi-mims-soil-biosamples-env_broad_scale-annotated.tsv \
local/goldData_biosamples-inferred-soil-env_broad_scale-counts.tsv
	$(RUN) python external_metadata_awareness/extract_value_set_evidence.py \
		--config $< \
		--downsample-uncounted \
		--output-file $@

.PHONY: aggressive-soil-env-broad-scale-cleanup
aggressive-soil-env-broad-scale-cleanup:
	rm -rf local/EnvBroadScaleSoilEnum*
	rm -rf local/env-package-heterogeneity.tsv
	rm -rf local/envo-info*
	rm -rf local/goldData*
	rm -rf local/goldterms*
	rm -rf local/ncbi-mims-soil-biosamples-env_broad_scale*
	rm -rf local/ncbi-mims-soil-biosamples-env_broad_scale-annotated.tsv
	rm -rf local/nmdc-production-biosamples*
	rm -rf local/soil-env-broad-scale-evidence-table.tsv