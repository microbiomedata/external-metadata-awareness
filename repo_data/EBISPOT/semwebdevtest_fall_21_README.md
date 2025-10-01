# Semantic Dev Tech Test  [![Build Status](https://travis-ci.com/EBISPOT/semantic_dev_tech_test.svg?branch=main)](https://travis-ci.com/EBISPOT/semantic_dev_tech_test)

Technical test for semantic dev.

This GitHub Repository has:

 *  An OWL file with an ontology of wines (src/resources/wine.owl)
 *  A script for loading OWL files into a customised Neo4j database.
 *  A `.travis.yml` file that launches a containerised Neo4j database and loads the OWL file into it.
 

### Exercise 1:

Explore the OWL file in Protege and run a reasoner.

![image](https://user-images.githubusercontent.com/112839/97699007-60bd2f00-1aa1-11eb-8e1a-ab8a5b1c98ac.png)

* Please explain, in a few clear sentences, why the reasoner classifies Barolo as an Italian wine.

Make sure docker has access to the location where you've checked out this repo.

Launch a local copy of the DB and load the ontology

```sh
docker run -d -p:7474:7474 -p 7687:7687 --volume=`pwd`:/import/  --env-file ./src/resources/env.list matentzn/vfb-prod
```

Wait until you can browse at http://localhost:7474

Then run:

```sh
python3 src/load_db.py file:///src/resources/wine.owl
```

You should now be able to browse a neo4j representation of the ontology at http://localhost:7474

* Compare the original OWL representation of the wine ontology and its representation as a Neo4j labelled property graph and document the transformation in your own words. How do the representations differ? How was the OWL representation mapped into the Neo4j representation?

### Exercise 2: 

Using a forked copy of this repo as a base, write an API library, preferably in Python\*, to query the database with methods to:

* List all grape growing regions (in the ontology)
* List all varietals  (in the ontology)
* List all types (classes) of wine  (in the ontology)
* Query for wine types and individual wines by: colour, varietal, region

Your code should:
  * have at least 3 unit tests, ideally with continuous integration via Travis or GitHub Actions
  * be well documented

If you prefer, you may base your API on SPARQL queries of the OWL ontology in place of Cypher queries of the Neo4J database.

You should include clear documentation on how to use your API.

\* While we would prefer a solution in Python, we will accept solutions in you language of choice if you are not comfortable with writing Python.

### Exercise 3:

Write a couple of paragraphs on how you might extend the OWL modelling and content to build a knowledge base of individual wines that would be useful to consumers trying to decide what wine to buy.
