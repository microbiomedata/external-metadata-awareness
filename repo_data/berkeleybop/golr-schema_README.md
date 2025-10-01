[![Build Status](https://travis-ci.org/berkeleybop/golr-schema.svg?branch=master)](https://travis-ci.org/berkeleybop/golr-schema)

# golr-schema
Utility to generate a schema.xml from a yaml config file.

## Usage

Directly with Maven:
```
mvn exec:java -Dexec.mainClass="org.bbop.cli.Main" -Dexec.args="-c src/test/resources/oban-config.yaml -o /tmp/schema.xml"
```

Packaged jar:
```
mvn package
java -jar target/golr-schema-1.0-SNAPSHOT-jar-with-dependencies.jar -c src/test/resources/ont-config.yaml -o /tmp/schema.xml
```

Define multiple configs and directories (all the files from the directory will be included):
```
mvn exec:java -Dexec.mainClass="org.bbop.cli.Main" -Dexec.args="-c src/test/resources/oban-config.yaml /tmp/foo.yaml /tmp/bar/ -o /tmp/schema.xml"
```

Note that if no output file is specified, the schema.xml will be printed out on the stdout.

