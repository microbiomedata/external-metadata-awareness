# SciGraph-docker-monarch-ontology
Build two Docker images with the monarch configs. Uses master HEAD from the SciGraph github repo.

## !!Deprecated!! See https://github.com/monarch-initiative/scigraph-docker

Need to have docker installed in order to run the build.

**Generate the docker images locally:**

mvn package


**Load the graph:**

docker run -v /tmp/graph:/scigraph scigraph-load-monarch

**Run the services:**

docker run -v /tmp/graph:/scigraph -d -p 9000:9000 --name scigraph-services scigraph-services-monarch

**Stop the services:**

docker stop scigraph-services

**Read logs of the services:**

docker logs scigraph-services

**Tips, remove all the local images**

docker rm $(docker ps -a -q)

docker rmi $(docker images -q)

**Enabling the image writers**

add that in the /etc/rc.local
Xvfb :1 -screen 0 800x600x16 &

and that in the /etc/environment
export DISPLAY=:1
