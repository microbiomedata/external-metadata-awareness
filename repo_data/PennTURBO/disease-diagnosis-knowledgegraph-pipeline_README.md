# Building a TURBO disease/diagnosis knowledge graph

### Background

A knowledge graph with normalized paths from MonDO disease classes to ICD code terms can be inserted into a GraphDB triple store by running:

https://github.com/PennTURBO/disease-diagnosis-knowledgegraph-pipeline/blob/master/R/disease_diagnosis_dev.R

### Running with pre-built Docker configuration

**1. Clone this repository to the machine you'd like to run the script.** To be safe, it should have 100 GB of free disk space and at minimum 25 GB of RAM available. You will need to have docker-compose installed.

**2. Ensure you have a UMLS license.** If you don't have one, sign up for one here: https://uts.nlm.nih.gov/license.html. It can take a few days to obtain the license.

**3. In the config/ directory, copy disease_diagnosis_credentials.yaml.template to disease_diagnosis_credentials.yaml.** Then insert your valid UMLS credentials and a username/password for the MySQL database (can be anything) into disease_diagnosis_credentials.yaml. Make sure not to leave any extraneous spaces.

**4. Sign up to receive the GraphDB Free download at https://www.ontotext.com/products/graphdb/graphdb-free/.** This process should be quick. You'll receive an e-mail after signing up which will give you the option to download the standalone server as a .zip file. Once downloaded, put the .zip file in docker/graphdb/.

**5. Update GraphDB Free version number** in the file docker/graphdb/Dockerfile. You should see a line starting with "ARG version" near the top of the page, set to some default value. If the version of graphDb you downloaded is different, make the necessary change and save the file.

**6. Run "docker-compose build" on your command line** from the diease_to_diagnosis_code repo. This step will likely take quite some time, as a lot of packages will be downloaded. Or, skip directly to the next step which will automatically trigger the build if not done already.

**7. Run "docker-compose up" on your command line** from the diease_to_diagnosis_code repo once the project is built. The pipeline will begin and will run for several hours. Once it completes, you should have a ready-to-use Disease-to-Diagnosis knowledge graph available at localhost:7200.

Throughout the build, you will see repeated messages of:

`mysql is awaiting completion of the RRF generation process. Checking again in 60 seconds...`

and later,

`builder is awaiting completion of the mysql process. Checking again in 60 seconds...`

This is normal and expected. See [Issue #2](https://github.com/PennTURBO/disease_to_diagnosis_code/issues/2) for why this is happening and how it can be improved.

### Building it yourself

## Prerequisites 

**Running the script requires a GraphDB triplestore server** from Ontotext (https://www.ontotext.com/products/graphdb/). Very similar scripts have been run with the free edition, using versions back to late 8.x. The most recent build was executed with a trial version of GraphDB Enterprise Edition 9.1.1, running under Oracle Java 11.0.6. Networking concerns like firewalls and VPNs are left to the reader.

**A disease/diagnosis repository must be created in the GraphDB server.** `disease_diagnosis_dev.R` clears the repository each time it is run, so the repository can be reused/only needs to be created once. This can be performed within GraphDB's web interface or via a REST call. To create the repo via the web interface, visit the repository configuration page at `http://graphdb_server.domain:port/repository`. The default port is 7200. _See your GraphDB administrator if a password is required._ 

- click the "Create new repository" button
- give the repository a name (with no whitespace)
- set the ruleset to "No inference"
- enable the context index
- otherwise leave the default settings and click "create"

To create the repository programmatically, see 

http://graphdb.ontotext.com/free/devhub/workbench-rest-api/location-and-repository-tutorial.html#create-a-repository

A turtle-formatted configuration file is required for programmatic repository creation. An applicable sample follows:

```turtle
#
# RDF4J configuration template for a GraphDB EE worker repository
#
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rep: <http://www.openrdf.org/config/repository#>.
@prefix sr: <http://www.openrdf.org/config/repository/sail#>.
@prefix sail: <http://www.openrdf.org/config/sail#>.
@prefix owlim: <http://www.ontotext.com/trree/owlim#>.

[] a rep:Repository ;
    rep:repositoryID "disease_diagnosis_dev" ;
    rdfs:label "" ;
    rep:repositoryImpl [
        rep:repositoryType "owlim:ReplicationClusterWorker" ;
        rep:delegate [
            rep:repositoryType "owlim:MonitorRepository" ;
            sr:sailImpl [
                sail:sailType "owlimClusterWorker:Sail" ;
           
                owlim:owlim-license "" ;
    
                owlim:base-URL "http://example.org/owlim#" ;
                owlim:defaultNS "" ;
                owlim:entity-index-size "10000000" ;
                owlim:entity-id-size  "32" ;
                owlim:imports "" ;
            owlim:repository-type "file-repository" ;
                owlim:ruleset "empty" ;
                owlim:storage-folder "storage" ;
    
                owlim:enable-context-index "true" ;

                owlim:enablePredicateList "true" ;

                owlim:in-memory-literal-properties "true" ;
                owlim:enable-literal-index "true" ;

                owlim:check-for-inconsistencies "false" ;
                owlim:disable-sameAs  "true" ;
                owlim:query-timeout  "0" ;
                owlim:query-limit-results  "0" ;
                owlim:throw-QueryEvaluationException-on-timeout "false" ;
                owlim:read-only "false" ;
    owlim:nonInterpretablePredicates "http://www.w3.org/2000/01/rdf-schema#label;http://www.w3.org/1999/02/22-rdf-syntax-ns#type;http://www.ontotext.com/owlim/ces#gazetteerConfig;http://www.ontotext.com/owlim/ces#metadataConfig" ;
            ]
        ]
    ].
```



 _After creating the disease diagnosis repository, a security policy can be applied by visiting `http://graphdb_server.domain:port/users`_. The default port is 7200.



**Running the script requires an R interpreter**, whose canonical source is https://cran.r-project.org/.  The most recent build was performed with the following version of R

`R version 3.6.2 (2019-12-12) -- "Dark and Stormy Night"`

`Platform: x86_64-apple-darwin15.6.0 (64-bit)`

The script explicitly imports the following packages:

- library(config)
- library(httr)
- library(igraph)
- library(SPARQL)

**These packages can be obtained with this one-time R command:**

`install.packages(c("config", "httr", "igraph", "SPARQL"))`

The package installer may suggest updating dependencies. This may require administrative privileges and could take several minutes. There is a very small chance that upgrading packages may cause conflicts or incompatibilities. That judgement call is left to the reader.

The table below provides an elaboration on the dependencies of those explicit imports, in terms of base R and additional packages. The `install.packages()` call should resolve the dependencies, so the table is provided principally for background information and debugging.

| Package | Version | Depends    | Imports                                                      | License            | Built |
| ------- | ------- | ---------- | ------------------------------------------------------------ | ------------------ | ----- |
| config  | 0.3     | NA         | yaml (>= 2.1.13)                                             | GPL-3              | 3.6.2 |
| httr    | 1.4.1   | R (>= 3.2) | curl (>= 3.0.0), jsonlite, mime, openssl (>= 0.8), R6        | MIT + file LICENSE | 3.6.2 |
| igraph  | 1.2.4.2 | methods    | graphics, grDevices, magrittr, Matrix, pkgconfig (>= 2.0.0),stats, utils | GPL (>= 2)         | 3.6.0 |
| SPARQL  | 1.16    | XML, RCurl | NA                                                           | GPL-3              | 3.6.2 |



**[A configuration file](disease_diagnosis_template.yaml) is also required for `disease_diagnosis_dev.R` itself. See also _Execution_ below.**

One configuration file can be loaded with the specifications for multiple different GraphDB endpoints. One of the specifications must be assigned to the  `selected.gdb.configuration` parameter in the default block, which also sets  some other, non-graphdb-related parameters

The terms `api.user` and `api.pass` refer to a GraphDB user with permission to write in the disease diagnosis repository, along with that user's password.

**The configuration file provides the names of two RDF files that must be present in the GraphDB server's import directory.** 

- `icd9_to_snomed.triples.file`
- `snomed.triples.file`

The location of the GraphDB import directory can be determined by visiting `http://graphdb_server.domain:port/import#server` and clicking on the "? Help" button in the upper right. The default port is 7200. It can also be determined by examining the  `<graphdb-distribution>/conf/graphdb.properties` file, understanding that most of the settings will be undefined and therefore set to implicit defaults.

- The **`icd9_to_snomed.triples.file`** parameter should be set to the path of a file containing an RDF direct mapping of the [National Library of Medicine's ICD9CM/SNOMED mappings](https://www.nlm.nih.gov/research/umls/mapping_projects/icd9cm_to_snomedct.html). **Contrary to recent claims, these mappings are updated (yearly), and the [disease diagnosis workflow includes a method for regenerating them in a mostly automated fashion](ICD9CM_SNOMED_MAP-to-RDF.md).** A [UMLS license](https://uts.nlm.nih.gov/license.html) is required to obtain the tabular ICD9CM/SNOMED mappings. 

- **The `snomed.triples.file`** parameter should point to a SNOMED RDF file in Bioportal style. Many RDF files, even those containing UMLS content, are freely available at the NCBO Bioportal (http://bioportal.bioontology.org/). However, SNOMED requires users to agree to terms of use, so the Bioportal does not redistribute their derived SNOMED RDF. Therefore it is necessary to 

    - connect to the UMLS servers (via a web interface or via REST). Requires a UMLS account.
    - download the UMLS distribution
    - unpack the UMLS archive into RRF "rich release format" files (and probabliy subset them) with the bundled MetaMorhoSys Java application
    - run a Bash script to load the RRF files into a MySQL database
    - run the umls2rdf Python script to dump the MySQL contents to RDF

[Detailed directions are avaialble](SNOMED_RDF_generation.md), but the process requires some manual steps and will be slightly different from one platform to another (Windows, Mac, Linux, etc.)

## Execution:

`Rscript <script path>/disease_diagnosis_dev.R <optional configuration file path>`

If a configuration file argument is passed and that file exists,  `disease_diagnosis_dev.R` will attempt to parse it and continue. No error handling is in place yet for the case where the file exists but is not valid. 

If no existing configuration file is passed,  `disease_diagnosis_dev.R`  looks for  `disease_diagnosis.yaml` in the current working directory and continues. Again, no error handling is performed.

