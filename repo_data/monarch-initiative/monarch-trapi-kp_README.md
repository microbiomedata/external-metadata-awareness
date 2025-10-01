# Monarch SemSimian Multi-CURIE Query TRAPI Knowledge Provider ("MMCQ")

This project is a [NCATS Translator API ("TRAPI")](https://github.com/NCATSTranslator/ReasonerAPI) wrapper for the Monarch Initiative information system - or rather specifically, the **_Semantic Similarity_** ("SemSimian") component of the system - making it behave like a TRAPI Knowledge Provider ("KP") responding  to Multi-Curie "similarity" queries against its embedded ["SemSimian" algorithm](https://github.com/monarch-initiative/semsimian).

The initial release of the wrapper application supports the following use case:

_**Given a set of (Human Phenotype Ontology term 'Human Phenotype Ontology ("HPO") term identified) phenotypes, what Monarch Disease Ontology ("MONDO") indexed diseases do they match?**_

The goal is to find a good, probably creative answer that satisfies as many of the N inputs as possible, but may not satisfy all of them.

## Installation

### Install dependencies within a suitable virtual environment

The Python virtual environment and dependencies of MMCQ are managed using Poetry. Assuming that you have [Poetry](https://python-poetry.org/docs/) and a suitable version of Python (i.e. ">=3.9,<3.12") installed, then:

    poetry shell
    poetry install

#### Jupyter Notebook

The [MultiCurieQueries.ipynb Jupyter Notebook](./docs/MultiCurieQueries.ipynb) _may_ require a minimum Python version of 3.11 to run and does require installation of the optional poetry dependencies. Modifying the above command as follows: 

    poetry install -E jupyter

Please note that the MMCQ server itself must be running (see below) for the Jupyter Notebook itself to work!
 
### Configure MMCQ settings
   
   Copy the `.env-template` file, saved as `.env` in repository root dir, then customize accordingly, for example:
   
   ```bash
    # SemSimian backend API for 'development' environment 
    # (see the '.env-template' file for possible alternat
    # parameters for a 'production' deployment)
    SEMSIMIAN_MODE="monarch"
    SEMSIMIAN_SCHEME="http://"
    SEMSIMIAN_HOST="api-v3.monarchinitiative.org"
    SEMSIMIAN_PORT=""  # default is HTTP port '80'
    SEMSIMIAN_SEARCH="/v3/api/semsim/search"
    
    # Front End Web Service
    WEB_HOST=0.0.0.0
    WEB_PORT=8080
    
    # TRAPI Service Endpoint
    # Use a real host name or IP here during deployment,
    # e.g. something like:
    # MMCQ_SERVICE_ADDRESS=trapi-mcq.monarchinitiative.org
    MMCQ_SERVICE_ADDRESS="localhost"
    MMCQ_TITLE="Monarch SemSimian MCQ"
    MMCQ_VERSION='1.4.0'
   ```

#### Troubleshooting

You may occasionally see the following mysterious error: 

```
Running uvicorn APP with --host  --port 8080
INFO:     Will watch for changes in these directories: ['/code/monarch-trapi-kp']
ERROR:    [Errno -2] Name or service not known
```

especially in Docker container runs.  If you look closely here, you'll see that although 
the **--host** parameter is given to uvicorn, in fact, the parameter value is empty!

First, for reliable 'source' reading of the **.env** file, enclose all environmental variable 
values in "double quotes".   

Secondly, if you are developing under Microsoft Windows (even if using a cygwin or equivalent
bash shell), whenever you change the contents of your **.env** file,  ensure that your **.env** file has 
'unix' style **\n** end-of-line characters (i.e. no Windoze **\r** carriage returns!) by running a *nix 
command line tool like '**dos2unix**' to force all end-of-line indications to be _*nix_ compatible.

## Running the System

### Run the Server from the CLI

Run the following script to start up the server from the command line terminal (under a Unix-type operating system):

  ```bash
      ./main.sh
  ```

### Running the Server within a Docker Container

   Or build an image and run it. From the root directory, type:
  
  ```bash
    docker build --tag mmcq-test .
  ```
  
  ```bash
   docker run  --name mmcq -p 8080:8080  mmcq-test
  ```

View logs using:

  ```bash
    docker logs -f mmcq
  ```

A quicker way to deployment is to [install Docker Compose](https://docs.docker.com/compose/install/) then use the provided **docker-compose.yaml** file:

  ```bash
    docker-compose build
    
    # -d runs the container in the background
    docker-compose up -d
    docker-compose logs -f
    
    # shut the server down when finished...
    docker-compose down
  ```

Note that use of Docker Compose allows local Docker container execution of the SemSimian Server image as the 'semsim' service. In such a case, the SEMSIMIAN_MODE environment variable (i.e. in .**`.env`**) should be set to value '**server**'.

Note that the SemSimian server may be run by Compose, then accessed either by an independently running MMCQ application or the MMCQ can itself be run as a Compose service. However, the **`.env`** environment variable file should have the correct SEMSIMIAN parameters set for this (the **`.env_template`** file documents these various optional sets of parameters). The key difference is that an external MMCQ application sees the SemSimian Server running on localhost, but the the Compose managed MMCQ expects to see the SemSimian Server service on host 'semsim'. This is reflected in the environment variables.

## Viewing the System

### TRAPI API

When run the system locally from the CLI or using Docker (but not within any named host), an OpenAPI web form exposing the TRAPI API is available at http://localhost:8080/1.5/docs.  The web form has a sample JSON query input that should work (the source file for this is [here](./mmcq/examples/reasoner-trapi-1.5.json)).

All of the standard TRAPI 1.5 endpoints directly accessible, as expected. These mainly consist of the **/meta_knowledge_graph** returning the Biolink Model compliant dictionary of edge templates and the **/query** endpoint for posting queries to the system.

Note that for the **/query** endpoint, the TRAPI query graph body can have the (optional) extra non-TRAPI standard JSON object key **limit** which instructs the system about the maximum number of results should be returned (Default: return the top 5 results). The current maximum allowable SemSimian value for this value appears to be 50. Higher values will trigger a 422 HTTP return code error.

### 'Common' API

An additional set of endpoints - so-called 'COMMON' API endpoints - is available at http://localhost:8080/common/docs.  Aside from accessing available release metadata about the system (via the /common/metadata path), this set of endpoints also provides a few non-TRAPI general purpose endpoints to retrieve specific data results more conveniently than TRAPI, such as retrieving a node record by CURIE.

Only the **/metadata** endpoint is implemented at this moment.


### AWS deployment

- create an AWS EC2 instance
- ssh to the instance
- install docker / start the service
- build the docker image
- run the docker image in the background
