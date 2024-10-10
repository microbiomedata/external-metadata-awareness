clean:
	rm -rf return-to-oak-results/*.txt

all: clean return-to-oak-results/non-aquatic-non-terrestrial-biomes.txt return-to-oak-results/non-fao-non-enriched-soil.txt

return-to-oak-results/biomes.txt:
	poetry run runoak --input sqlite:obo:envo info .desc//p=i biome .not biome | sort > $@

return-to-oak-results/aquatic-biomes.txt:
	poetry run runoak --input sqlite:obo:envo info .desc//p=i 'aquatic biome' .not 'aquatic biome' | sort > $@

return-to-oak-results/terrestrial-biomes.txt:
	poetry run runoak --input sqlite:obo:envo info .desc//p=i 'terrestrial biome' .not 'terrestrial biome' | sort > $@

return-to-oak-results/non-aqutic-biomes.txt: return-to-oak-results/biomes.txt return-to-oak-results/aquatic-biomes.txt
	comm -23 $^ > $@

return-to-oak-results/non-terrestrial-biomes.txt: return-to-oak-results/biomes.txt return-to-oak-results/terrestrial-biomes.txt
	comm -23 $^ > $@

return-to-oak-results/non-aquatic-non-terrestrial-biomes.txt: return-to-oak-results/non-aqutic-biomes.txt return-to-oak-results/non-terrestrial-biomes.txt
	comm -12 $^ > $@

return-to-oak-results/soil.txt:
	poetry run runoak --input sqlite:obo:envo info .desc//p=i 'soil' .not soil | sort > $@


return-to-oak-results/soil.csv: return-to-oak-results/soil.txt
	poetry run normalize-envo-data \
		--input-file $< \
		--ontology-prefix ENVO \
		--output-file $@

# 			--output $@ \
    #				--output-type tsv

#    		--output-type yaml \
#		--output $@

return-to-oak-results/soil-annotated.yaml: return-to-oak-results/soil.csv
	date ; poetry run runoak \
		-v \
		--input bioportal: annotate \
		--no-matches-whole-text \
		--output-type yaml \
		--output $@ \
		--text-file $< \
		--match-column normalized_label ; date

return-to-oak-results/soil-relationships.tsv:
	poetry run runoak --input sqlite:obo:envo relationships .desc//p=i soil > $@

return-to-oak-results/enriched-soil.txt:
	poetry run runoak --input sqlite:obo:envo info .desc//p=i 'enriched soil' .not 'enriched soil' | sort > $@

return-to-oak-results/non-enriched-soil.txt: return-to-oak-results/soil.txt return-to-oak-results/enriched-soil.txt
	comm -23 $^ > $@

return-to-oak-results/mixs-fao-classes.txt: downloads/mixs.yaml
	yq '.enums.FaoClassEnum.permissible_values' $< | cat > $@

return-to-oak-results/mixs-fao-classes-tidy.txt: return-to-oak-results/mixs-fao-classes.txt
	sed 's/://' $< | sed 's/s$$//' | tr '[:upper:]' '[:lower:]' | sort > $@

return-to-oak-results/non-fao-non-enriched-soil.txt: return-to-oak-results/mixs-fao-classes-tidy.txt return-to-oak-results/non-enriched-soil.txt
	grep -v -f $(word 1, $^) $(word 2, $^) > $@

return-to-oak-results/non-observed-biomes.txt: return-to-oak-results/observed-consolidated/soil-ebs-biomes.txt return-to-oak-results/biomes.txt
	grep -v -f $(word 1, $^) $(word 2, $^) > $@