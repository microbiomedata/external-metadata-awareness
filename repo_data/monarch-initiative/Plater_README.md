## PLATER

![test batch](https://travis-ci.com/TranslatorSRI/Plater.svg?branch=master)

PLATER is a service to stand up REST endpoint over a neo4j database.
There are some restrictions on the data structure of the Neo4j backend to be fully utilized through PLATER.

> **NEO4J data structure restrictions:**
> * All nodes should have an `id` to be searchable (Used in querying single Nodes)
> * All edges should have an `id` to be searchable (Used in generating ReasonerAPI)
> * Nodes labeled `Concept` are ignored. 

### Installation

To run the web server directly:

#### Create a virtual Environment and activate.

    cd <PLATER-ROOT>
    python<version> -m venv venv
    source venv/bin/activate
    
#### Install dependencies
    
    pip install -r PLATER/requirements.txt
    
 
#### Configure PLATER settings
   
   Populate `.env-template` file with settings and save as `.env` in repo root dir.
   
   ```bash   
    WEB_HOST=0.0.0.0
    WEB_PORT=8080
    NEO4J_HOST=neo4j
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=<change_me>    
    NEO4J_HTTP_PORT=7474
    PLATER_TITLE='Plater'
    PLATER_VERSION='1.1.0'
    BL_VERSION='1.6.1'

   ```
   
  
#### Run Script
  
    ./main.sh
 
    
 ### DOCKER 
   Or build an image and run it. 
  
  ```bash
    cd PLATER
    docker build --tag <image_tag> .
    cd ../
  ```
  
  ```bash
   docker run --env-file .env\
    --name plater\
    -p 8080:8080\
    --network <network_where_neo4j_is_running>\
    plater-tst

  ```
 
 ### Clustering with [Automat Server](https://github.com/RENCI-AUTOMAT/Automat-server/) \[Optional\]
 You can also serve several instances of plater through a common gateway(Automat). On specific instructions 
 please refer to [AUTOMAT's readme](https://github.com/RENCI-AUTOMAT/Automat-server/blob/master/README.md)
  
 

 ### Miscellaneous
 ###### `/about` Endpoint 
 The `/about` endpoint can be used to present meta-data about the current PLATER instance. 
 This meta-data is served from `<repo-root>/PLATER/about.json` file. One can edit the contents of
 this file to suite needs. In containerized environment we recommend mounting this file as a volume.
 
 Eg:
 ```bash
docker run -p 0.0.0.0:8999:8080  \
               --env NEO4J_HOST=<your_neo_host> \
               --env NEO4J_HTTP_PORT=<your_neo4j_http_port> \
               --env NEO4J_USERNAME=neo4j\
               --env NEO4J_PASSWORD=<neo4j_password> \
               --env WEB_HOST=0.0.0.0 \
               -v <your-custom-about>:/<path-to-plater-repo-home>/plater/about.json \
               --network=<docker_network_neo4j_is_running_at> \    
                <image_tag>
    
``` 
 
   
    
    
