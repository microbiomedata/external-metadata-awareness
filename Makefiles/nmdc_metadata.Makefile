RUN=poetry run
WGET=wget

downloads/nmdc-production-studies.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/study_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

downloads/nmdc-production-biosamples.json:
	wget -O $@.bak https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999
	yq '.resources' -o=json $@.bak | cat > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-5pct.json: downloads/nmdc-production-biosamples.json
	$(RUN) random-sample-resources \
		--input-file $< \
		--output-file $@ \
		--sample-percentage 5

local/nmdc-production-biosamples-env-context-columns.tsv: downloads/nmdc-production-biosamples.json
	$(RUN) biosample-json-to-context-tsv \
		--input-file $< \
		--output-file $@

local/nmdc-production-biosamples-env-context-authoritative-labels.tsv: local/nmdc-production-biosamples-env-context-columns.tsv
	$(RUN) python external_metadata_awareness/get_authoritative_labels_only_for_nmdc_context_columns.py \
		--input-file $< \
		--output-file $@ \
		--oak-adapter-string 'sqlite:obo:envo'

local/nmdc-production-biosamples-env_package-predictions.tsv: local/nmdc-production-biosamples-env-context-authoritative-labels.tsv \
downloads/nmdc-production-studies.json
	#  local/env-package-heterogeneity.tsv is an output
	# may also get printed to the console?
	$(RUN) python external_metadata_awareness/predict_env_package_from_nmdc_context_authoritative_labels.py \
		--input-file $(word 1,$^) \
		--output-file $@ \
		--oak-adapter-string 'sqlite:obo:envo' \
		--heterogeneity-file 'local/env-package-heterogeneity.tsv' \
		--override-file 'contributed/mam-env-package-overrides.tsv' \
		--override-biosample-column 'id' \
		--override-env-package-column 'mam_inferred_env_package' \
		--studies-json $(word 2,$^)

# no header?
local/nmdc-production-biosamples-env_local_scale.tsv: local/nmdc-production-biosamples-env-context-columns.tsv
	cut -f5 $< | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@

local/nmdc-production-biosamples-soil-env_local_scale.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f5 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-soil-env_broad_scale.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f3 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-water-env_broad_scale.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"water\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f3 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-soil-env_medium.tsv: local/nmdc-production-biosamples-env_package-predictions.tsv
	$(RUN) python -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], sep='\t').query('predicted_curated_env_package == \"soil\"').to_csv(sys.argv[2], sep='\t', index=False)" $<  $@.bak
	cut -f7 $@.bak | sed '1d' | sort | uniq -c | awk '{print $$2 "\t" $$1}' > $@
	rm -rf $@.bak

local/nmdc-production-biosamples-env_local_scale-ids.txt: local/nmdc-production-biosamples-env_local_scale.tsv
	cut -f1 $< > $@

local/nmdc-production-biosamples-env-package.json:
	curl -X 'GET' \
		'https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=999999&projection=env_package' \
		-H 'accept: application/json' > $@.bak
	yq '.resources' -o=json $@.bak | cat > $@ # ENVO:00001998 is also soil
	rm -rf $@.bak

local/nmdc-production-studies-images.csv: downloads/nmdc-production-studies.json
	$(RUN) python external_metadata_awareness/study-image-table.py \
		--input-file $< \
		--output-file $@

####

# biosamples that are part of a particular study
downloads/sty-11-ev70y104_biosamples.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/biosample_set?filter=%7B%22part_of%22%3A%20%22nmdc%3Asty-11-ev70y104%22%7D&max_page_size=999999'
	yq -o=json e '.resources' $@.bak | cat > $@
	rm -rf $@.bak

# metadata about a particular study
downloads/sty-11-ev70y104_study.json:
	wget -O $@.bak 'https://api.microbiomedata.org/nmdcschema/ids/nmdc%3Asty-11-ev70y104'
	yq -o=json e '.' $@.bak | cat > $@
	rm -rf $@.bak
