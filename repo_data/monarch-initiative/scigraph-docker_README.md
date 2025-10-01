# scigraph-docker
Build scigraph docker image with the monarch configs. Uses master HEAD from the SciGraph github repo.

**Generate the monarch config files locally:**

    ./conf/build-load-conf.sh data
    ./conf/build-service-conf.sh data

For building the Monarch Ontology graph:

    ./conf/build-load-conf.sh ontology
    ./conf/build-service-conf.sh ontology
 
**Build the SciGraph Image:**

    docker build -t scigraph .

**Load the graph:**

    docker run \
      -v `pwd`/data:/data \
      -v `pwd`/conf:/scigraph/conf \
      scigraph load-scigraph monarchLoadConfiguration.yaml

**Run the services:**

    docker run \
      -v `pwd`/data:/data \
      -v `pwd`/conf:/scigraph/conf \
      -d -p 9000:9000 \
      --name scigraph-services \
      scigraph start-scigraph-service monarchConfiguration.yaml

**Stop the services:**

    docker stop scigraph-services

**Read logs of the services:**

    docker logs scigraph-services

**Tips, remove all the local images**

    docker rm $(docker ps -a -q)

    docker rmi $(docker images -q)
