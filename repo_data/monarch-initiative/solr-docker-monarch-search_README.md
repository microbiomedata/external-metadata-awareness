# solr-docker-monarch-search
Docker image to create the solr index for the search core.

**Build the docker image locally:**

docker build -t solr-docker-monarch-search .

**Create the index:**

docker run -v /tmp/solr:/solr solr-docker-monarch-search