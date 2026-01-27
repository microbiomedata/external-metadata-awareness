# yactp
Yet Another Clinical Trials Parser

This parser downloads data from the ClinicalTrials.gov server and extracts the cross section between a set of diseases
that descend from some MeSH term and with a list of medications of interest. For instance, we might be interested in
seeing all Clinical Trials for tyrosine kinase inhibitors and descendants of [Neoplasms - D009369](https://meshb.nlm.nih.gov/record/ui?ui=D009369).



## Setup
We need to install the SPARQLWrapper package
```
virtualenv p38 
source p38/bin/activate
pip install sparqlwrapper
```
When running the sparql command, first enter
```
source p38/bin/activate
```

## Getting MeSH Neoplasm Term IDs/names
We first need to run the ``meshSparql.py`` script, which sends a SPARQL query to MeSH and retrieves
a list of MeSH entries that descend from a MeSH term such as ``D009369``.

Run the script like this
```
python meshSparql.py -m <MeSH ID>
```
If the ``-m`` argument is omitted, the default of D009369 will be used. The script produces an output file whose name includes the date on
which the analysis was performed, e.g., ``mesh_D009369_12_05_2020.tsv`` and contains a table with entries such as the following:
```
(...)
D014685 Venereal Tumors, Veterinary
D003969 Vipoma
D014846 Vulvar Neoplasms
D017624 WAGR Syndrome
(...)
```

The file is used in subsequent steps.


## Running yactp

The expected input file is a list of medication names, one on a line. For instance,

```
afatinib
imatinib
(...)
```

Two example input files can be found in the ``example_inputs`` directory.

Run the script as follows
```
python parseCT.py -i <path-to-input-file> -m <path to the MeSH file from the first step>
```

For demonstration purposes, if you leave off the ``-i`` argument, the script will use a file in
the subdirectory ``kinase_data`` that contains just two medication names.

For each of the medications in this list, the parser downloads data using this query
```
'https://clinicaltrials.gov/ct2/download_studies?term=%s&down_count=10000&down_format=csv'
```
where ``%s`` is replaced by the medication of interest. 


The script will generate an output file called ``clinical_trials_pki_studies``. 
This file contains detailed results of parsing. The following table  shows the structure of the output file.	

<table>
<tr><td>query</td><td>org_study_id</td><td>nct_id</td><td>brief_title</td><td>start_date</td><td>completion_date</td><td>phase</td><td>condition</td><td>intervention_type</td><td>intervention_name</td><td>	mesh</td></tr>
<tr><td>afatinib</td><td>MedOPP137</td><td>NCT03623750</td><td>E GFR TKI and EGF-P TI C Ombination in EGFR mutA nt NSCL C	</td><td>July 6, 2018</td><td>August 1, 2020</td><td>Phase 1/Phase 2</td><td>Carcinoma, Non-Small-Cell Lung</td><td>Drug</td><td>EGFR-TK Inhibitor</td><td>Carcinoma, Non-Small-Cell Lung</td></tr>
<tr><td>afatinib</td><td>BIBW2992 ORL</td><td>NCT01427478</td><td>Evaluation of Afatinib in Maintenance Therapy in Squamous Cell Carcinoma of the Head and Neck</td><td>September 2011</td><td>November 2021</td><td>Phase 3</td><td>Head and Neck Squamous Cell Carcinoma</td><td>	Drug</td><td>AFATINIB</td><td>Carcinoma;Carcinoma, Squamous Cell;Squamous Cell Carcinoma of Head and Neck</td></tr>
</table>

The script also outputs a summary table that is intended for downstream use, ``clinical_trials_by_phase.tsv``:

<table>
<tr><td>Disease</td><td>MeSH id</td><td>medication</td><td>Phase</td><td>Earliest start year</td><td>Latest start year</td><td>NCIT</td></tr>
<tr><td>Mastocytosis</td><td>D008415</td><td>imatinib</td><td>Phase 2</td><td>2004</td><td>2004</td><td>NCT00171912;NCT00109707
<tr><td>Mastocytosis</td><td>D008415</td><td>imatinib</td><td>Phase 4</td><td>2011</td><td>2011</td><td>NCT01297777</td></tr>
</table>

``Earliest start date`` and ``Latest start date`` are used to show the earliest and latest year when a study started (they are of course the
same if there was only one study or if all studies started in the same year).

The script downloads files and stores them in a (newly created) directory called ``ct_data``. This directory can be
deleted after running the script. Finally, the script outputs a logfile ``yactp-stats.txt`` with some details of the parsing results.