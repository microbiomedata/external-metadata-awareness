#re-annotate-biosample-contexts:
#	poetry run biosample-duckdb-reannotation \
#		--db-path local/ncbi_biosamples_copy.duckdb \
#		--ontologies bto \
#		--ontologies envo \
#		--ontologies faketest \
#		--ontologies pco \
#		--ontologies po

re-annotate-biosample-contexts:
	poetry run biosample-duckdb-reannotation \
		--db-path local/ncbi_biosamples_copy.duckdb \
		--ontologies envo \
		--ontologies faketest \
		--ontologies pco \
		--ontologies po
