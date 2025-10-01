# PennTurbo Knowledgegraph API #

REST API server for communication with resources produced by the knolwedgegraph Pipelines

## Installation ##
knowledgegraph-api is a Scala project that can either be run locally through SBT (Scala Build Tool), or run in a docker container.

### Requirements ###
#### Local
- SBT 
	- Minimum version is 1.1.4
		- [Official SBT Setup Guide](https://www.scala-sbt.org/release/docs/Setup.html)

#### Docker
- Docker
    - Most recent stable release, minimum version is 17.06.0
      - [Official Docker Website Getting Started](https://docs.docker.com/engine/getstarted/step_one/)
      - [Official Docker Installation for Windows](https://docs.docker.com/docker-for-windows/install/)
    - **Enable File Sharing**:  Configure file sharing in Docker for the directory or drive that will contain the source code ([Windows configuration](https://docs.docker.com/docker-for-windows/#file-sharing))
    - **Runtime Memory**: (Mac and Windows only) If using **Windows** or **Mac**, we recommend docker VM to be configured with at least 6GB of runtime memory ([Mac configuration](https://docs.docker.com/docker-for-mac/#advanced), [Windows configuration](https://docs.docker.com/docker-for-windows/#advanced)).  By default, docker VM on Windows or Mac starts with 2G runtime memory.

### Configuration ###
Copy `turboAPI.properties.template` to `turboAPI.properties`.  Update passwords as necessary.


## Build & Run ##

### Local Build & Run ###
```sh
$ cd knowledgegraph-api
$ sbt
> jetty:start
```

### Docker ###
#### Build
```
docker-compose build
```


#### Run
```
docker-compose up
```

This runs `sbt ~"jetty:start"` in the context of a docker container.  May take several minutes to compile.

## General Use ##

For free text lookup, send POST JSON to "http://localhost:8080/medications/findOrderNamesFromInputString"

Example input for free text lookup:

    {"searchTerm":"analgesic"}

For URI lookup, send POST JSON to "http://localhost:8080/medications/findOrderNamesFromInputURI"

    {"searchTerm":"http://purl.obolibrary.org/obo/CHEBI_35480"}

Note that when running from SBT the default port is 8080, as a precompiled .jar the default port is 8089.

See dashboardApiDocs.raml for more explicit documentation.


## Tests ##
The integration test suite can be run localy with the command `sbt test` or via docker with the command `docker-compose -f docker-compose-int-test.yml up`.

See [ScalaTest documentation](http://www.scalatest.org/user_guide/using_scalatest_with_sbt) for details.

- JUnit test results will be located in `target/test-reports/*.xml`
- HTML test results will be located in `target/test-reports/html/*`


