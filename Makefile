WGET=wget

# get MIxS YAML and EnvO OWL or sqlite

# very complex documents; many are too large to load into a MongoDB BSON document
downloads/bioproject.xml:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml" # ~ 3 GB August 2024

downloads/biosample_set.xml.gz:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz" # ~ 3 GB August 2024

local/biosample_set.xml: downloads/biosample_set.xml.gz
	gunzip -c $< > $@

# for development
downloads/books.xml:
	$(WGET) -O $@ "https://www.w3schools.com/xml/books.xml"

# 8 years old. seems very incomplete.
downloads/biosample.xsd:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/biosample/biosample.xsd?view=co"

# find code for converting to tabel in other repos
# or convert to duckdb
downloads/ncbi_biosample_attributes.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/attributes/?format=xml"

downloads/ncbi_biosample_packages.xml:
	$(WGET) -O $@ "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"