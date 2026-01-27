# urigen-id-generator
Script that takes a set of new ontology terms and runs them through Urigen to batch-generated IDs.


The script takes 3:
- an input tsv file
- the path to an output tsv file
- your Urigen API key

The input file tsv needs to contain at least 2 columns, ID and label, separated by a pipe (|), eg
```
ID|Label
ID|A rdfs:label
|PacBio Sequel System
|PacBio RS II
|ONT MinION
```
The ID must be in the first column and the label in the 2nd one, and the ID field must be empty for any terms for which an ID should be generated. The input file can have as many columns as you like, as long as all columns are separated by a pipe and the first two columns are ID and label, respectively.

To find out your API key, log into http://garfield.ebi.ac.uk:8180/urigen

The script assumes that you want to generate new IDs for EFO terms. For other ontologies, you will have to edit the script to change the ONTOlOGY_ID value as well as the default URI to CURIE shortening.

Run the script in your favourite IDE or via the command line using

```
python3 idgenerator.py -i some_new_entities.tsv -o new_entities_with_ids.tsv -a MYURIGENAPIKEY
```

