RUN=poetry run

# Default MongoDB connection parameters (can be overridden)
MONGO_HOST ?= localhost
MONGO_PORT ?= 27017
MONGO_DB_GOLD ?= gold_metadata

# see also https://github.com/microbiomedata/sample-annotator/blob/b48b62d2cd83d57dff4c56342b4b5bf7154c9ade/make-gold-cache.Makefile

local/goldData.xlsx:
	curl -o $@ "https://gold.jgi.doe.gov/download?mode=site_excel"

# Target: flatten-gold-biosamples
# Usage: make -f Makefiles/gold.Makefile flatten-gold-biosamples
#
# This target will flatten GOLD biosamples stored in MongoDB and create 
# normalized collections with environmental context fields.
#
# It performs the following tasks:
# 1. Connects to MongoDB for gold_metadata database
# 2. Flattens each biosample document, especially the environmental fields
# 3. Converts environmental IDs to canonical CURIEs
# 4. Looks up canonical labels and checks for obsolete terms
# 5. Creates flattened_biosamples and flattened_biosample_contacts collections
#
# You can override connection parameters:
# make -f Makefiles/gold.Makefile flatten-gold-biosamples MONGO_HOST=192.168.1.100 MONGO_PORT=27777
#
flatten-gold-biosamples: # depends on populating a gold_metadata collection with the sample-annotator repo
	$(RUN) python external_metadata_awareness/insert_all_flat_gold_biosamples.py \
		--dotenv-path local/.env.flattening \
		--mongo-uri "mongodb://localhost:27777/gold_metadata?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
		--source-collection biosamples \
		--target-collection flattened_biosamples \
		--contacts-collection flattened_biosample_contacts
