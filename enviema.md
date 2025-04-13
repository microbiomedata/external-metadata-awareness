I want to normalize and unify all of the tools I use to load biosample, study, etc, data into MongoDB.

The data will come from downloaded files, responses from APIs, and clones from other MongoDB collections.

Much of the core functionality is already in this repo or other repos in the same GH organization.

The resulting MongoDBs will have value added data, like flattening of records with a complex structure, normalization of
text with CURIes from the OBO foundry, etc.

Emphasis will be put on uniform interfaces and validation, like MongoDB connection strings, Click CLI parameters, .env
file locations and content, etc.

These tools should be able to run form multiple locations (like my Ubuntu NUC, my LBL MacBook Pro, and NERSC Perlmutter)
and be able to write into MongoDBs hosted on any of those systems

The codename for this effort is enviema. It's GitHub issue
is https://github.com/microbiomedata/external-metadata-awareness/issues/176

Another outcome of this should be good documentation and automation. The Python scripts should have Click aliases in
pyproject.toml and have Makefile illustrations of use

We should end up with documentation of the inputs, transformation steps, and resulting MongoDB collection. Ideally it
would be easy to track whether several server have the same collection. We will need a good mechanism for keeping
metadata about the collection in a collection, possible names `notes`

We may need to ask a colleague with database/system admin permissions to create new databases

We should think about whether to have an A/B version of the databases so that one can be refreshed while colleagues use
the other onne

Some of the MongoDB access will require establishing an ssh tunnel to NERSC resources on SPIN.

I want to start by cloning the National Microbiome Data Collaborative's production metadatastore. I have access to that
either though an API that doesn't require authentication or though direct MongoDB access with does require an ssh tunnel
unless running or Perlmutter, and requires a MongoDB username/password. Lets' begin by cloning the data onto the
unauthenticated MongoDB on my Ubuntu 24 NUC.

The API is at https://api.microbiomedata.org/ and has a swagger interface at https://api.microbiomedata.org//docs

An example of use is

https://api.microbiomedata.org/nmdcschema/biosample_set?max_page_size=20

The codebase for that API is https://github.com/microbiomedata/nmdc-runtime

This endpoint returns biosamples from the database with these query parameters:

1. filter (optional): A JSON-formatted MongoDB query filter - Example: {"associated_studies": "nmdc:sty-11-34xj1150"}
2. max_page_size (optional, default=20): Controls how many biosamples are returned per page
3. page_token (optional): Token for retrieving the next page of results (provided in previous response)
4. projection (optional): Comma-delimited list of field names to include in the response

The endpoint supports efficient queries on indexed fields for biosample_set, including:

- alternative_identifiers
- environmental parameters (env_broad_scale, env_local_scale, env_medium)
- collection_date
- ecosystem hierarchy (ecosystem, ecosystem_category, ecosystem_type, ecosystem_subtype, specific_ecosystem)
- latitude and longitude

The response is paginated, returning a ListResponse object with:

- resources: Array of matching biosamples
- next_page_token: Token for the next page of results (if more results exist)

I can connect to the MongoDB with a string like

`mongodb://<USERNAME>:<PASSWORD>@localhost:27777/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin`

After establishing a tunnel like this if necessary

```shell
ssh -i ~/.ssh/nersc -L27777:mongo-loadbalancer.nmdc.production.svc.spin.nersc.org:27017 -o ServerAliveInterval=60 <USERNAME>@dtn01.nersc.gov
```

That illustration uses an ssh key that was created with the [sshproxy](https://docs.nersc.gov/connect/mfa/#sshproxy)

Like

```shell
~/sshproxy -u mam -f
```

You can learn about any ssh tunnels running on your computer with a command like

```shell
ps -ef | grep ssh
```

But this article won't describe that interpretation process.

----

Getting collection names in the most direct possible way:

Create a `.env` file with the appropriate value for `MONGO_USERNAME=`, `MONGO_PASSWORD=` and `MONGO_PORT` on separate lines. Talk to
your manager, a colleague, or your project's PI for obtaining those values

```shell
set -a
source .env
set +a
mongosh "mongodb://localhost:${MONGO_PORT}/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
  --username "$MONGO_USERNAME" \
  --password "$MONGO_PASSWORD" \
  --eval 'db = db.getSiblingDB("nmdc"); db.biosample_set.findOne()'
```

I don't have `db.getSiblingDB("ncbi").getCollectionNames()` permission on the NMDC production MongoDB!

```shell
mongosh "mongodb://localhost:${MONGO_PORT}/?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin" \
  --username "$MONGO_USERNAME" \
  --password "$MONGO_PASSWORD" \
  --quiet \
  --eval 'db = db.getSiblingDB("nmdc"); print(JSON.stringify(db.getCollectionNames()))' \
  | jq -r '.[]' | sort
```

If you want to connect to a different server on a different address/hostname, or without username/password
authentication, then you will have to modify that command.

----

What MongoDB collections does the schema (version XYZ) specify?

curl -sSL 'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/tags/v11.5.1/nmdc_schema/nmdc_materialized_patterns.yaml' | yq '.classes.Database.slots.[]' | sort

What collections does the runtime API report?

curl -sSL 'https://api.microbiomedata.org/nmdcschema/collection_stats' | jq -r '.[].ns' | sed 's/nmdc\.//' | sort

----

## Flattening NMDC Collections

After restoring the NMDC data from the dump, you can create flattened collections for easier querying and analysis using one of the following commands.

### For local unauthenticated MongoDB:

```shell
make -f Makefiles/nmdc_metadata.Makefile flatten-nmdc
```

### For authenticated MongoDB using credentials from an .env file:

```shell
make -f Makefiles/nmdc_metadata.Makefile flatten-nmdc-auth
```

The .env file should be located at `local/.env` and contain the following variables:
```
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
MONGO_HOST=localhost
MONGO_PORT=27777
MONGO_DB=nmdc
MONGO_AUTH_SOURCE=admin
```

Either command creates the following collections in the NMDC database:

- `flattened_biosample`: Flattened view of biosamples with all fields normalized and environmental fields decorated with ontology information
- `flattened_biosample_chem_administration`: Extracted chemical administration details from biosamples
- `flattened_biosample_field_counts`: Statistics on field usage across all biosamples 
- `flattened_study`: Flattened view of studies with all fields normalized
- `flattened_study_associated_dois`: Extracted DOIs associated with studies
- `flattened_study_has_credit_associations`: Extracted credit associations from studies

The flattening process:
1. Reads data directly from your local MongoDB (using the already restored NMDC collections)
   - Automatically detects alternative collection names (`study_set`, `studies`, or `study` and `biosample_set`, `biosamples`, or `biosample`)
2. Processes complex nested structures into simple dot-notation fields
3. Converts arrays to pipe-separated strings for easier querying
4. Decorates environmental context fields with detailed ontology information:
   - Adds `*_normalized_curie`: The properly formatted CURIE with colon separator (e.g., ENVO:01000253)
   - Adds `*_canonical_label`: The authoritative label from the ontology
   - Adds `*_obsolete`: Boolean indicating if the term is obsolete
   - Adds `*_label_match`: Boolean indicating if the asserted label matches the canonical label
5. Extracts sub-objects into specialized collections

The implementation is in `external_metadata_awareness/flatten_nmdc_collections.py`.
