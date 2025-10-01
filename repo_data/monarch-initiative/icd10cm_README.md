# ICD10CM
Mondo data ingest pipeline and analyses for ICD10CM.

## Running ingest
(TODO)

## Running analyses
### Running via Python
#### Syntax
`python3 scripts/<SCRIPT_NAME>.py`

#### Example
`python3 scripts/check_valid_codes.py`

### Running via `robot`
#### Running a new analysis
There are ontological assets availablie in the `data/` directory (or will be, 
once we've set up Git-LFS properly), and SPARQL queries available in the 
`sparql/` directory. Use them as you please to run your own
[`robot` query](http://robot.obolibrary.org/query.html). Modify/add as you 
please. 

#### Running a previously run, cached analysis
The Python script actually calls `robot` using a subprocess. When it does this, 
it not only saves the results in `cache/robot/<ONTOLOGY_FILENAME>_<SPARQL_FILENAME>/results.csv`, 
but it also saves a `command.sh` in the same folder. If you `cd` into that 
folder and run `sh command.sh`, it will run the query and save the results there,
overwriting any `results.csv` in that folder.
