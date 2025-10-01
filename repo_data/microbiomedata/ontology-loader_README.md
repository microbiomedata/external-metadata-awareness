## ontology_loader

Suite of tools to configure and load an ontology from the OboFoundary into the data object for OntologyClass as 
specified by NMDC schema.

## Development Environment

#### Pre-requisites

- >=Python 3.9
- Poetry
- Docker
- MongoDB
- NMDC materialized schema
- ENV variable for MONGO_PASSWORD (or pass it in via the cli/runner itself directly)

```bash
% docker pull mongo
% docker run -d --name mongodb-container -p 27018:27017 mongo
```

#### MongoDB Connection Settings

When connecting to MongoDB, you need to set the correct environment variables depending on where your code is running:

1. When running from your local machine (CLI or tests):
   ```bash
   export MONGO_HOST=localhost
   export MONGO_PORT=27018
   export ENABLE_DB_TESTS=true
   export MONGO_PASSWORD="your_valid_password"
   ```

2. When running inside Docker containers:
   ```bash
   export MONGO_HOST=mongo
   export MONGO_PORT=27017
   ```

The Docker container networking uses container names (like 'mongo') for internal communication, while your host machine must use 'localhost' with the mapped port (27018).

#### Basic mongosh commands
```bash
% docker ps
% docker exec -it [mongodb-container-id] bash
% mongosh mongodb://admin:root@mongo:27017/nmdc?authSource=admin
% show dbs
% use nmdc
% db.ontology_class_set.find().pretty()
% db.ontology_relation_set.find().pretty()
% db.ontology_class_set.find( { id: { $regex: /^PO/ } } ).pretty()
% db.ontology_class_set.find( { id: { $regex: /^UBERON/ } } ).pretty()
% db.ontology_class_set.find( { id: { $regex: /^ENVO/ } } ).pretty()
``` 

#### Command line
```bash
% poetry install
% poetry run ontology_loader --help
% poetry run ontology_loader --source-ontology "envo"
% poetry run ontology_loader --source-ontology "uberon"
```

#### Running the tests
```bash
% make test
```

#### Running the linter
```bash
% make lint
```

#### Python example usage
```bash
pip install nmdc-ontology-loader
```

```python
from ontology_loader.ontology_load_controller import OntologyLoaderController
import tempfile

def load_ontology():
    """Load an ontology using the default MongoDB connection."""
    loader = OntologyLoaderController(
        source_ontology="envo",
        output_directory=tempfile.gettempdir(),
        generate_reports=True,
    )
    loader.run_ontology_loader()
```

#### Using with an existing MongoDB connection

If you already have a MongoDB connection established (e.g., in a Dagster/Dagit job), you can pass it directly to the OntologyLoaderController:

```python
from pymongo import MongoClient
from ontology_loader.ontology_load_controller import OntologyLoaderController
import tempfile

# Use an existing MongoDB client
mongo_client = MongoClient("mongodb://admin:password@localhost:27018/nmdc?authSource=admin")

# Pass the client and database name to OntologyLoaderController
loader = OntologyLoaderController(
    source_ontology="envo",
    output_directory=tempfile.gettempdir(),
    generate_reports=True,
    mongo_client=mongo_client,  # Pass the existing client
    db_name="nmdc",  # Required when passing an existing client
)

# The loader will use the provided client instead of creating a new connection
loader.run_ontology_loader()
```

This approach is particularly useful when:
- You're running in a job scheduler like Dagster/Dagit
- You want to reuse an existing connection pool
- You have custom MongoDB connection settings that are managed externally
- You need to use a connection with specific authentication or configuration

> **Note**: When passing an existing MongoDB client, you must also provide the `db_name` parameter to specify which database to use. This is required as the database name cannot be automatically determined from a MongoDB client instance.

### Testing CRUD operations in a live MongoDB

If you want to test the CRUD operations in a live MongoDB instance, you need to set two environment variables:
MONGO_PASSWORD="your_valid_password"
ENABLE_DB_TESTS=true

This will allow you to run tests to actually insert/update/delete records in your MongoDB tests instance instead
of simply mocking the calls. You can then run the tests with the following command:

```bash
make test
```
 
The same test command will run without the environment variables, but it will only mock the calls to the database.
This is intended to help prevent accidental data loss or corruption in a live database environment and to 
ensure that MONGO_PASSWORD is not hardcoded in the codebase.

### Reset collections in dev

```bash
docker exec -it nmdc-runtime-test-mongo-1 bash
```
```bash
mongosh mongodb://admin:root@mongo:27017/nmdc?authSource=admin
db.ontology_class_set.find({}).pretty()
db.ontology_relation_set.find({}).pretty()
db.biosample_set.find({}).pretty()
db.ontology_class_set.drop()
db.ontology_relation_set.drop()
db.ontology_class_set.countDocuments()
db.ontology_relation_set.countDocuments()
```
