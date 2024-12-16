biosamples_from_mongo.duckdb:
	poetry run python \
		external_metadata_awareness/mongodb_biosamples_to_duckdb.py \
		extract \
		--mongo_uri mongodb://localhost:27017/ \
		--db_name biosamples \
		--collection biosamples \
		--duckdb_file $@ \
		--paths BioSample \
		--paths BioSample.Attributes.Attribute \
		--max_docs 5000 \
		--batch_size 1000
