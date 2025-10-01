[![Docker Image CI](https://github.com/PennTURBO/carnival-tox-temporal-omop/actions/workflows/docker-CI.yml/badge.svg)](https://github.com/PennTURBO/carnival-tox-temporal-omop/actions/workflows/docker-CI.yml)

# Overview
This is a demonstration project that uses [Carnival](https://github.com/carnival-data/carnival) harmonize to patient data from [OMOP](https://ohdsi.github.io/CommonDataModel/index.html) data sources with publicly available data sources like the [United States Census Data](https://www.census.gov/data/developers.html) to create patient exposome cohort graphs compatable with [ComptoxAI](https://www.comptox.ai) for machine learning analysis.

# Running the Project

### Quickstart
```
git clone https://github.com/PennTURBO/carnival-tox-temporal-omop.git # if using a GitHub token
# git clone git@github.com:PennTURBO/carnival-tox-temporal-omop.git # if using an SSH key linked to your GitHub account

cd carnival-tox-temporal-omop
Download https://upenn.box.com/s/285hchcxaeatnik4sbnj3w7hkdd6h10o and move it to this directory.
tar -xf synpuf_data.tar
docker compose up db # It may take a few minutes to initally build the database

Access the database from the host running Docker:
address: localhost
user: postgres
password: postgres
database: synpuf
port: 5432 # set in .env, passed in through docker-compose.yml
Postgres database files are stored in Docker volume pgdata, which mounts inside Docker as /var/lib/postgresql/data

ctrl+c to stop


To run the application and generate the cohort graph:
docker compose up

While the application is running, cohort graph can be exported by visiting
* http://localhost:5858/export_graphml
* http://localhost:5858/export_graphson

ctrl+c to stop
```

The OMOP patient_ids used to seed the graph and patient address information is configured in `config/cohort_config.yml`.

Census API keys can be used by copying `.secrets.env-template` to `.secrets.env` and adding your key to `.secrets.env`.

# Preliminary Setup

Before running the quickstart, you may need to do some one-time prelimary setup.

### Install git and set up GitHub 

Set up GitHub authentication with git. Upload your public SSH key or generate a token.

### Use your existing SSH public key

Upload ~/.ssh/id_rsa.pub to https://github.com/settings/keys

To checkout the project, run `git clone git@github.com:PennTURBO/carnival-tox-temporal-omop.git`

For more information see:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

### Use a GitHub token

Create a token, https://github.com/settings/tokens

Save it and treat it as secret. When cloning this private repository, use your GitHub username as your login and the token as your password, not your GitHub password.

To checkout the project, run `git clone https://github.com/PennTURBO/carnival-tox-temporal-omop.git`

For more information see:
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

### Install one of Docker Desktop, Docker, or Podman

**Note: you may need to set the appropriate [file sharing settings](https://docs.docker.com/desktop/settings/windows/#file-sharing) in Docker for the files (test report output, graph exports etc.) to be written.**
<!-- 

https://podman.io/getting-started/installation
https://podman-desktop.io/docs/Installation

## Unimplemented quickstart steps

```
docker compose up db -d
docker compose up carnival

Open a browser to check API endpoints:
http://localhost:5858
http://localhost:5858/endpoint

ctrl+c to stop
```

## Detailed Setup
### Prerequisites: Docker and git

On [Windows](https://docs.docker.com/desktop/windows/install/) and [Mac](https://docs.docker.com/desktop/mac/install/), install Docker Desktop. 


Note that as non-profit institutions, we can use the free "Personal" license.

[Docker Licensing FAQ](https://www.docker.com/pricing/faq)
*I am a researcher at a university (or another not-for-profit institution); do I or my research assistants need to purchase a Pro, Team, or Business subscription to use Docker Desktop?*

*No. You and your assistants may use Docker Desktop for free with a Docker Personal subscription.*

### 1. Clone Carnival Micronaut

```
git clone https://github.com/carnival-data/carnival-demo-biomedical.git
cd carnival-demo-biomedical
```

### 2. Build and run the app

```
docker compose build
docker compose up
```

After a few minutes, there should be a server running at `http://localhost:5858`.

API endpoints will serve JSON responses containing the case and control cohorts ([API Documentation](https://github.com/carnival-data/carnival-demo-biomedical/blob/master/docs/ResearchAnswersApi.raml)):

```
http://localhost:5858/case_patients
http://localhost:5858/control_patients
```

## Set up instructions for running the app with less Docker

Prerequisite: JDK 11, Docker, git

### 1. Clone Carnival Micronaut

```
git clone https://github.com/carnival-data/carnival-demo-biomedical.git
cd carnival-demo-biomedical
```
-->
<!--
### 3. Create Home Directory

The Carnival Micronaut Home directory will us the working directory for Carnival Micronaut.  It will include all configuration and data.

Set an environment variable to point to the home directory:

```
export CARNIVAL_MICRONAUT_HOME=/full/path/to/carnival-micronaut/carnival-micronaut-home
```
-->
<!--
### 2. Start the database using Docker

```
docker compose build db
docker compose up db
# To run in the background as a daemon use:
# docker compose up -d db
```

### 3. Build and run the app

```
./gradlew run
```

After a few minutes, there should be a server running at http://localhost:5858.

## Testing with Docker
Run tests with the following:
```
docker compose -f docker-compose-test.yml up
```
This will run the unit tests. The test results will be printed in the docker log. An exit code of 0 will be returned if the tests pass, otherwise a non-zero code will be returned.

-->

# Running the application
The applicaton can be started by the command `docker compose up`. This will start the database and webserver, and generate patient cohort graph files in graphml and graphson format in the folder `build\export`. _**Note:** you may need to set the appropriate [file sharing settings in Docker](https://docs.docker.com/desktop/settings/windows/#file-sharing) to be able to access these files directly._

Once the webserver has started, the graph can be exported from:
* http://localhost:5858/export_graphml
* http://localhost:5858/export_graphson

Basic information about the contents of the graph can be found at:
* http://localhost:5858/

# Viewing source data in Postgres

Once docker has been started using `docker compose up db`, the database can be browsed using database GUI tool such as Azure Data Studio (with the Postgres plugin).
* Host: localhost
* Port: 5432, or as specified in `.env`
* Database: synpuf
* Username: postgres
* Password: postgres

# Configuration

## Patient Cohort Configuration
The patient_ids used to seed the graph and patient address information can be configuration can be configured in the file `config\cohort_config.yml`

```
carnival-micronaut:

  # These are the patient_id values in the OMOP database used to generate the cohort graph
  patient_ids: [1,2,3]


  # This section allows configuration of the MostRecentAddress nodes associated with paients.
  most_recent_address:

    # if true, override address information in the OMOP data source.
    # if false, this section is ignored and the OMOP address data is used.
    override_omop: true

    default_address:
      address_1: "1 S Penn Square"
      address_2: ""
      city: "Philadelphia"
      state: "PA"
      zip: "19107"
      county: "PA"
      #tract: "000500" # optionally specify the census tract
```

## Keys and tokens
### US Census Data API Key
An API key can be used with requests to the US census datasets APIs. This does not seem to be required at the moment, but will be used in requests by this application if provided.

  1. Request a key from https://www.census.gov/data/developers.html
  2. Copy `.secrets.env-template` to `.secrets.env`
  3. Open `.secrets.env` and add a line that with your api key: ```CENSUS_API_KEY="MY KEY HERE" ```
  

# Running Tests

Tests can be run using the command:
`docker-compose -f docker-compose-test.yml up --abort-on-container-exit`

A test result report will be generated in `build/reports/tests`

# Graph Modeling Documentation
Initial graph modeling is being done with arrows.app and can be viewed [here](https://arrows.app/#/googledrive/ids=11I1I6cdisDc6734yv4Ro9GmgdgWiLylL), or by opening the file `https://drive.google.com/file/d/11I1I6cdisDc6734yv4Ro9GmgdgWiLylL/view?usp=sharing` in the [arrow.app](arrows.app) webpage.

# Data Sources
  * Postgres database containing [OMOP v5.2](https://ohdsi.github.io/CommonDataModel/cdm53.html) formatted patient data
    * By default, this project has a docker image that contains a Postgres database populated an OMOP formated subset of the [Synpuf](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) dataset. The [quickstart](https://github.com/PennTURBO/carnival-tox-temporal-omop/edit/location/README.md#quickstart) provides instructions on how to set this up.
      * The raw data is located in PennBox: https://upenn.box.com/s/285hchcxaeatnik4sbnj3w7hkdd6h10o
      * Extracting the raw data creates `synpuf` and `vocab` folders in the [data](https://github.com/PennTURBO/carnival-tox-temporal-omop/tree/main/data) directory, which postgres docker image loads when it is first built
  * [US Census Geocoding Service](https://geocoding.geo.census.gov/geocoder/)
  * US Census Survey Data: [API](https://www.census.gov/data/developers.html), [Explorer](https://data.census.gov)
