# csv2caDSR

A very simple program for harmonizing CSV files against
Common Data Elements from the [caDSR](https://datascience.cancer.gov/resources/metadata),
which we access using the [caDSR-on-FHIR service](https://github.com/HOT-Ecosystem/cadsr-on-fhir/).

## How to use

Using csv2caDSR is an overly complicated process (it will be improved in later versions if needed):

1. `sbt "run --csv example.csv --to-json example.json"`
    - Creates a JSON file describing the columns in the CSV file.

2. Fill in the caDSR values in the CSV file.

3. `sbt "run --json example-with-caDSRs.json --to-json example-with-values.json"`
    - Fills in values for caDSR values.

4. Map CSV values to caDSR values.

5. `sbt "run --json example-with-values.json --to-json example-with-enumValues.json"`
    - Retrieve descriptions and concept identifiers for the mapped caDSR values.

6. `sbt "run --csv example.csv --json example-with-enumValues.json --to-csv example-mapped.csv"`
    - Map CSV file to CDEs based on the mapping information in `example-with-enumValues.json`.

7. `sbt "run --csv example.csv --json example-with-enumValues.json --to-pfb examples/avro/example.avro"`
    - Convert CSV file to a PFB file in Avro.

8. `sbt "run --csv example.csv --json example-with-enumValues.json --to-cedar examples/cedar/prefix --upload-to-cedar --cedar-upload-folder-url https://repo.metadatacenter.org/folders/bba27862-cbfb-474b-a6d0-bbf03c297df9"`
    - Convert CSV file to CEDAR instance data (using the prefix provided, in this example at `examples/cedar/prefix.instance.${index}.json`),
      generate a CEDAR template (in this example, at `examples/cedar/prefix.template.json`), and optionally upload it to a particular CEDAR template.

9. `sbt "run --csv example.csv --json example-with-enumValues.json --to-jsonld examples/jsonld/prefix --generate-shacl"`
    - Convert CSV file to JSON-LD (using the prefix provided, in this example at `examples/jsonld/prefix.instance.${index}.jsonld`) and
      generate a SHACL file (in this example, at `examples/jsonld/prefix.shacl.ttl`).