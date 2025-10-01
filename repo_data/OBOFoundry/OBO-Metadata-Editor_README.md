# OBO Metadata Editor

A web based editor for modifying existing and creating new OBO Metadata configurations.

## Before running the server:

1. Install the necessary python dependencies using `pip` by navigating to the directory in which `server.py` is located and running the following command:
```
pip install -r requirements.txt
```

2. Make sure that the following environment variables have been set:

- GITHUB_CLIENT_ID
- GITHUB_CLIENT_SECRET
- GITHUB_APP_STATE
- FLASK_SECRET_KEY
- FLASK_HOST

To obtain the values for the first two settings, send an email to james@overton.ca. For the values of `GITHUB_APP_STATE` and `FLASK_SECRET_KEY`, a randomly generated string may be used. `FLASK_HOST` should be the full server address, including the protocol and (optionally) the port, e.g., https://purl-editor.com:5000.

3. Edit the file `config.py` and make sure that the configuration settings are correct. Note in particular the settings for `LOG_LEVEL`, `GITHUB_ORG`, `SCHEMAFILE`, and `ONTOLOGY_METADATA_URL`.
- `LOG_LEVEL` should be set to one of: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (_without_ quotes). Note that setting logging to DEBUG will only be effective if FLASK_ENV is set to `development` (the default is `production`)
- `GITHUB_ORG` should be set to the organization or username that owns the repository. Normally it should be set to `OBOFoundry`.
- `SCHEMAFILE` is the location of the jsonschema file that will be used to validate YAML code.
- `ONTOLOGY_METADATA_URL` is the URL from which descriptive information about various ontologies can be found.

## Running the server

- Navigate to the directory in which `server.py` is located, and then run the following commands:
```
export FLASK_APP=server.py
export FLASK_DEBUG=1 (optional)
export FLASK_ENV=development (optional)
python3 -m flask run
```
