RUN=poetry run
WGET=wget

local/water-env-broad-scale-evidence-table.tsv: config/water-env_broad_scale-evidence-config.yaml \
local/biome-ids.tsv \
local/nmdc-production-biosamples-water-env_broad_scale.tsv \
local/ncbi-mims-water-biosamples-env_broad_scale-annotated.tsv \
local/goldData_biosamples-inferred-water-env_broad_scale-counts.tsv
	$(RUN) python external_metadata_awareness/extract_value_set_evidence.py \
		--config $< \
		--output-file $@

.PHONY: aggressive-soil-env-broad-scale-cleanup
aggressive-water-env-broad-scale-cleanup:
	rm -rf local/env-package-heterogeneity.tsv
	rm -rf local/envo-info*
	rm -rf local/goldData*
	rm -rf local/goldterms*
	rm -rf local/ncbi-mims-water-biosamples-env_broad_scale*
	rm -rf local/ncbi-mims-water-biosamples-env_broad_scale-annotated.tsv
	rm -rf local/nmdc-production-biosamples*
	rm -rf local/water-env-broad-scale-evidence-table.tsv
