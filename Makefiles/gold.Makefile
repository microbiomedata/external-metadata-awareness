RUN=poetry run

# see also https://github.com/microbiomedata/sample-annotator/blob/b48b62d2cd83d57dff4c56342b4b5bf7154c9ade/make-gold-cache.Makefile

local/goldData.xlsx:
	curl -o $@ "https://gold.jgi.doe.gov/download?mode=site_excel"
