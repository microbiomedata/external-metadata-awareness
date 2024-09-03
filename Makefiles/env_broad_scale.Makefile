RUN=poetry run
WGET=wget

valid-env_broad_scale-biosample-all: valid-env_broad_scale-biosample-clean \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv \
local/ncbi-biosamples-context-value-counts-failures.csv

valid-env_broad_scale-biosample-clean:
	rm -rf local/biome-info.txt \
		local/envo-info.csv \
		local/envo-info.txt \
		local/ncbi-biosamples-context-value-counts.csv \
		local/ncbi-biosamples-context-value-counts-normalized.csv \
		local/ncbi-biosamples-context-value-counts-real-labels.csv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv \
		local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv

local/ncbi-biosamples-context-value-counts-normalized.csv: local/ncbi-biosamples-context-value-counts.csv # requires SPIN PostgreSQL connection switch to duckdb input
	$(RUN) normalize-envo-data \
		--count-col-name total_count \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@ \
		--val-col-name value

local/ncbi-biosamples-context-value-counts-failures.csv: local/ncbi-biosamples-context-value-counts-normalized.csv
	$(RUN) find-envo-present-no-curie-extracted \
		--input-file $< \
		--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels.csv: local/ncbi-biosamples-context-value-counts-normalized.csv local/envo-info.csv
	$(RUN) merge-in-reference-data \
		--keep-file $(word 1,$^) \
		--keep-key normalized_curie \
		--reference-file $(word 2,$^) \
		--reference-key normalized_curie \
		--reference-addition normalized_label \
		--addition-rename real_label \
		--merged-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv: local/ncbi-biosamples-context-value-counts-real-labels.csv
	date ; $(RUN) runoak \
		--input sqlite:obo:envo annotate \
		--matches-whole-text \
		--output-type tsv \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date



local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv: local/biome-info.txt \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated.tsv
	$(RUN) detect-curies-in-subset \
		--tsv-file $(word 2,$^) \
		--class-info-file $(word 1,$^)  \
		--tsv-column-name normalized_curie \
		--subset-label biome \
		--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv: local/biome-info.txt \
local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-1.tsv
	$(RUN) detect-curies-in-subset \
		--tsv-file $(word 2,$^) \
		--class-info-file $(word 1,$^)  \
		--tsv-column-name matched_id \
		--subset-label biome \
		--output-file $@

local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv: local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.tsv
	$(RUN) or-boolean-columns \
		--input-file $< \
		--output-file $@ \
		--column1 "normalized_curie_biome" \
		--column2 "matched_id_biome"

detected-annotations-to-postgres: local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2-or-ed.tsv
	$(RUN) load-tsv-into-postgres \
	--tsv-file $< \
	--table-name detected_annotations

# REPORT OF WHETHER A BIOSAMPLE USES A BIOME AS IT'S env_broad_scale VALUE
# joins pre-loaded (grouped) detected_annotations table with individual biosample env_broad_scale assertions
local/soil-water-env-broad-scale.tsv: sql/soil-water-env_broad_scale.sql
	$(RUN) sql-to-tsv \
	--sql-file $< \
	--output-file $@
