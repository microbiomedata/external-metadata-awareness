# biosamples-analysis
Contains python scripts and cypher to read BioSamples info from Solr, store in Neo4J database

Docker
======


The plan is to have 4 different docker containers:
	collate-attributes to query Solr and create a single combined CSV
	create-csv to split that combined CSV into separate ones
	build-neo to use the neo4j bulk loader to create a graph database
	neo-data to have a self-contained neo4j server with data inside

docker-compose up collate-attributes
docker-compose up create-csv
docker-compose up populate-neo4j
docker-compose up neo4j-server(-local)

Neo4J Server Local
======
The Neo4J Server Local container is a docker container with just the neo4j server. The data is
passed using volumes.
In order to configure the server inside the container, it's necessary to follow this procedure
1. In the `docker-compose.yml` uncomment the `command` line withing the `neo4j-server-local` task
2. Launch `docker-compose up neo4j-server-local`. This will create a template into the neo4j-server-local/conf folder
for the configuration files necessary to neo4j
3. Update the `.conf` files as you need -- e.g increase java heap memory, map the server ips (0.0.0.0:7474 for TCP and 0.0.0.0:7687 for BOLT)
4. Comment back the `command` line in the `docker-compose.yml` file
5. Run `docker-compose up neo4j-server-local` eventually

Neo4J Known Host problems
======
Sometimes happens that the python script are not working due to a invalid certificate in the `~/.neo4j/know_host` file.
In order to solve this, run this command that remove all the known_hosts from the file
```
echo "" > ~/.neo4j/know_hosts
```
