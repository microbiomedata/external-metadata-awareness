envo-clean:
	rm -rf local/envo-leaf-ids.txt
	rm -rf local/envo-leaves.txt

env_local_scale-clean:
	rm -rf local/env-local-scale-candidate-ids.txt
	rm -rf local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.png
	rm -rf local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.txt
	rm -rf local/env-local-scale-candidate-non-leaf.txt
	rm -rf local/env-local-scale-candidates.txt
	rm -rf local/mam-individual-exclusion-ids.txt

gold-clean:
	rm -rf local/goldData.xlsx
	rm -rf local/goldData_biosamples-inferred-soil-env_local_scale-counts.tsv
	rm -rf local/goldData_biosamples-inferred-soil-env_local_scale-ids.txt
	rm -rf local/goldData_biosamples-inferred-soil-env_local_scale.tsv
	rm -rf local/goldData_biosamples.csv
	rm -rf local/goldterms-env_local_scale-of-environmental-terrestrial-soil.tsv

ncbi-metadata-clean:
	#rm -rf downloads/biosample_set.xml.gz
	rm -rf local/biosample_set.xml
	rm -rf local/ncbi_biosamples.duckdb
	#rm -rf local/ncbi_biosamples.duckdb.gz

ncbi-schema-inference-clean:
	rm -rf local/biosample-count-mongodb.txt
	rm -rf local/biosample-count-xml.txt
	rm -rf local/mongodb-paths-1pct.txt
	rm -rf local/ncbi_biosamples_inferred_schema.json.10pct.keep
	rm -rf local/ncbi_biosamples_inferred_schema.json.30pct.keep
	rm -rf local/ncbi_metadata_samples_schema_inference_no_values.txt
	rm -rf local/ncbi_metadata_samples_schema_inference.txt

ncbi-schema-clean:
	rm -rf downloads/ncbi-biosample-packages.xml

nmdc-schemas-clean:
	rm -rf downloads/nmdc_submission_schema.yaml

nmdc-metadata-clean:
	rm -rf downloads/nmdc-production-biosamples.json
	rm -rf downloads/nmdc-production-studies.json
	rm -rf local/nmdc-production-biosamples-env-context-columns-counts.tsv
	rm -rf local/nmdc-production-biosamples-env-context-columns-ids.txt
	rm -rf local/nmdc-production-biosamples-env-context-columns.tsv

unorganized-clean:
	rm -rf local/envo_goldterms.db
	rm -rf local/unused-terrestrial-biomes-response.txt
