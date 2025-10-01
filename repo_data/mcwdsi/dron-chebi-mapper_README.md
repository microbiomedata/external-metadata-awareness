# dron-chebi-mapper
Calls BioPortal API to look for matches in ChEBI to DrOn ingredient terms derived from RxNorm

mvn compile
mvn dependency:copy-dependencies
<put your own BioPortal API key in a file src/main/resources/api-key.txt>   //NOTE: this file is git ignored if you name it exactly thusly
java -cp "./target/dependency/*:./target/classes" edu.ufl.bmi.ontology.ChebiClassSearcher ./src/main/resources/config.properties > dron-chebi-mappings.txt &
<it will run for ahwile - it's a big input file>
