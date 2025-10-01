# complexphen
Model for complex diseases

complexphen is a Java library based on phenol that intends to ingest, Q/C, and analyze the new common-disease model. 
We may consider merging it into phenol at a later time.


For now, there are some prototype files in the ``src/test/resources/annotations`` directory with sample annotation
files that are used for testing/developing the code.


## test drive

Clone and build the application.

```bazaar
git clone https://github.com/monarch-initiative/complexphen
cd complexphen
mvn package
```

There is a test file in the src/test/resources directory that can be used for a test drive. First
we need to download ontology files and then analyze a test file.
```bazaar
java -jar complexphen-cli/target/complexphen.jar download
$ java -jar complexphen-cli/target/complexphen.jar annotation-qc -s complexphen-core/src/test/resources/stroke.tsv 
[INFO] Loading hp.json
log4j:WARN No appenders could be found for logger (org.monarchinitiative.phenol.io.OntologyLoader).
log4j:WARN Please initialize the log4j system properly.
log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
[INFO] Loading mondo.json
[INFO] Loading ecto.json
###--- Complex Disease Model ---###

Stroke disorder (MONDO:0005098)
has_phenotype:
  Aphasia (HP:0002381) HPO:probinson[15-11-2021]
risk_increased_by_disease:
  Essential hypertension (MONDO:0001134) HPO:probinson[15-11-2021]
risk_increased_by_exposure:
  smoking (NCIT:C1543) HPO:probinson[15-11-2021]
 - No phenotype risk annotations
```

