# solr-docker-monarch-feature-location
Docker image to create the solr index for the feature-location core.

**Build the docker image locally:**

docker build -t solr-docker-monarch-feature-location .

**Create the index:**

docker run -v /tmp/solr:/solr solr-docker-monarch-feature-location