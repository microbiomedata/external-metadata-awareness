RUN=poetry run
WGET=wget

## for env medium
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-3.csv: local/environmental-material-info.txt \
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-2.csv
#	$(RUN) detect-curies-in-subset \
#		--tsv-file $(word 2,$^) \
#		--class-info-file $(word 1,$^)  \
#		--tsv-column-name normalized-curie \
#		--subset-label environmental-material \
#		--output-file $@
#
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-4.csv: local/environmental-material-info.txt \
#local/ncbi-biosamples-context-value-counts-real-labels-only-annotated-3.csv
#	$(RUN) detect-curies-in-subset \
#		--tsv-file $(word 2,$^) \
#		--class-info-file $(word 1,$^)  \
#		--tsv-column-name matched_id \
#		--subset-label environmental_material \
#		--output-file $@
