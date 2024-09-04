RUN=poetry run
WGET=wget

SUBMISSION_SCHEMA_URL=https://raw.githubusercontent.com/microbiomedata/submission-schema/v10.7.0/src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml

downloads/nmdc_submission_schema.yaml:
	wget -O $@ $(SUBMISSION_SCHEMA_URL)

local/established-value-sets-from-submission-schema.json: downloads/nmdc_submission_schema.yaml
	yq -o=json e '{"enums": {"EnvBroadScaleSoilEnum": .enums.EnvBroadScaleSoilEnum, "EnvLocalScaleSoilEnum": .enums.EnvLocalScaleSoilEnum, "EnvMediumSoilEnum": .enums.EnvMediumSoilEnum}}' $< | cat > $@ # ~ 48

local/nmdc-submission-schema-enums-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums | keys | .[]' $< | sort  > $@

local/EnvBroadScaleSoilEnum-pvs-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums.EnvBroadScaleSoilEnum.permissible_values | keys | .[]' $< | cat > $@

local/EnvLocalScaleSoilEnum-pvs-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums.EnvLocalScaleSoilEnum.permissible_values | keys | .[]' $< | cat > $@

local/EnvBroadScaleSoilEnum-pvs-keys-parsed.csv: local/EnvBroadScaleSoilEnum-pvs-keys.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/EnvLocalScaleSoilEnum-pvs-keys-parsed.csv: local/EnvLocalScaleSoilEnum-pvs-keys.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv: local/EnvBroadScaleSoilEnum-pvs-keys-parsed.csv
	cut -f3,4 -d, $< | head -n 1 > $<.header.csv
	tail -n +2 $< | cut -f3,4 -d, | sort | uniq > $@.tmp
	cat $<.header.csv $@.tmp > $@
	rm -rf $<.header.csv $@.tmp

local/EnvLocalScaleSoilEnum-pvs-keys-parsed-unique.csv: local/EnvLocalScaleSoilEnum-pvs-keys-parsed.csv
	cut -f3,4 -d, $< | head -n 1 > $<.header.csv
	tail -n +2 $< | cut -f3,4 -d, | sort | uniq > $@.tmp
	cat $<.header.csv $@.tmp > $@
	rm -rf $<.header.csv $@.tmp

local/EnvBroadScaleSoilEnum.png: local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv
	cat $< | tail -n +2  | cut -f1 -d, > $@.ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --no-view --output $@ --gap-fill [ .idfile $@.ids.txt ] .or biome
	rm -rf $@.ids.txt

local/EnvMediumSoilEnum-pvs-keys.txt: downloads/nmdc_submission_schema.yaml
	yq eval '.enums.EnvMediumSoilEnum.permissible_values | keys | .[]' $< | cat > $@

local/EnvMediumSoilEnum-pvs-keys-parsed.csv: local/EnvMediumSoilEnum-pvs-keys.txt
	$(RUN) normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

local/EnvMediumSoilEnum-pvs-keys-parsed-unique.csv: local/EnvMediumSoilEnum-pvs-keys-parsed.csv
	cut -f3,4 -d, $< | head -n 1 > $<.header.csv
	tail -n +2 $< | cut -f3,4 -d, | sort | uniq > $@.tmp
	cat $<.header.csv $@.tmp > $@
	rm -rf $<.header.csv $@.tmp

local/EnvMediumSoilEnum.png: local/EnvMediumSoilEnum-pvs-keys-parsed-unique.csv
	cat $< | tail -n +2  | cut -f1 -d, > $@.ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --gap-fill --no-view --output $@ .idfile $@.ids.txt
	rm -rf $@.ids.txt
