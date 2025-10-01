### monarch-stack
Specification for deploying monarch services with docker-compose

<!-- MarkdownTOC -->

- [Host Environment](#host-environment)
- [Downloading Service Data and Configs](#downloading-service-data-and-configs)
  - [Fetching all data](#fetching-all-data)
  - [Directory structure](#directory-structure)
  - [Fetching data for a single service](#fetching-data-for-a-single-service)
- [Running Docker Compose](#running-docker-compose)
- [Testing](#testing)

<!-- /MarkdownTOC -->

### Host Environment

The docker-compose commands require a host with the following:
- Docker Engine > 19.03.0
- Docker Compose > 1.25.5
- User in the docker group, with group access to GIDs 8983 (solr) and 14728 (scigraph)
- Directory with > 500 GB space to store current and previous data releases

### Downloading Service Data and Configs

Data and configuration files can be downloaded by running make.  If running directly on
the host this will require gcc and pigz.  Alternatively, this can be run with 
[docker](https://hub.docker.com/repository/docker/monarchinitiative/gcc-pigz)

#### Fetching all data

```
ARCHIVE=https://archive.monarchinitiative.org/202003 \
UI_RELEASE=https://github.com/monarch-initiative/monarch-ui/releases/download/v1.0.2/static-assets.tar.gz \
DATADIR=./data \
make all
```

Or with docker:

```
docker run \ 
     --workdir /usr/src/ \
     --volume `pwd`:/usr/src/ \
     monarchinitiative/gcc-pigz:10.1  \
        /bin/sh -c 'umask 0002 && \
          ARCHIVE=https://archive.monarchinitiative.org/202003 \
          UI_RELEASE=https://github.com/monarch-initiative/monarch-ui/releases/download/v1.0.2/static-assets.tar.gz \
          DATADIR=/srv/monarch \
          make'
```

#### Directory structure

The data directory will have the following structure:

/path/to/data/
  - solr/
  - solr-old/
  - scigraph-data/
  - scigraph-data-old/
  - scigraph-ontology/
  - scigraph-ontology-old/
  - owlsim/
  - owlsim-old/
  - monarch-ui/
  - monarch-ui-old/

Each directory contains data and configuration files needed for the Monarch services.
The -old directories contain the files for the previous run of make or will be empty if
this is the first time running make.

#### Fetching data for a single service

Data for a single service can be fetched by changing the make target:

```
make fetch_solr
```

See ```make list``` to view all targets

### Running Docker Compose

All Monarch services can be composed by running
```
DATADIR=/path/to/data/ docker-compose up
```
Note that owlsim takes 12 minutes to initialize, followed by a warm up query generated
by the biolink container which takes an additional ~20 minutes.

In practice, our backend services change infrequently so it is useful to separate 
data providing backend services (solr, scigraph-data, scigraph-ontology, owlsim) and
our API and front end (biolink, monarch-ui).  Therefore, these can be composed independently:

```
DATADIR=/path/to/data docker-compose -f services/monarch-app.yml up
DATADIR=/path/to/data docker-compose -f services/backend.yml up
```

### Testing

Tests are a WIP, but the services/ compose files contain healthchecks.
