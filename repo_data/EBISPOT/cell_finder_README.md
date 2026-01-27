
# Build the simple CL ontology 

`make`

# Start neo4j and elastic search service

`docker-compose up`



# Create Index in elastic search

In case previous index, you can delete with 

`curl -XDELETE http://localhost:9200/cell_finder`

Then create the ES index

`curl -XPOST http://localhost:9200/cell_finder  -d @mapping_basic.json`

Install the cell finder node libs

`yarn`

Load the data from neo4j into ES

`npm run dataimport`

# Start the cell finder app

`npm start`

