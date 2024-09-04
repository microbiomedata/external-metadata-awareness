RUN=poetry run
WGET=wget

# want to combine the evidence from

# local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.txt (class hierarchy judgement calls)
# counts of NCBI Biosamples env_local_scale assertions (local/ncbi-mims-soil-biosamples-env_local_scale-annotated.tsv) after normalization. See normalized_curie/real_label and matched_id/matched_label... some overlap with GOLD Biosamples?
# counts of NMDC Biosamples env_local_scale assertions (env_local_scale_id from  needs extraction and counting)

# counts of GOLD Biosamples using env_local_scale terms inferred from goldterms (sparse local/goldData_biosamples-inferred-soil-env_local_scale-counts.tsv)

# flags for process, biome, or envirnmental material classes

local/env-local-scale-candidates.txt:
	$(RUN) runoak --input sqlite:obo:envo info .desc//p=i 'material entity' .not [ .desc//p=i 'biome'.or .desc//p=i 'environmental material' .or .desc//p=i 'anatomical entity' .or .desc//p=i 'chemical entity' .or .desc//p=i 'environmental system' .or .desc//p=i 'administrative region' .or .desc//p=i 'aeroform' .or .desc//p=i 'anatomical entity environment' .or .desc//p=i 'area protected according to IUCN guidelines' .or .desc//p=i 'astronomical object' .or .desc//p=i 'building part' .or .desc//p=i 'channel of a watercourse' .or .desc//p=i 'collection of organisms' .or .desc//p=i 'cryospheric layer' .or .desc//p=i 'ecozone' .or .desc//p=i 'environmental monitoring area' .or .desc//p=i 'fluid layer'  .or .desc//p=i 'healthcare facility' .or .desc//p=i 'ice field' .or .desc//p=i 'ice mass' .or .desc//p=i 'industrial building' .or .desc//p=i 'interface layer' .or .desc//p=i 'manufactured product' .or .desc//p=i 'mass of biological material' .or .desc//p=i 'mass of fluid' .or .desc//p=i 'material isosurface' .or .desc//p=i 'meteor' .or .desc//p=i 'meteorite' .or .desc//p=i 'observing system' .or .desc//p=i 'organic object' .or .desc//p=i 'organism' .or .desc//p=i 'particle' .or .desc//p=i 'piece of plastic' .or .desc//p=i 'piece of rock' .or .desc//p=i 'planetary structural layer' .or .desc//p=i 'plant anatomical entity' .or .desc//p=i 'political entity' .or .desc//p=i 'protected area' .or .desc//p=i 'subatomic particle' .or .desc//p=i 'transport feature' .or .desc//p=i 'water current' .or .desc//p=i,p 'l~undersea' ] .or bridge .or road .or 'wildlife management area' .or .desc//p=i 'lake layer' .or .desc//p=i island > $@

local/env-local-scale-candidate-ids.txt: local/env-local-scale-candidates.txt
	cut -f1 -d' ' $< > $@

local/mam-individual-exclusion-ids.txt:
	cat contributed/mam-individual-exclusions/env_local_scale/*txt | cut -f1 -d' ' > $@

local/env-local-scale-candidates-relationships.tsv: local/env-local-scale-candidate-ids.txt
	$(RUN) runoak --input sqlite:obo:envo relationships .idfile $< > $@

local/env-local-scale-candidate-leaves.txt: local/env-local-scale-candidate-ids.txt local/envo-leaf-ids.txt
	$(RUN) runoak --input sqlite:obo:envo info .idfile $(word 1,$^) .and .idfile $(word 2,$^)  > $@

local/env-local-scale-candidate-non-leaf.txt: local/env-local-scale-candidates.txt local/envo-leaf-ids.txt
	$(RUN) runoak --input sqlite:obo:envo info .idfile $(word 1,$^) .not [ .idfile $(word 2,$^) ] > $@

local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.txt: local/env-local-scale-candidate-non-leaf.txt local/mam-individual-exclusion-ids.txt
	$(RUN) runoak --input sqlite:obo:envo info .idfile $(word 1,$^) .not .idfile $(word 2,$^) > $@

local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied-ids.txt: local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.txt
	cut -f1 -d' ' $< > $@


local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied.png: local/env-local-scale-candidate-non-leaf.txt \
local/mam-individual-exclusion-ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --gap-fill --output $@ [ 'material entity' or .idfile $(word 1,$^) ] .not .idfile $(word 2,$^)

#local/env-local-scale-non-leaf.csv: local/env-local-scale-candidate-non-leaf.txt
#	$(RUN) normalize-envo-data \
#		--input-file $< \
#		--ontology-prefix ENVO \
#		--output-file $@

local/env-local-scale-non-leaf.png: local/env-local-scale-candidates.txt local/envo-leaf-ids.txt
	$(RUN) runoak --input sqlite:obo:envo viz --gap-fill  --output $@  .idfile $(word 1,$^) .not [ .idfile $(word 2,$^) ]

# 		--downsample-uncounted \

local/soil-env-local-scale-evidence-table.tsv: config/soil-env_local_scale-evidence-config.yaml \
local/env-local-scale-candidate-non-leaf-mam-individual-exclusion-applied-ids.txt \
local/nmdc-production-biosamples-soil-env_local_scale.tsv \
local/ncbi-mims-soil-biosamples-env_local_scale-annotated.tsv \
local/goldData_biosamples-inferred-soil-env_local_scale-counts.tsv
	$(RUN) python external_metadata_awareness/extract_value_set_evidence.py \
		--config $< \
		--downsample-uncounted \
		--output-file $@

.PHONE: aggressive-cleanup
aggressive-soil-env-local-scale-cleanup:
	# building local/envo_goldterms.db takes < 1 minute # may want to include other sem sql files too
	# building local/ncbi_biosamples.duckdb and compressing local/ncbi_biosamples.duckdb.gz takes "a while"
	# don't delete local/.env or local/env.template... maybe they should go in another directory?
	# downloading downloads/biosample_set.xml.gz takes ~ 2 minutes (~ 3 GB)
	# unpacking local/biosample_set.xml takes ~ 6 minutes (~ 100 GB)
	rm -rf downloads/nmdc-production-*
	rm -rf local/biosample-count-mongodb.txt # 1 minute to rebuild
	rm -rf local/biosample-count-xml.txt # 1.5 minutes to rebuild
	rm -rf local/env-local-scale*
	rm -rf local/env-package-heterogeneity.tsv
	rm -rf local/envo-*
	rm -rf local/goldData*
	rm -rf local/goldterms*
	rm -rf local/mam-individual-exclusion-ids.txt
	rm -rf local/ncbi-mims-soil*
	rm -rf local/nmdc-production-biosamples*
	rm -rf local/soil-env-local-scale-evidence-table.tsv

