# solr-docker-monarch-golr
Docker image to create the solr index for the golr core.

**Build the docker image locally:**

docker build -t solr-docker-monarch-golr .

**Create the index:**

docker run -v /tmp/solr:/solr solr-docker-monarch-golr
