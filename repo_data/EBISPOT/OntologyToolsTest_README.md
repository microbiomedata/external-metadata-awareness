# Ontology Tools Developer Test

## Purpose
This test serves 2 purposes:
1. It gives you (the candidate) some idea of the work we are doing and the technologies we use. We therefore ask you to use one of our core services to retrieve information regarding ontologies. We will also ask you to use specific technologies.
1. It gives us some idea of your familiarity with the tools we are using and the quality of your work. If you choose not to take part in the test, you will not be considered for the position.

## Functional Requirements
Write a web application that will try to retrieve an ontology by ID from a local database. If the ontology cannot be found in the local database, try to request the information from OLS - the ontology lookup service (Details regarding OLS is provided below). If the ontology can not be found on OLS, give an error message.

You must use the ontology lookup service (OLS) to retrieve information regarding ontologies. Ontologies in OLS are stored by ontology ID. Some examples of ontology IDs are efo, mondo, go, ncit. Information regarding ontologies can be retrieved from OLS using its REST api. The following HTTP GET request will retrieve information regarding the efo ontology:

https://www.ebi.ac.uk/ols4/api/ontologies/efo

The general request for retrieving information regarding an ontology is:
https://www.ebi.ac.uk/ols4/api/ontologies/{ontologyId}, where {ontologyId} should be replaced with the ontologyId you want use. E.g., using the ontology id for efo this becomes https://www.ebi.ac.uk/ols4/api/ontologies/efo, for the ontology id mondo, it becomes https://www.ebi.ac.uk/ols4/api/ontologies/mondo, and so forth for other ontology IDs.

A list of all ontologies can be retrieved using 
https://www.ebi.ac.uk/ols4/api/ontologies


For each ontology, store and display the following information:
* Ontology ID - as given in OLS
* Title
* Description
* List of definition properties
* List of synonym properties.

## Non-functional requirements
* Use Spring Boot to implement the application
* Use MongoDB as a local database
* Provide a REST API for storing and retrieving information regarding ontologies.
* Use React to implement the frontend.
* Ensure all errors are logged using a logging framework of your choice (i.e., log4j, slf4j, flogger - not System.out/System.err)
* Write unit tests for your application.
* Ensure that your application can be built and tested using Maven.
* Containerize your application using Docker and provide clear instructions on how to run your application using Docker.
* Check your application into a public GitHub repository and sent the repository URL to HR. 
