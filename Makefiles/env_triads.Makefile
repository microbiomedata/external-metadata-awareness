MONGO_DB = ncbi_metadata
MONGO_HOST = localhost
MONGO_PORT = 27017
MONGO_COMMAND = mongosh
RUN = poetry run

.PHONY: count-harmonizable-attribs purge-derived-repos

# make load-biosamples-into-mongo
# Processed 44750000 BioSample nodes (95.56%), elapsed time: 34960.22 seconds
  #date
  #Sat Apr  5 21:12:43 EDT 2025


count-harmonizable-attribs: mongo-js/count_harmonizable_biosample_attribs.js
	date
	@echo "Ensuring index on Attributes.Attribute.harmonized_name..."
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.biosamples.createIndex({"Attributes.Attribute.harmonized_name": 1})' # 30? minutes
	@echo "Running aggregation script..."
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet $<  # 30? minutes
	date

purge-derived-repos:
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.biosamples_env_triad_value_counts_gt_1.drop()'
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.env_triad_component_labels.drop()'
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.env_triad_component_curies_uc.drop()'

env-triads: # depends on biosamples_flattened, created from the biosamples collection with flatten_biosamples.js
#	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) mongo-js/flatten_biosamples.js # 1770.18 real
#	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
#		'db.biosamples_flattened.createIndex({ env_broad_scale: 1, env_local_scale: 1, env_medium: 1 })'  # real    3m7.979s
#	date && mongosh ncbi_metadata mongo-js/enriched_biosamples_env_triad_value_counts_gt_1.js && date # Elapsed time: 173055 ms
	$(RUN) time python external_metadata_awareness/new_env_triad_values_splitter.py \
		--host localhost \
		--port 27017 \
		--db ncbi_metadata \
		--collection biosamples_env_triad_value_counts_gt_1 \
		--no-authenticate \
		--field env_triad_value \
		--min-length 3 # < 1 minute # FAILS IF BIOPORTAL KEY NOT IN local/.env # works best if expanded_envo_po_lexical_index.yaml present
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.biosamples_env_triad_value_counts_gt_1.createIndex({ "components.label": 1, "components.label_digits_only": 1, "components.label_length": 1, "count": 1 })'  # fast
	date && time mongosh ncbi_metadata mongo-js/aggregate_env_triad_label_components.js && date # fast
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.env_triad_component_labels.createIndex({label_digits_only: 1, label_length: 1})'
	date && time poetry run python external_metadata_awareness/new_env_triad_oak_annotator.py && date # 3 minutes, local, non-web API
	date && time poetry run python external_metadata_awareness/new_env_triad_ols_annotator.py && date # 7 minutes, running mostly off of cache; 7 hours without cache
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.biosamples_env_triad_value_counts_gt_1.createIndex({ "components.curie_uc": 1, "count": 1 })'
	date && time mongosh ncbi_metadata mongo-js/aggregate_env_triad_curies.js && date
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.env_triad_component_curies_uc.createIndex({ prefix_uc: 1 })'
	date && time poetry run python external_metadata_awareness/new_check_semsql_curies.py && date
	time $(MONGO_COMMAND) --host $(MONGO_HOST) --port $(MONGO_PORT) $(MONGO_DB) --quiet --eval \
		'db.env_triad_component_curies_uc.createIndex({ prefix_uc: 1, curie_uc: 1 })'
	date && time poetry run python external_metadata_awareness/new_bioportal_curie_mapper.py && date # 2 minutes, mostly running off of cache; 13 minutes without cache
	$(RUN) python external_metadata_awareness/populate_env_triads_collection.py # creates its own indices # 30 minutes + 6 for indexing

# todo run populate_env_triads_collection with --no-recreate-indices ?

# not really triads related
.PHONY: normalize-measurements
normalize-measurements:
	$(RUN) python external_metadata_awareness/normalize_biosample_measurements.py \
		--overwrite \
		--field age \
		--field elev \
		--field samp_size

# PRIOR TO THIS CODE
#bioprojects
#bioprojects_submissions
#
#biosamples # review, document and optimize indices
#biosamples_attribute_name_counts_flat_gt_1
#
#biosamples_flattened # review, document and optimize indices
#biosamples_ids
#biosamples_links
#
#notes
#
#packages
#
#sra_attributes_k_doc_counts_gt_1
#sra_biosamples_bioprojects ... index on both biosample_accession and bioproject_accession

# AFTER THIS CODE
#biosamples_env_triad_value_counts_gt_1
#
#env_triad_component_curies_uc
#env_triad_component_labels


#db.env_triad_component_labels.updateMany(
#  {},
#  { $unset: { oak_text_annotations: "", components_count: "oak_annotations_count" } }
#);

#use ncbi_metadata
#
#db.biosamples_env_triad_value_counts_gt_1.drop()
#db.env_triad_component_curies_uc.drop()
#db.env_triad_component_labels.drop()

#db.biosamples_env_triad_value_counts_gt_1.updateMany(
#  {},
#  { $unset: { components: "", components_count: "" } }
#);

#db.biosamples_env_triad_value_counts_gt_1.aggregate([
#  {
#    $facet: {
#      components_count: [
#        { $match: { components_count: 2 } },
#        { $count: "count" }
#      ],
#      lingering_envo: [
#        { $match: { "components.lingering_envo": true } },
#        { $count: "count" }
#      ],
#      prefix_uc_ENVO: [
#        { $match: { "components.prefix_uc": "ENVO" } },
#        { $count: "count" }
#      ],
#      prefix_uc_OF: [
#        { $match: { "components.prefix_uc": "OF" } },
#        { $count: "count" }
#      ]
#    }
#  }
#])

#db.biosamples_env_triad_value_counts_gt_1.aggregate([
#  { $unwind: "$components" },
#  { $group: { _id: "$components.prefix_uc", count: { $sum: 1 } } },
#  { $sort: { count: -1 } }
#]);

