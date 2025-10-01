# Monarch Solr 

A Dockerized instance of the Monarch KG as a Solr database.

It is assumed that you have already [installed Docker](https://docs.docker.com/get-docker/) and [Compose](https://docker-docs.netlify.app/compose/install/) or perhaps have the [Docker Desktop](https://docs.docker.com/compose/install/) running on your local system.


## Running the System

First, make sure that Docker (or the Docker Desktop) is running then Docker Compose is used to build the local Monarch Solr system. Note that since we are simply directly using a standard Solr Docker image from DockerHub, there is no 'build' step needed.

```bash
docker-compose up -d
```

To monitor the logs:

```bash
docker-compose logs -f
```

To stop the server:

```bash
docker-compose down
```

The Solr instances with Monarch data loaded should now be visible at **http://localhost:8983**. 
