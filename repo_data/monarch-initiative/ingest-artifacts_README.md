## Ingest-Artifacts

This repo is to store artifacts generated ingesting Monarch's sources via Dipper,
 as data is explored, modeled, transformed, and quality-assured.
 Issues and discussion realted to source data ingest continue to live in the [main Dipper repo](https://github.com/monarch-initiative/dipper). 

In this repo, each Monarch data source has its own directory holding the following types of artifacts:
  
 - _**Source Data Views:**_  Subsets or tidy versions of source data to facilitate exploration.
 - _**Notebooks:**_   Sharable notebooks set up for exploration of source data to be converted to RDF by Dipper.
 - _**Ontologist Cmaps:**_   Standardized diagrams that specify a target data model for a particular source, along with informal transform specifications for mapping source data to the target model. (The cmap files can be created and viewed with the **program [here](http://cmap.ihmc.us/))**.
 - _**Dipper RDF files:**_  Slim versions of each transformed data set that holds selected subset of records for QA and testing purposes.
 - _**Test Querys:**_   SPARQL or Cypher query used for exploration and QA of Dipper outputs. 
 - _**Documentation:**_  Draft versions of data model diagrams.
 
 -----------
 
 Certain ingest-related artifacts live elsewhere in Monarch's ecosystem. These include:  
 - **Data QA Logs**: Google Docs used to track ontologicaly motivated exchanges on data testing and QA for a given source - currently live [here](https://drive.google.com/drive/u/0/folders/0ByKzIoedGeqJVHlxY0x5QXRVT0U).  
 - **Term Translation Tables**: Text documents that will hold source-to-target concept and IRI mappings used to convert data for a given source - live in the main Dipper repo [here](https://github.com/monarch-initiative/dipper/tree/master/translationtable).  
 - **Unit tests**: Automated scripts to test specific aspects of Dipper outputs. These also live in the main dipper repo.  
