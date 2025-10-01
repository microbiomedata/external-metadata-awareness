# Convert RDF to Neo4J Graph

This utility provides a wrapper for the [Neosemantics plugin](https://neo4j.com/labs/neosemantics-rdf/) to import a TURTLE file into a Neo4j Property Graph. 

## Dependencies

Before getting started, you will need to download a [.jar](https://github.com/neo4j-labs/neosemantics/releases) of the neosemantics Neo4j plugin. We can confirm compatibility with version 3.5.0.4, and haven't tested any preceding or following verions yet. Put the .jar in a directory called `plugins/` at the base of the cloned directory. 

You will also need [SBT](https://www.scala-sbt.org/) installed to run the Scala program.

## Configuration

There are two configuration files which may come in handy. In the file `conf/namespaces.conf`, you can specify prefixes to be used in place of full namespaces in the RDF. This makes Cypher querying significanlty more pleasant. The default list of prefixes in that file can be removed and replaced, or added on to. You should see some confirmation of each prefix in the console output, like so:
```
Adding prefix owl for namespace http://www.w3.org/2002/07/owl#
Adding prefix dct for namespace http://purl.org/dc/terms/
Adding prefix rdfs for namespace http://www.w3.org/2000/01/rdf-schema#
```

In `conf/requiredNodeLabels.conf`, you can list RDF classes for which you are expecting corresponding labels for in the Neo4j graph, one per line. Prefix notation should be used. Unless the file is empty, the console output will include a count of the nodes with each of the corresponding labels in the Neo4j graph, and display a warning if any of the labels are not present. For example, the following could be added to this file:
```
owl:Class
obo:BFO_0000001
```
If you had decided to use the Mondo ontology as your RDF source, your console output might then include:
```
Found 117778 instances of nodes with label owl__Class
Found 0 instances of nodes with label obo__BFO_0000001
There were failing checks; see the output above for more information
```

Note that neosemantics is set by default to create lables by placing two underscores after the prefix.

## Running

To run the program, you must supply two command line arguments to the SBT console: the location of a TURTLE RDF file, and the location where the output Neo4j graph directory should be placed.

`run myTurtleFile.ttl output_dir`

The TURTLE file will be read into the Neo4j graph using the default neosemantics settings. We have not yet included functionality to alter the neosemantics settings via a configuration file. To change the neosemantics settings, it shouldn't be too much trouble to modify the code in the `Neo4jConnector` object.
