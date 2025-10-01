Convert SSSOM TSV to nodes and edges CSV files that can be ingested by Neo4J 3.1.1 used by OxO.

Requirements:
Java 17, Python 3.
Environment variables:
$INPUT_DIR = directory containing SSSOM files or it can point to a single SSSOM file that needs to be imported.
$OUTPUT_DIR = directory where output files will be written.
$NEO4J_HOME = directory where Neo4J is installed. Files to be imported will be copied to $NEO4J_HOME/import.

This consists of 2 steps:

(1) Generate CSV files:
To build, using Java 17:

    mvn clean package

Run `ols2csv.sh` which takes 1 input parameter, namely the URL where OLS can be accessed. I.e.:

    ols2csv.sh https://www.ebi.ac.uk/ols4/

This will result in the following files to be written out to the $OUTPUT_DIR directory:

- `datasources.csv`
- `ols_mappings.csv`
- `ols_terms.csv`

(2) Import CSV files into OxO Neo4J:

Ensure that Neo4J is running and ensure that the `config.ini` has to correct connection information for Neo4J. Then the 
CSV files can be imported using 

    import2neo4j.sh

(3) Once step (2) is completed, the OxO1 indexer can be run to create the Solr indexes. This is using Java 8:

    java -Xmx10g -jar ./oxo-indexer/target/oxo-indexer.jar








